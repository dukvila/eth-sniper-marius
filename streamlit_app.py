import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V62 DAY-TRADER PRO", layout="wide")
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
    except:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 50:
    dabartine = kainos[-1]
    
    # --- PRO ANALIZĖS VARIKLIS ---
    # 1. Momentum (3 valandų greitis)
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    
    # 2. RSI tipo indikatorius (Supaprastintas day-tradingui)
    kilimai = sum(max(0, kainos[i] - kainos[i-1]) for i in range(-14, 0))
    kritimai = sum(max(0, kainos[i-1] - kainos[i]) for i in range(-14, 0))
    rsi = 100 - (100 / (1 + (kilimai / kritimai))) if kritimai > 0 else 100
    
    # 3. Efficiency Ratio (ER) - Triukšmo filtras
    direction = abs(kainos[-1] - kainos[-10])
    vol_sum = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    er = direction / vol_sum if vol_sum > 0 else 0
    
    # Saugumo tikimybė
    tikimybe = (er * 70) + (rsi * 0.3)
    tikimybe = max(min(tikimybe, 99), 1)

    # --- DAY-TRADING SIGNALŲ LOGIKA ---
    # Griežtas filtras: Pirkti tik jei RSI ne per aukštas ir ER geras
    if tikimybe > 60 and momentum > 0 and rsi < 70:
        busena = "🚀 VERTA PIRKTI (STIPRUS SIGNALAS)"
        bg_color = "#28a745"
    elif rsi > 75:
        busena = "⚠️ PERPIRKTA (GALIMAS KRITIMAS)"
        bg_color = "#ff8c00"
    elif tikimybe < 35 or er < 0.2:
        busena = "🛑 PAVOJUS - CHAOTIŠKA RINKA"
        bg_color = "#dc3545"
    else:
        busena = "🧐 STEBĖTI (LAUKTI GERESNIO MOMENTO)"
        bg_color = "#6c757d"

    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:20px; border-radius:15px; text-align:center; color:white; font-family:sans-serif;">
        <h1 style="margin:0; font-size:32px;">{busena}</h1>
        <p style="margin:10px; font-size:20px;">
            Kaina: {dabartine:.2f}€ | RSI: {rsi:.1f} | Tikimybė: {tikimybe:.1f}%
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- PROGNOZĖ ---
    volatilumas = statistics.stdev(kainos[-40:])
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        posukis = (volatilumas * 0.8 * (1 if h % 2 == 0 else -1))
        trendas = momentum * h * (er + 0.1)
        p_fut.append(dabartine + trendas + posukis)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija (4 valandos)
    ist_nuo = laikai[-1] - timedelta(hours=4)
    idx = next((i for i, t in enumerate(laikai) if t >= ist_nuo), 0)
    ax.plot(laikai[idx:], kainos[idx:], color='#1a46ba', linewidth=4, alpha=0.8)
    
    # Prognozė (Zig-Zag)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=4)
    
    # Kainos ant lūžių
    for i in range(len(p_fut)):
        if i > 0 and i < len(p_fut)-1:
            is_peak = p_fut[i] > p_fut[i-1] and p_fut[i] > p_fut[i+1]
            is_bottom = p_fut[i] < p_fut[i-1] and p_fut[i] < p_fut[i+1]
            if is_peak or is_bottom:
                c = 'white' if is_peak else '#ff4b4b'
                ax.text(l_fut[i], p_fut[i] + (1.5 if is_peak else -2.8), f"{p_fut[i]:.1f}€", 
                        color=c, fontweight='bold', ha='center', fontsize=11)

    # Tikslas
    ax.scatter(l_fut[-1], p_fut[-1], color='#00ff00', s=550, zorder=60, edgecolors='white', linewidth=2)
    ax.text(l_fut[-1], p_fut[-1] + 3.8, f"TIKSLAS: {p_fut[-1]:.1f}", color='#00ff00', fontweight='bold', ha='center', fontsize=12)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.1, color='white', linestyle='--')
    plt.xticks(color='gray', fontsize=12)
    plt.yticks(color='gray', fontsize=12)
    st.pyplot(fig)
    
    st.info(f"Paskutinis atnaujinimas: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("🔄 Analizuojami day-trading duomenys...")
