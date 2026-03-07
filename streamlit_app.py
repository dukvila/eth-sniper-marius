import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V32 MARKET PULSE", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V32 | MARKET PULSE")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-100:]
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except: return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    vidurkis_24h = statistics.mean(kainos[-96:]) # Paskutinės 24 valandos
    momentum = (kainos[-1] - kainos[-8]) / 2 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # ŠVELNESNĖ PROGNOZĖ (Mix su 24h vidurkiu)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        # Prognozė labiau traukiama link 24h vidurkio, kad nebūtų per staigi
        val = (dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.8)) + vidurkis_24h) / 2
        p_fut.append(val)

    max_p = max(p_fut)
    piko_idx = p_fut.index(max_p)
    pelnas_eur = max_p - dabartine

    # --- STATUSO SKYDELIS (Sušvelnintas) ---
    if momentum > 0.4 and pelnas_eur > 2.0:
        msg, col = "📈 PALANKI TENDENCIJA", "#28a745"
        info = "Rinkos jėga teigiama, prognozuojamas nuosaikus kilimas."
    elif momentum < -0.4:
        msg, col = "📉 RIZIKINGA ZONA", "#dc3545"
        info = "Fiksuojamas pardavėjų pranašumas."
    else:
        msg, col = "🏊‍♂️ RAMI RINKA", "#00d9ff"
        info = "Dalyvių aktyvumas žemas, kaina plaukia vietoje."

    st.markdown(f'<div style="background-color:{col};padding:15px;border-radius:10px;text-align:center;color:white;"><h2>{msg}</h2><p>{info}</p></div>', unsafe_allow_html=True)

    # --- GRAFIKAS ---
    fig, (ax, ax_vol) = plt.subplots(2, 1, figsize=(14, 9), facecolor='black', gridspec_kw={'height_ratios': [3, 1]})
    ax.set_facecolor('#0a0a0a')
    ax_vol.set_facecolor('#0a0a0a')
    
    # Pagrindinis grafikas
    ax.plot(laikai[-20:], kainos[-20:], color='#2962ff', linewidth=3, alpha=0.5)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, label='Švelni prognozė')
    
    # Smaigalių fiksavimas (V28)
    for i in range(len(kainos[-20:])-2):
        idx = i + (len(kainos) - 20)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # Aktyvus indikatorius
    marker = '^' if momentum > 0.15 else 'v' if momentum < -0.15 else 'o'
    m_col = '#00ff00' if momentum > 0.15 else '#ff0000' if momentum < -0.15 else '#00d9ff'
    ax.scatter(laikai[-1], kainos[-1], marker=marker, color=m_col, s=200, zorder=30)

    # --- RINKOS DALYVIŲ AKTYVUMAS (Žalia/Raudona) ---
    pirkejai = max(0.1, momentum * 10) if momentum > 0 else 0.5
    pardavejai = abs(momentum * 10) if momentum < 0 else 0.5
    
    ax_vol.barh(['Pardavėjai', 'Pirkėjai'], [pardavejai, pirkejai], color=['#ff4b4b', '#28a745'])
    ax_vol.set_title("RINKOS DALYVIŲ AKTYVUMAS (PULSAS)", color='white', fontsize=10)
    ax_vol.tick_params(axis='x', colors='gray')
    ax_vol.tick_params(axis='y', colors='white')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.03, color='white')
    plt.tight_layout()
    st.pyplot(fig)

    # Skaitikliai
    c1, c2, c3 = st.columns(3)
    c1.metric("KAINA", f"{dabartine:.2f} €")
    c2.metric("24H VIDURKIS", f"{vidurkis_24h:.2f} €")
    c3.info(f"🕒 Atnaujinta: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.error("Nepavyko prisijungti.")
