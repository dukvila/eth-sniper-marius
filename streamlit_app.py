import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V41 REAL-TIME SHARP", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-100:]
            # Sutvarkome laiką į Lietuvos (+2 valandos nuo UTC)
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except:
        return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    momentum = (kainos[-1] - kainos[-8]) / 2 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # --- AŠTRI PROGNOZĖ (Kampai) ---
    l_fut = [laikai[-1] + timedelta(minutes=15*h) for h in range(1, 12)]
    p_fut = []
    for h in range(1, 12):
        # Sukuriame aštrius zigzagus
        kryptis = 1.8 if h % 4 == 0 else -1.4 if h % 2 == 0 else 0.4
        val = dabartine + (momentum * h) + (kryptis * nuokrypis)
        p_fut.append(val)

    max_p = max(p_fut)
    min_p_fut = min(p_fut)
    piko_idx = p_fut.index(max_p)
    dugno_idx = p_fut.index(min_p_fut)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija (Aštri mėlyna linija)
    ax.plot(laikai[-30:], kainos[-30:], color='#1a46ba', linewidth=4, alpha=0.8)
    
    # Istoriniai smaigaliai (Surašome sumas kaip tavo nuotraukose)
    for i in range(len(kainos[-30:])-2):
        idx = i + (len(kainos) - 30)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.4, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=9, ha='center')

    # Neoninė kampuota prognozė
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=6)
    
    # Sumos ant prognozės taškų
    ax.text(l_fut[piko_idx], max_p + 1.2, f"{max_p:.1f}€", color='white', fontweight='bold', ha='center')
    ax.text(l_fut[dugno_idx], min_p_fut - 2.8, f"{min_p_fut:.1f}€", color='#ff4b4b', fontweight='bold', ha='center')

    # --- INDIKATORIUS (Tavo prašytas geltonas taškas) ---
    if momentum > 0.15:
        ax.scatter(laikai[-1], kainos[-1], marker='^', color='#00ff00', s=300, zorder=30)
    elif momentum < -0.15:
        ax.scatter(laikai[-1], kainos[-1], marker='v', color='#ff0000', s=300, zorder=30)
    else:
        ax.scatter(laikai[-1], kainos[-1], marker='o', color='#ffeb3b', s=250, zorder=30)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.05, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    st.pyplot(fig)

    # Tikras laikas apačioje
    st.write(f"🕒 Dabartinis laikas: **{datetime.now().strftime('%H:%M:%S')}** | Kaina: **{dabartine:.2f} €**")
else:
    st.error("Nepavyko atnaujinti duomenų.")
