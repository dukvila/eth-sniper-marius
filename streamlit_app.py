import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V63 REAL-TREND", layout="wide")
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
    
    # --- REAL-TREND ANALIZĖ ---
    # Skaičiuojame tikrąjį momentumą (kiek kaina keitėsi vidutiniškai per valandą)
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    volatilumas = statistics.stdev(kainos[-40:])
    
    # Rinkos efektyvumas (ER) - jei ER mažas, prognozė bus atsargi
    direction = abs(kainos[-1] - kainos[-10])
    vol_sum = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    er = direction / vol_sum if vol_sum > 0 else 0
    
    # Tikimybės balas
    tikimybe = (er * 75) + (15 if momentum > 0 else 5)
    tikimybe = max(min(tikimybe, 99), 1)

    # --- BŪSENOS INDIKATORIUS ---
    if tikimybe > 60 and momentum > 0.5:
        busena = "📈 REALI PROGNOZĖ: AUGIMAS"
        bg_color = "#28a745"
    elif momentum < -0.5 and tikimybe > 50:
        busena = "📉 REALI PROGNOZĖ: KRITIMAS"
        bg_color = "#dc3545"
    else:
        busena = "🔄 RINKA STOVI (NEAIŠKU)"
        bg_color = "#6c757d"

    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:20px; border-radius:15px; text-align:center; color:white; font-family:sans-serif;">
        <h1 style="margin:0; font-size:30px;">{busena}</h1>
        <p style="margin:10px; font-size:18px;">
            Dabartinė kaina: {dabartine:.2f}€ | Pagreitis: {momentum:.2f}€/h | Stabilumas (ER): {er:.2f}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- DINAMINĖ PROGNOZĖ (Be dirbtinių tikslų) ---
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Tikrasis trendas + nedidelis triukšmas, pagrįstas volatilumu
        triuksmas = (volatilumas * 0.4 * (1 if h % 2 == 0 else -1)) * (1 - er)
        p_fut.append(dabartine + (momentum * h) + triuksmas)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija (Mėlyna)
    ax.plot(laikai[-60:], kainos[-60:], color='#1a46ba', linewidth=4, alpha=0.9, label="Istorinė kaina")
    
    # Tikroji prognozė (Cyan)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, linestyle='--', marker='o', markersize=5, label="Reali prognozė")
    
    # Vertės ant prognozės taškų
    for i in [2, 5, 9]: # Rodyti tik svarbius taškus (po 1.5h, 3h, 5h)
        ax.text(l_fut[i], p_fut[i] + 1.2, f"{p_fut[i]:.1f}€", color='white', fontweight='bold', ha='center')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.1, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    
    st.pyplot(fig)
    
    st.info(f"Prognozė atnaujinta realiu laiku: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("🔄 Jungiamasi prie rinkos duomenų...")
