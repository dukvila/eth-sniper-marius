import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V49 HARVARD CALIBRATED", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            if 'result' in res:
                d = res['result']['XETHZEUR'][-160:]
                laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
                kainos = [float(z[4]) for z in d]
                return laikai, kainos
            return [], []
    except Exception: return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 40:
    dabartine = kainos[-1]
    
    # --- HARVARD ANALYTICS ---
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    volatilumas = statistics.stdev(kainos[-40:])
    
    # Kaufman Efficiency Ratio (Rinkos stabilumo matas)
    direction = abs(kainos[-1] - kainos[-10])
    vol_sum = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    efficiency = direction / vol_sum if vol_sum != 0 else 0

    # Crypto Critical Info
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("DABARTINĖ KAINA", f"{dabartine:.2f} €")
    with c2: st.metric("RINKA", "STABILU" if efficiency > 0.6 else "CHAOSAS")
    with c3: st.metric("MOMENTUMAS", f"{momentum:.2f} €/h")

    # --- PROGNOZĖ (Kalibruotas Zig-Zag) ---
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Švelnesni, bet aiškūs prekybos posūkiai
        posukis = (volatilumas * 0.8 * (1 if h % 2 == 0 else -1))
        trendas = momentum * h * (efficiency + 0.2)
        val = dabartine + trendas + posukis
        p_fut.append(val)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # 4 valandų istorija
    pradzia_4h = laikai[-1] - timedelta(hours=4)
    r_idx = next((i for i, t in enumerate(laikai) if t >= pradzia_4h), 0)
    ax.plot(laikai[r_idx:], kainos[r_idx:], color='#1a46ba', linewidth=4)
    
    # Neoninė prognozės linija
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=3)
    
    # --- SUMOS ANT VISŲ LŪŽIŲ ---
    for i in range(len(p_fut)):
        is_pikas = (i > 0 and i < len(p_fut)-1 and p_fut[i] > p_fut[i-1] and p_fut[i] > p_fut[i+1])
        is_dugnas = (i > 0 and i < len(p_fut)-1 and p_fut[i] < p_fut[i-1] and p_fut[i] < p_fut[i+1])
        
        if is_pikas or is_dugnas or i == len(p_fut)-1:
            color = 'white' if p_fut[i] > dabartine else '#ff4b4b'
            offset = 0.8 if p_fut[i] > dabartine else -1.8
            ax.text(l_fut[i], p_fut[i] + offset, f"{p_fut[i]:.1f}€", 
                    color=color, fontweight='bold', ha='center', fontsize=10)

    # --- ŽALIAS TIKSLO APSKRITIMAS (Prognozės gale) ---
    ax.scatter(l_fut[-1], p_fut[-1], color='#00ff00', s=350, zorder=60, edgecolors='white')
    ax.text(l_fut[-1], p_fut[-1] + 2.0, "TIKSLAS", color='#00ff00', fontweight='bold', ha='center')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.1, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    st.pyplot(fig)
else:
    st.warning("Analizuojami Harvard moksliniai duomenys...")
