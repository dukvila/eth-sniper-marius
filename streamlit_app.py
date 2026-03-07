import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V65 REVERSAL-ANALYST", layout="wide")
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
    
    # --- SUDĖTINGI SKAČIAVIMAI (Day-Trading Logic) ---
    vidurkis = statistics.mean(kainos[-40:])
    nuokrypis = statistics.stdev(kainos[-40:])
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    
    # Rinkos pervargimas (Overbought/Oversold)
    # Jei kaina per toli nuo vidurkio - prognozuojame grįžimą
    z_score = (dabartine - vidurkis) / nuokrypis if nuokrypis > 0 else 0
    
    # Ateities prognozė (10 žingsnių po 30 min)
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    
    for h in range(1, 11):
        # Grįžimo jėga (traukia kainą prie vidurkio)
        pull_to_mean = (vidurkis - dabartine) * 0.1 * h
        # Momentum jėga (slopstanti laike)
        decaying_momentum = momentum * h * (0.9 ** h)
        # Rezultatas: Momentum vs Mean Reversion
        fut_p = dabartine + decaying_momentum + pull_to_mean
        p_fut.append(fut_p)

    # --- STATUSO PANĖLĖ ---
    if abs(z_score) > 2:
        status = "⚠️ PERTEMPTA - LAUKIAMAS APSISUKIMAS"
        color = "#ff8c00"
    elif momentum > 0:
        status = "📈 SVEIKAS AUGIMAS"
        color = "#28a745"
    else:
        status = "📉 MATOMAS KRITIMAS"
        color = "#dc3545"

    st.markdown(f"""
    <div style="background-color:{color}; padding:15px; border-radius:12px; text-align:center; color:white;">
        <h2 style="margin:0;">{status}</h2>
        <p style="margin:5px;">Kaina: {dabartine:.2f}€ | Nuokrypis nuo vidurkio: {z_score:+.2f} | Momentum: {momentum:+.2f}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Minimali istorija (30 min)
    ax.plot(laikai[-3:], kainos[-3:], color='gray', linewidth=2, alpha=0.4)
    
    # ATEITIES PROGNOZĖ (Reversas / Tęstinumas)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', label="Matematinė prognozė")
    
    # Pagalbinės ribos (Resistance / Support)
    ax.axhline(vidurkis + (nuokrypis * 2), color='#dc3545', linestyle='--', alpha=0.3, label="Max viršūnė")
    ax.axhline(vidurkis - (nuokrypis * 2), color='#28a745', linestyle='--', alpha=0.3, label="Max dugnas")
    
    # Kainos ant prognozės
    for i in [2, 5, 9]:
        ax.text(l_fut[i], p_fut[i] + 1.5, f"{p_fut[i]:.1f}€", color='white', ha='center', fontweight='bold')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.05, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    
    st.pyplot(fig)
    
    st.info("Ši prognozė skaičiuoja galimą kainos 'pervargimą' ir grįžimą į realią vertę.")
else:
    st.warning("🔄 Analizuojami rinkos pasipriešinimo lygiai...")
