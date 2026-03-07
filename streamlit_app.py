import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija ir Automatinis atnaujinimas (kas 2 min)
st.set_page_config(page_title="ETH SNIPER V20 PRO", layout="wide")
st_autorefresh(interval=120000, key="datarefresh")
st.title("🎯 ETH SNIPER V20 | AUTO-LEARNING RADAR")

def get_market_data():
    sentiment = 1.0
    try:
        # Nuotaikos iš CryptoPanic
        cp_url = "https://cryptopanic.com/api/v1/posts/?auth_token=cb3edbdd0bef024331f39e3d16bbafd8cf61208f&currencies=ETH&filter=hot"
        with urllib.request.urlopen(cp_url, timeout=10) as r:
            data = json.loads(r.read().decode())
            posts = data.get('results', [])
            pos = sum((p.get('votes', {}).get('positive', 0) + p.get('votes', {}).get('bullish', 0)) for p in posts[:12])
            neg = sum((p.get('votes', {}).get('negative', 0) + p.get('votes', {}).get('bearish', 0)) for p in posts[:12])
            sentiment = 1.0 + (pos - neg) / 120
    except: sentiment = 1.0
    
    try:
        # Kainos iš Kraken (15 min intervalas geresniam tikslumui)
        k_url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(k_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-80:] 
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos, sentiment
    except: return [], [], 1.0

laikai, kainos, sentiment = get_market_data()

if kainos:
    dabartine = kainos[-1]
    
    # --- V20 SAVIKONTROLĖS LOGIKA ---
    # Tikriname paskutinių 4 žvakių (1 valandos) realų nuokrypį
    realus_pokytis = kainos[-1] - kainos[-4]
    
    # Apskaičiuojame bazinį trendą ir pridedame "stabdį", jei rinka lūžta žemyn
    nuokrypis = statistics.stdev(kainos[-40:])
    trendas = (kainos[-1] - kainos[-8]) / 8
    
    # Jei kaina krenta, o trendas dar rodo kilimą - priverstinai koreguojame
    if realus_pokytis < 0 and trendas > 0:
        trendas = realus_pokytis / 4 # Priverčiame prognozę nulinkti žemyn
        stilius = "⚠️ AGRESYVUS KRITIMAS"
    elif realus_pokytis > 0:
        stilius = "🚀 STABILUS KILIMAS"
    else:
        stilius = "📉 TRENDO SEKIMAS"

    # Prognozės generavimas (24 valandos į priekį)
    l_at = [laikai[-1] + timedelta(hours=h) for h in range(25)]
    p_at = []
    for h in range(25):
        # Dinaminė formulė su savikontrolės koeficientu
        val = dabartine + (trendas * h) + ((math.sin(h/3.5)*(nuokrypis*0.8) + math.sin(h/1.2)*(nuokrypis*0.3)) * sentiment)
        p_at.append(val)

    # Braižymas (PRO tamsus stilius)
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='black')
    ax.set_facecolor('#0e1117')
    ax.plot(l_at, p_at, color="#00ffcc" if trendas > 0 else "#ff0055", linewidth=3, label="V20 PROGNOZĖ")
    
    # Pikai ir tikimybės
    for t in range(1, 24):
        is_max = p_at[t] > p_at[t-1] and p_at[t] > p_at[t+1]
        is_min = p_at[t] < p_at[t-1] and p_at[t] < p_at[t+1]
        if is_max or is_min:
            prob = min(99.1, max(52.0, (82 + (sentiment-1)*60) + (realus_pokytis/2)))
            ax.scatter(l_at[t], p_at[t], color="#ff4b4b" if is_max else "#faca2b", s=100, zorder=5)
            ax.text(l_at[t], p_at[t] + (8 if is_max else -20), f"{p_at[t]:.1f}€\n{prob:.1f}%", 
                    ha='center', color='white', fontsize=9, fontweight='bold')

    ax.grid(True, alpha=0.05, color='white')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    
    st.success(f"Būsena: {stilius} | Nuotaika: {sentiment:.2f}")
    st.pyplot(fig)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Dabartinė Kaina", f"{dabartine:.2f} €")
    c2.metric("Valandos Pokytis", f"{realus_pokytis:.2f} €", delta_color="normal")
    c3.metric("Nuotaikos Indeksas", f"{sentiment:.2f}")
else:
    st.warning("Jungiamasi prie Kraken biržos... Patikrinkite ryšį.")
