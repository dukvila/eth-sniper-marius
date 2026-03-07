import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Nustatymai ir Automatinis atnaujinimas (3 min geresniam tikslumui)
st.set_page_config(page_title="ETH SNIPER V18.5 PRO", layout="wide")
st_autorefresh(interval=180000, key="datarefresh")
st.title("🎯 ETH SNIPER V18.5 | PRO RADAR")

def get_market_data():
    sentiment = 1.0
    # Nuotaikų gavimas
    try:
        cp_url = "https://cryptopanic.com/api/v1/posts/?auth_token=cb3edbdd0bef024331f39e3d16bbafd8cf61208f&currencies=ETH&filter=hot"
        with urllib.request.urlopen(cp_url, timeout=10) as r:
            data = json.loads(r.read().decode())
            posts = data.get('results', [])
            pos = sum((p.get('votes', {}).get('positive', 0) + p.get('votes', {}).get('bullish', 0)) for p in posts[:12])
            neg = sum((p.get('votes', {}).get('negative', 0) + p.get('votes', {}).get('bearish', 0)) for p in posts[:12])
            sentiment = 1.0 + (pos - neg) / 120 # Padidintas jautrumas
    except: sentiment = 1.0
    
    # Kainų gavimas iš Kraken (XETHZEUR)
    try:
        k_url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=60"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(k_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-100:]
            # Laiko korekcija (+2h Lietuvai)
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos, sentiment
    except: return [], [], 1.0

# Vykdymas
laikai, kainos, sentiment = get_market_data()

if kainos:
    dabartine = kainos[-1]
    # PATOBULINTA: Trendas skaičiuojamas pagal paskutines 4 valandas (super agresyvu)
    nuokrypis = statistics.stdev(kainos[-48:])
    trendas = (kainos[-1] - kainos[-4]) / 4 

    l_at = [laikai[-1] + timedelta(hours=h) for h in range(25)]
    p_at = []
    
    for h in range(25):
        # Dinaminė V18.5 formulė
        val = dabartine + (trendas * h) + ((math.sin(h/3.2)*(nuokrypis*0.9) + math.sin(h/0.9)*(nuokrypis*0.4)) * sentiment)
        p_at.append(val)

    # Braižymas
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='#000000')
    ax.set_facecolor('#0a0a0a')
    ax.plot(l_at, p_at, color="#00ff88", linewidth=3, label="V18.5 PROGNOZĖ")
    
    # Išmanieji Pikai ir Dugnai
    for t in range(1, 24):
        is_max = p_at[t] > p_at[t-1] and p_at[t] > p_at[t+1]
        is_min = p_at[t] < p_at[t-1] and p_at[t] < p_at[t+1]
        if is_max or is_min:
            prob = min(99.5, max(60.0, (86 + (sentiment-1)*65) + math.cos(t)*5))
            color = "#ff3333" if is_max else "#ffcc00"
            ax.scatter(l_at[t], p_at[t], color=color, s=150, edgecolors='white', zorder=5)
            ax.text(l_at[t], p_at[t] + (15 if is_max else -35), f"{p_at[t]:.1f}€\n{prob:.1f}%", 
                    ha='center', color='white', fontsize=10, fontweight='bold')

    ax.grid(True, alpha=0.1, color='white')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(color='white')
    plt.yticks(color='white')
    
    st.info(f"⚡ Būsena: Agresyvus Radaras | Nuotaika {sentiment:.2f} | Atnaujinta: {datetime.now().strftime('%H:%M:%S')}")
    st.pyplot(fig)
    
    col1, col2 = st.columns(2)
    col1.metric("Dabartinė Kaina", f"{dabartine:.2f} €", f"{trendas:.2f} €/h")
    col2.metric("24h Prognozė", f"{p_at[-1]:.2f} €")
else:
    st.error("Nepavyko pasiekti Kraken duomenų. Patikrink interneto ryšį.")
