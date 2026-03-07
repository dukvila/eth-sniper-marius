import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V27.2 FUTURE FOCUS", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("💰 ETH SNIPER V27.2 | FUTURE FOCUS")

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
    momentum = (kainos[-1] - kainos[-8]) / 8 
    nuokrypis = statistics.stdev(kainos[-20:])
    volat = (nuokrypis / dabartine) * 100
    
    # Prognozės generavimas (8 valandos į priekį)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 9)]
    p_fut = []
    for h in range(1, 9):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.7))
        p_fut.append(val)

    # --- PELNO ANALIZĖ ---
    max_p_fut = max(p_fut)
    pelnas = max_p_fut - dabartine
    piko_idx = p_fut.index(max_p_fut)
    piko_laikas = l_fut[piko_idx]
    
    if momentum > 0.1 and pelnas > 1.5:
        statusas, spalva = "🚀 PIRKTI", "#28a745"
        detales = f"Tikėtinas pelnas: +{pelnas:.2f}€ | Parduoti iki {piko_laikas.strftime('%H:%M')}"
    elif momentum < -0.1:
        statusas, spalva = "📉 LAUKTI / PARDUOTI", "#dc3545"
        detales = "Trendas neigiamas. Kaina artėja prie žemesnio taško."
    else:
        statusas, spalva = "⌛ NEUTRALU", "#ffc107"
        detales = f"Pelnas per mažas (+{pelnas:.2f}€). Rizika didesnė už grąžą."

    st.markdown(f'<div style="background-color:{spalva};padding:20px;border-radius:10px;text-align:center;color:white;"><h1>{statusas}</h1><h3>{detales}</h3></div>', unsafe_allow_html=True)

    # --- GRAFIKAS (Fokusas į ateitį) ---
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Rodome tik paskutines 15 istorinių žvakių (apie 4 valandas), kad atlaisvintume vietos prognozei
    ax.plot(laikai[-15:], kainos[-15:], color='#2962ff', linewidth=3, alpha=0.6, label="Istorija (4h)")
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, label="Prognozė (8h)")
    
    # Praeities pikai (tik matomoje dalyje)
    for i in range(len(kainos[-15:])-2):
        idx = i + (len(kainos) - 15)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=9, ha='center')

    # Tikslo žymėjimas (Ryškus taškas ateityje)
    ax.scatter(piko_laikas, max_p_fut, color='white', s=150, zorder=10, edgecolors='#00ffcc')
    ax.text(piko_laikas, max_p_fut + 1.2, f"TIKSLAS: {max_p_fut:.1f}€\n({piko_laikas.strftime('%H:%M')})", 
            color='white', fontweight='bold', ha='center', fontsize=10)

    # Laiko ašies formatavimas
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.xticks(color='gray', fontsize=9)
    plt.yticks(color='gray', fontsize=9)
    ax.grid(True, alpha=0.03, color='white')
    st.pyplot(fig)

    # Skaitikliai
    c1, c2, c3 = st.columns(3)
    c1.metric("DABARTINĖ KAINA", f"{dabartine:.2f} €")
    c2.metric("POTENCIALUS PELNAS", f"+{pelnas:.2f} €")
    c3.info(f"🕒 LT Laikas: {(datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')}")
else:
    st.warning("🔄 Kraunami šviežiausi duomenys...")
