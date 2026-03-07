import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V64 FUTURE-FOCUS", layout="wide")
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
    except:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 50:
    dabartine = kainos[-1]
    
    # --- SKAIČIAVIMAI ---
    # Momentum (3h pagreitis)
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    volatilumas = statistics.stdev(kainos[-40:])
    
    # Efficiency Ratio (ER)
    direction = abs(kainos[-1] - kainos[-10])
    vol_sum = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    er = direction / vol_sum if vol_sum > 0 else 0
    
    # Prognozės generavimas (Ateities 5 valandos)
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    p_high = []
    p_low = []
    
    for h in range(1, 11):
        triuksmas = (volatilumas * 0.5 * (1 if h % 2 == 0 else -1)) * (1 - er)
        base_p = dabartine + (momentum * h) + triuksmas
        p_fut.append(base_p)
        # Saugumo koridorius (95% tikimybė pagal volatilumą)
        p_high.append(base_p + (volatilumas * 0.8))
        p_low.append(base_p - (volatilumas * 0.8))

    # --- BŪSENOS PANĖLĖ ---
    color = "#28a745" if momentum > 0 else "#dc3545"
    st.markdown(f"""
    <div style="background-color:{color}; padding:15px; border-radius:12px; text-align:center; color:white;">
        <h2 style="margin:0;">🚀 ATEITIES PROGNOZĖ (5 VALANDOS)</h2>
        <p style="margin:5px; font-size:18px;">Momentum: {momentum:+.2f}€/h | ER: {er:.2f} | Dabartinė: {dabartine:.2f}€</p>
    </div>
    """, unsafe_allow_html=True)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Minimali istorija (tik 30 min)
    ax.plot(laikai[-3:], kainos[-3:], color='gray', linewidth=2, alpha=0.5, label="Praeitis")
    
    # ATEITIES KORIDORIUS (Šešėlis)
    ax.fill_between(l_fut, p_low, p_high, color='#00ffcc', alpha=0.1, label="Rizikos zona")
    
    # PAGRINDINĖ PROGNOZĖS LINIJA
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=6, label="Ateities trendas")
    
    # KAINŲ ETIKETĖS
    for i in range(len(p_fut)):
        if i % 2 == 0: # Rodyti kas antrą, kad nebūtų šiukšlyno
            ax.text(l_fut[i], p_fut[i] + 1.5, f"{p_fut[i]:.1f}€", color='white', fontweight='bold', ha='center', fontsize=10)

    # Tikslas (paskutinis taškas)
    ax.scatter(l_fut[-1], p_fut[-1], color='white', s=100, zorder=10)
    ax.text(l_fut[-1], p_fut[-1] + 3, "GALUTINĖ", color='#00ffcc', fontweight='bold', ha='center')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.05, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    
    st.pyplot(fig)
    
    st.info("Ši prognozė remiasi gryna matematika: dabartiniu pagreičiu ir volatilumu.")
else:
    st.warning("🔄 Skaičiuojama ateities prognozė...")
