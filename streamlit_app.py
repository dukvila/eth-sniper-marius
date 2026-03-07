import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH SNIPER V19 PRO", layout="wide")
st_autorefresh(interval=120000, key="datarefresh") # Atnaujinimas kas 2 min

def get_market_data():
    try:
        # Kraken API - paimame šviežiausius duomenis
        k_url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15" # 15 min tikslumas
        req = urllib.request.Request(k_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-60:] # Paskutinė valanda su puse
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except: return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    # PATOBULINTA: Skaičiuojame ne tik trendą, bet ir jo greitį
    diffs = np.diff(kainos)
    pagreitis = np.mean(diffs[-5:]) # Paskutinių 5 žvakių kryptis
    
    nuokrypis = statistics.stdev(kainos[-20:])
    
    l_at = [laikai[-1] + timedelta(minutes=15*h) for h in range(20)]
    p_at = []
    
    for h in range(20):
        # Dinaminė prognozė: jei pagreitis neigiamas, sinusas spaudžiamas žemyn
        base = dabartine + (pagreitis * h * 1.5)
        vibracija = (math.sin(h/2.5) * nuokrypis * 0.7)
        p_at.append(base + vibracija)

    # Braižymas
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    ax.plot(l_at, p_at, color="#ff0055" if pagreitis < 0 else "#00ff88", linewidth=3)
    
    # Žymėjimas
    for t in range(1, 19):
        if (p_at[t] > p_at[t-1] and p_at[t] > p_at[t+1]) or (p_at[t] < p_at[t-1] and p_at[t] < p_at[t+1]):
            color = "#ff3333" if p_at[t] > p_at[t-1] else "#ffcc00"
            ax.scatter(l_at[t], p_at[t], color=color, s=100)
            ax.text(l_at[t], p_at[t]+2, f"{p_at[t]:.1f}€", color='white', fontsize=8, ha='center')

    ax.grid(alpha=0.1)
    st.pyplot(fig)
    st.metric("Dabartinė Kaina", f"{dabartine:.2f} €", f"{pagreitis:.2f} (Pagreitis)")
else:
    st.error("Laukiama duomenų...")
