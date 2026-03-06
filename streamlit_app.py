import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta

# Nustatymai
st.set_page_config(page_title="ETH SNIPER V18", layout="wide")
st.title("🚀 ETH SNIPER V18 | PRO RADAR")

def get_market_data():
    sentiment = 1.0
    try:
        # CryptoPanic Nuotaikos
        cp_url = "https://cryptopanic.com/api/v1/posts/?auth_token=cb3edbdd0bef024331f39e3d16bbafd8cf61208f&currencies=ETH&filter=hot"
        with urllib.request.urlopen(cp_url, timeout=5) as r:
            data = json.loads(r.read().decode())
            posts = data.get('results', [])
            pos = sum((p.get('votes', {}).get('positive', 0) + p.get('votes', {}).get('bullish', 0)) for p in posts[:12])
            neg = sum((p.get('votes', {}).get('negative', 0) + p.get('votes', {}).get('bearish', 0)) for p in posts[:12])
            sentiment = 1.0 + (pos - neg) / 180
    except:
        sentiment = 1.0
    
    try:
        # Binance Kainos
        b_url = "https://api1.binance.com/api/v3/klines?symbol=ETHEUR&interval=1h&limit=100"
        with urllib.request.urlopen(b_url, timeout=5) as r:
            d = json.loads(r.read().decode())
            return [datetime.fromtimestamp(z[0]/1000) for z in d], [float(z[4]) for z in d], sentiment
    except:
        return [], [], 1.0

if st.button('PALEISTI RADARĄ'):
    laikai, kainos, sentiment = get_market_data()
    
    if kainos:
        # V18 PROGNOZĖS MATEMATIKA
        dabartine = kainos[-1]
        nuokrypis = statistics.stdev(kainos[-48:])
        trendas = (kainos[-1] - kainos[-18]) / 18 

        l_at = [datetime.now() + timedelta(hours=h) for h in range(25)]
        p_at = []
        for h in range(25):
            val = dabartine + (trendas * h) + ((math.sin(h/3.8)*(nuokrypis*0.8) + math.sin(h/1.2)*(nuokrypis*0.3)) * sentiment)
            p_at.append(val)

        # BRAIŽYMAS
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(l_at, p_at, color="#005A5A", linewidth=3)
        
        # Pikų žymėjimas
        for t in range(1, 24):
            if (p_at[t] > p_at[t-1] and p_at[t] > p_at[t+1]) or (p_at[t] < p_at[t-1] and p_at[t] < p_at[t+1]):
                prob = min(98.8, max(55.0, (84 + (sentiment-1)*55) + math.cos(t)*4))
                ax.scatter(l_at[t], p_at[t], color="#D32F2F" if p_at[t] > p_at[t-1] else "#F57C00", s=100, edgecolors='black')
                ax.text(l_at[t], p_at[t] + 10, f"{p_at[t]:.1f}€\n{prob:.1f}%", ha='center', fontsize=9, fontweight='bold')

        ax.grid(True, alpha=0.15)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        st.pyplot(fig)
        st.metric("Dabartinė ETH kaina", f"{dabartine:.2f} €")
    else:
        st.error("Nepavyko gauti duomenų iš biržos. Bandykite dar kartą.")
