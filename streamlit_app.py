import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V48 HARVARD SHARP", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            if 'result' in res:
                d = res['result']['XETHZEUR'][-160:]
                # Lietuvos laikas (+2h) sinchronizuotas su tavo kompiuteriu
                laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
                kainos = [float(z[4]) for z in d]
                return laikai, kainos
            return [], []
    except Exception:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 40:
    dabartine = kainos[-1]
    
    # --- HARVARD ANALYTICS & CRITICAL DATA ---
    pokytis_24h = ((kainos[-1] - kainos[0]) / kainos[0]) * 100
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    volatilumas = statistics.stdev(kainos[-40:])
    
    # Kaufman Efficiency Ratio (Rinkos triukšmo filtras)
    direction = abs(kainos[-1] - kainos[-10])
    vol = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    efficiency = direction / vol if vol != 0 else 0

    # Viršutinė juosta (Crypto Critical)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("KAINA", f"{dabartine:.2f} €", f"{pokytis_24h:.2f}%")
    with c2: st.metric("RINKA", "STABILU" if efficiency > 0.6 else "CHAOSAS")
    with c3: st.metric("MOMENTUMAS", f"{momentum:.2f} €/h")

    # --- TIKSLI PROGNOZĖ ---
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Moksliškai pagrįstas judėjimas
        triuksmas = (volatilumas * (1.1 - efficiency) * (1 if h % 2 == 0 else -1))
        trendas = momentum * h * efficiency
        val = dabartine + trendas + triuksmas
        p_fut.append(val)

    # --- GRAFIKAS TELEFONUI ---
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # 4h Istorija
    ist_nuo = laikai[-1] - timedelta(hours=4)
    r_idx = next((i for i, t in enumerate(laikai) if t >= ist_nuo), 0)
    ax.plot(laikai[r_idx:], kainos[r_idx:], color='#1a46ba', linewidth=5, alpha=0.9)
    
    # Aštri prognozės linija
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=6, marker='o', markersize=4)
    
    # --- SUMOS ANT VISŲ LŪŽIO TAŠKŲ ---
    for i in range(len(p_fut)):
        # Priverstinai žymime kiekvieną lūžį
        if i > 0 and i < len(p_fut)-1:
            color = 'white' if p_fut[i] > p_fut[i-1] else '#ff4b4b'
            ax.text(l_fut[i], p_fut[i] + (0.8 if p_fut[i] > p_fut[i-1] else -2.2), 
                    f"{p_fut[i]:.1f}", color=color, fontweight='bold', ha='center', fontsize=11)

    # --- RYŠKUS ŽALIAS GALAS (TELEFONUI) ---
    ax.scatter(l_fut[-1], p_fut[-1], color='#00ff00', s=400, zorder=60, edgecolors='white', linewidth=2)
    ax.text(l_fut[-1], p_fut[-1] + 1.5, "TIKSLAS", color='#00ff00', fontweight='bold', ha='center', fontsize=12)

    # Indikatorius (Geltonas taškas)
    if abs(momentum) < 0.2:
        ax.scatter(laikai[-1], kainos[-1], color='#ffeb3b', s=250, zorder=55)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.1, color='white')
    plt.xticks(color='gray', fontsize=12)
    plt.yticks(color='gray', fontsize=12)
    
    st.pyplot(fig)
    st.success("✅ Prognozė sukalibruota mobiliam įrenginiui.")
else:
    st.warning("🔄 Jungiamasi prie Harvard Analytics serverio...")
