import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V47 HARVARD ANALYTICS", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            if 'result' in res:
                d = res['result']['XETHZEUR'][-160:]
                # Lietuvos laikas (+2 valandos)
                laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
                kainos = [float(z[4]) for z in d]
                return laikai, kainos
            return [], []
    except Exception:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 40:
    dabartine = kainos[-1]
    
    # --- MOKSLINĖ ANALITIKA (Harvard Method Inspired) ---
    pokytis_24h = ((kainos[-1] - kainos[0]) / kainos[0]) * 100
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    volatilumas = statistics.stdev(kainos[-40:])
    
    # Kaufman Efficiency Ratio (triukšmo matavimas)
    direction = abs(kainos[-1] - kainos[-10])
    volatility = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    efficiency = direction / volatility if volatility != 0 else 0

    # --- CRYPTO CRITICAL INFORMACIJA ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("DABARTINĖ KAINA", f"{dabartine:.2f} €", f"{pokytis_24h:.2f}%")
    with c2:
        status = "STABILU" if efficiency > 0.6 else "CHAOSAS"
        st.metric("RINKOS EFEKTYVUMAS", status, f"{efficiency:.2f} ER")
    with c3:
        st.metric("MOMENTUMAS", f"{momentum:.2f} €/h")

    # --- TIKSLI PROGNOZĖ ---
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        # Algoritmas derinantis momentumą ir rinkos efektyvumą
        triuksmas = (volatilumas * (1 - efficiency) * np.sin(h))
        trendas = momentum * h * efficiency
        val = dabartine + trendas + triuksmas
        p_fut.append(val)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(15, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # 4 valandų istorija
    pradzia_4h = laikai[-1] - timedelta(hours=4)
    r_idx = next((i for i, t in enumerate(laikai) if t >= pradzia_4h), 0)
    ax.plot(laikai[r_idx:], kainos[r_idx:], color='#1a46ba', linewidth=4, alpha=0.9, label="Istorija")
    
    # Istorinės sumos
    for i in range(r_idx + 1, len(kainos) - 1):
        if (kainos[i] > kainos[i-1] and kainos[i] > kainos[i+1]) or (kainos[i] < kainos[i-1] and kainos[i] < kainos[i+1]):
            if abs(kainos[i] - dabartine) > volatilumas: # Rodome tik reikšmingus
                ax.text(laikai[i], kainos[i]+0.3, f"{kainos[i]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # Aštri mokslinė prognozė
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=6, label="Mokslinė prognozė")
    
    # Sumos ant prognozės kampų
    for i in range(len(p_fut)):
        if i > 0 and i < len(p_fut)-1:
            if (p_fut[i] > p_fut[i-1] and p_fut[i] > p_fut[i+1]) or (p_fut[i] < p_fut[i-1] and p_fut[i] < p_fut[i+1]):
                color = 'white' if p_fut[i] > p_fut[i-1] else '#ff4b4b'
                ax.text(l_fut[i], p_fut[i] + (1.2 if p_fut[i] > p_fut[i-1] else -2.5), 
                        f"{p_fut[i]:.1f}€", color=color, fontweight='bold', ha='center')

    # Geltonas taškas (Ramybės indikatorius)
    if abs(momentum) < 0.2:
        ax.scatter(laikai[-1], kainos[-1], color='#ffeb3b', s=300, zorder=50, edgecolors='white')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.08, color='white', linestyle='--')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    st.pyplot(fig)

    st.success("✅ Rinkos duomenys analizuojami realiu laiku. Prognozė atnaujinama kas 60s.")
else:
    st.warning("🔄 Kraunama Harvard Analytics duomenų bazė...")
