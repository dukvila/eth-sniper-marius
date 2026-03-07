import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V52 PROBABILITY SNIPER", layout="wide")
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
    except: return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 50:
    dabartine = kainos[-1]
    
    # --- HARVARD PROBABILITY ENGINE ---
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    volatilumas = statistics.stdev(kainos[-40:])
    
    # Efficiency Ratio (Rinkos triukšmo filtras)
    direction = abs(kainos[-1] - kainos[-10])
    vol_sum = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    er = direction / vol_sum if vol_sum > 0 else 0
    tikimybe = (er * 100) + (5 if momentum > 0 else -5)

    # --- CRYPTO CRITICAL INFORMACIJA ---
    color = "#28a745" if momentum > 0 else "#dc3545"
    st.markdown(f"""
    <div style="background-color:{color}; padding:15px; border-radius:10px; text-align:center; color:white;">
        <h2 style="margin:0;">🚀 {'VERTA PIRKTI' if momentum > 0 else 'LAUKITE KOREKCIJOS'}</h2>
        <p style="margin:5px; font-size:18px;">Pikas: {(dabartine + volatilumas):.1f}€ | Tikimybė: {max(min(tikimybe, 99), 1):.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

    # --- PROGNOZĖ ---
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Bangavimas priklauso nuo rinkos efektyvumo (er)
        posukis = (volatilumas * 0.7 * (1 if h % 2 == 0 else -1))
        trendas = momentum * h * (er + 0.1)
        p_fut.append(dabartine + trendas + posukis)

    # --- GRAFIKAS TELEFONUI ---
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # 4 valandų istorija
    ist_nuo = laikai[-1] - timedelta(hours=4)
    idx = next((i for i, t in enumerate(laikai) if t >= ist_nuo), 0)
    ax.plot(laikai[idx:], kainos[idx:], color='#1a46ba', linewidth=4, alpha=0.8)
    
    # Tikimybinė prognozė
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=3)
    
    # SUMOS ANT VISŲ LŪŽIŲ
    for i in range(len(p_fut)):
        if i > 0 and i < len(p_fut)-1:
            is_peak = p_fut[i] > p_fut[i-1] and p_fut[i] > p_fut[i+1]
            is_bottom = p_fut[i] < p_fut[i-1] and p_fut[i] < p_fut[i+1]
            if is_peak or is_bottom:
                txt_color = 'white' if is_peak else '#ff4b4b'
                offset = 1.2 if is_peak else -2.5
                ax.text(l_fut[i], p_fut[i] + offset, f"{p_fut[i]:.1f}€", 
                        color=txt_color, fontweight='bold', ha='center', fontsize=1
