import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V46 MASTER TRADER", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            if 'result' in res:
                d = res['result']['XETHZEUR'][-160:]
                # Lietuvos laiko pataisa (+2 valandos)
                laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
                kainos = [float(z[4]) for z in d]
                return laikai, kainos
            return [], []
    except Exception:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 30:
    dabartine = kainos[-1]
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    nuokrypis = statistics.stdev(kainos[-40:])
    
    # --- PROGNOZĖS SKAIČIAVIMAS (Aštrus Zig-Zag) ---
    l_fut = [laikai[-1] + timedelta(minutes=20*h) for h in range(1, 13)]
    p_fut = []
    for h in range(1, 13):
        kryptis = 2.5 if h % 4 == 0 else -2.0 if h % 2 == 0 else 0.8
        val = dabartine + (momentum * h) + (kryptis * nuokrypis * 1.4)
        p_fut.append(val)

    # --- GRAFIKO BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(15, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Rodome 4 valandas ISTORIJOS
    pradzia_4h = laikai[-1] - timedelta(hours=4)
    r_idx = next((i for i, t in enumerate(laikai) if t >= pradzia_4h), 0)
    
    # Istorinė linija
    ax.plot(laikai[r_idx:], kainos[r_idx:], color='#1a46ba', linewidth=4, alpha=0.9)
    
    # Istorinių smaigalių sumos
    for i in range(r_idx + 1, len(kainos) - 1):
        if kainos[i] > kainos[i-1] and kainos[i] > kainos[i+1]:
            ax.text(laikai[i], kainos[i]+0.4, f"{kainos[i]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # Aštri prognozė
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=6)
    
    # Sumos ant prognozės kampų
    for i in range(len(p_fut)):
        if i > 0 and i < len(p_fut)-1:
            is_pikas = p_fut[i] > p_fut[i-1] and p_fut[i] > p_fut[i+1]
            is_dugnas = p_fut[i] < p_fut[i-1] and p_fut[i] < p_fut[i+1]
            if is_pikas or is_dugnas:
                color = 'white' if is_pikas else '#ff4b4b'
                offset = 1.0 if is_pikas else -2.8
                ax.text(l_fut[i], p_fut[i] + offset, f"{p_fut[i]:.1f}€", color=color, fontweight='bold', ha='center')

    # Indikatorius (Geltonas taškas ramybei)
    if abs(momentum) < 0.15:
        ax.scatter(laikai[-1], kainos[-1], marker='o', color='#ffeb3b', s=300, zorder=50)
    elif momentum > 0.15:
        ax.scatter(laikai[-1], kainos[-1], marker='^', color='#00ff00', s=450, zorder=50)
    else:
        ax.scatter(laikai[-1], kainos[-1], marker='v', color='#ff0000', s=450, zorder=50)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.08, color='white', linestyle='--')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    st.pyplot(fig)

    # Informacija apačioje
    st.markdown(f"""
    <div style="background-color:#0e1117; padding:15px; border-radius:10px; border:1px solid #1a46ba;">
        <span style="color:white; font-size:18px;">🕒 Realus laikas: <b>{datetime.now().strftime('%H:%M:%S')}</b></span>
        <span style="color:#00ffcc; font-size:18px; margin-left:25px;">💰 Kaina: <b>{dabartine:.2f} €</b></span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("🔄 Jungiamasi prie biržos duomenų...")
