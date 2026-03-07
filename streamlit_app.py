import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V31 ULTIMATE", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V31 | ULTIMATE SIGNAL")

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
    # Skaičiuojame tikslų momentumą (per paskutines 2 valandas)
    momentum = (kainos[-1] - kainos[-8]) / 2 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # Prognozės generavimas (8-9 valandos)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.8))
        p_fut.append(val)

    max_p = max(p_fut)
    piko_idx = p_fut.index(max_p)
    pelnas_eur = max_p - dabartine

    # --- SPRENDIMŲ ANALIZATORIUS ---
    if momentum > 0.4 and pelnas_eur > 3.0:
        msg, col = "🚀 VERTA PIRKTI", "#28a745"
        detales = f"Prognozuojamas pikas: {max_p:.1f}€ (+{pelnas_eur:.2f}€)"
    elif momentum < -0.4:
        msg, col = "🪂 RIZIKA / PARDUOTI", "#dc3545"
        detales = "Kaina krenta, prognozė neigiama."
    else:
        msg, col = "🏊‍♂️ LAUKTI (Neutralu)", "#00d9ff"
        detales = "Rinka neturi aiškios krypties."

    st.markdown(f'<div style="background-color:{col};padding:20px;border-radius:15px;text-align:center;color:white;"><h1>{msg}</h1><h3>{detales}</h3></div>', unsafe_allow_html=True)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija ir Prognozė
    ax.plot(laikai[-15:], kainos[-15:], color='#2962ff', linewidth=3, alpha=0.5)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5)
    
    # Smaigalių fiksavimas (Melsvi skaičiai)
    for i in range(len(kainos[-15:])-2):
        idx = i + (len(kainos) - 15)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')
        elif (kainos[idx] < kainos[idx-1] and kainos[idx] < kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]-1.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # Aktyvus indikatorius (trikampis)
    marker = '^' if momentum > 0.15 else 'v' if momentum < -0.15 else 'o'
    m_col = '#00ff00' if momentum > 0.15 else '#ff0000' if momentum < -0.15 else '#00d9ff'
    ax.scatter(laikai[-1], kainos[-1], marker=marker, color=m_col, s=250, zorder=30)

    # Tikslo fiksavimas
    ax.scatter(l_fut[piko_idx], max_p, color='white', s=120, zorder=20)
    ax.text(l_fut[piko_idx], max_p + 1.5, f"{max_p:.1f}€\n({l_fut[piko_idx].strftime('%H:%M')})", 
            color='white', fontweight='bold', ha='center', fontsize=9)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    ax.grid(True, alpha=0.03, color='white')
    st.pyplot(fig)

    # Skaitikliai
    c1, c2, c3 = st.columns(3)
    c1.metric("KAINA", f"{dabartine:.2f} €")
    c2.metric("MOMENTUMAS", f"{momentum:.2f} €/h")
    c3.info(f"🕒 Atnaujinta: {(datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')}")
else:
    st.error("Duomenų sinchronizacijos klaida.")
