import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta

# 1. Puslapio nustatymai
st.set_page_config(page_title="ETH SNIPER V18", layout="wide")
st.title("🎯 ETH SNIPER V18 | PRO RADAR")

# Tavo CryptoPanic raktas
CP_API_KEY = "cb3edbdd0bef024331f39e3d16bbafd8cf61208f"

def get_market_data():
    sentiment = 1.0
    try:
        url_n = f"https://cryptopanic.com/api/v1/posts/?auth_token={CP_API_KEY}&currencies=ETH&filter=hot"
        with urllib.request.urlopen(url_n, timeout=5) as r:
            posts = json.loads(r.read().decode()).get('results', [])
            pos = sum((p.get('votes', {}).get('positive', 0) + p.get('votes', {}).get('bullish', 0)) for p in posts[:12])
            neg = sum((p.get('votes', {}).get('negative', 0) + p.get('votes', {}).get('bearish', 0)) for p in posts[:12])
            sentiment = 1.0 + (pos - neg) / 180
    except: pass
    
    try:
        # Naudojame stabilų Binance API adresą
        url_b = "https://api1.binance.com/api/v3/klines?symbol=ETHEUR&interval=1h&limit=100"
        with urllib.request.urlopen(url_b, timeout=5) as r:
            d = json.loads(r.read().decode())
            return [datetime.fromtimestamp(z[0]/1000) for z in d], [float(z[4]) for z in d], sentiment
    except: return [], [], 1.0

# Vieno mygtuko paspaudimas telefone
if st.button('PALEISTI RADARĄ'):
    laikai, kainos, sentiment = get_market_data()
    
    if kainos:
        # Tavo V18 matematika
        dabartine = kainos[-1]
        nuokrypis = statistics.stdev(kainos[-48:])
        trendas = (kainos[-1] - kainos[-18]) / 18 

        l_at = [datetime.now() + timedelta(hours=h) for h in range(25)]
        p_at = []
        for h in range(25):
            val = dabartine + (trendas * h) + ((math.sin(h/3.8)*(nuokrypis*0.8) + math.sin(h/1.2)*(nuokrypis*0.3)) * sentiment)
            p_at.append(val)

        # Braižymas
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(l_at, p_at, color="#005A5A", linewidth=3, label="ETH PROGNOZĖ")
        ax.margins(y=0.2)

        # Taškų žymėjimas
        for t in range(1, 24):
            is_max = p_at[t] > p_at[t-1] and p_at[t] > p_at[t+1]
            is_min = p_at[t] < p_at[t-1] and p_at[t] < p_at[t+1]
            if is_max or is_min:
                prob = min(98.8, max(55.0, (84 + (sentiment-1)*55) + math.cos(t)*4))
                color = "#D32F2F" if is_max else "#F57C00"
                ax.scatter(l_at[t], p_at[t], color=color, s=100, edgecolors='black', zorder=5)
                
                # Tekstas virš taško
                y_offset = 10 if is_max else -25
                ax.text(l_at[t], p_at[t] + y_offset, f"{p_at[t]:.0f}€\n{prob:.1f}%", 
                        ha='center', fontsize=9, fontweight='bold')

        # Informacija
        st.info(f"📊 Nuotaika: {sentiment:.2f} | Atnaujinta: {datetime.now().strftime('%H:%M:%S')}")
        ax.grid(True, alpha=0.2)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        st.pyplot(fig)
        st.metric("Dabartinė kaina", f"{dabartine:.2f} €")
    else:
        st.error("Nepavyko gauti duomenų. Bandykite dar kartą.")
