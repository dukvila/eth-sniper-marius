import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta

# Konfigūracija
st.set_page_config(page_title="ETH SNIPER V18 | KRAKEN", layout="wide")
st.title("🎯 ETH SNIPER V18 | KRAKEN RADAR")
from streamlit_autorefresh import st_autorefresh
# Atnaujina kas 5 minutes (300 000 milisekundžių)
st_autorefresh(interval=300000, key="datarefresh")
def get_market_data():
    sentiment = 1.0
    # 1. Nuotaikos (CryptoPanic)
    try:
        cp_url = "https://cryptopanic.com/api/v1/posts/?auth_token=cb3edbdd0bef024331f39e3d16bbafd8cf61208f&currencies=ETH&filter=hot"
        with urllib.request.urlopen(cp_url, timeout=10) as r:
            data = json.loads(r.read().decode())
            posts = data.get('results', [])
            pos = sum((p.get('votes', {}).get('positive', 0) + p.get('votes', {}).get('bullish', 0)) for p in posts[:12])
            neg = sum((p.get('votes', {}).get('negative', 0) + p.get('votes', {}).get('bearish', 0)) for p in posts[:12])
            sentiment = 1.0 + (pos - neg) / 180
    except:
        sentiment = 1.0
    
    # 2. Kainos iš KRAKEN (Vietoj Binance)
    try:
        # Kraken API naudoja XETHZEUR porą
        k_url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=60"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(k_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            # Kraken duomenų struktūra: [time, open, high, low, close, vwap, volume, count]
            d = res['result']['XETHZEUR']
            # Paimame paskutinius 100 įrašų
            d = d[-100:]
            laikai = [datetime.fromtimestamp(z[0]) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos, sentiment
    except Exception as e:
        return [], [], 1.0

if st.button('PALEISTI RADARĄ (KRAKEN)'):
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

        # Braižymas (V18 stilius)
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
        ax.plot(l_at, p_at, color="#005A5A", linewidth=3, label="V18 PROGNOZĖ")
        
        # Žymėjimas
        for t in range(1, 24):
            is_max = p_at[t] > p_at[t-1] and p_at[t] > p_at[t+1]
            is_min = p_at[t] < p_at[t-1] and p_at[t] < p_at[t+1]
            if is_max or is_min:
                prob = min(98.8, max(55.0, (84 + (sentiment-1)*55) + math.cos(t)*4))
                ax.scatter(l_at[t], p_at[t], color="#D32F2F" if is_max else "#F57C00", s=100, edgecolors='black', zorder=5)
                ax.text(l_at[t], p_at[t] + 8, f"{p_at[t]:.1f}€\n{prob:.1f}%", ha='center', fontsize=9, fontweight='bold')

        ax.grid(True, alpha=0.1)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        st.info(f"📊 Šaltinis: KRAKEN | Nuotaika {sentiment:.2f}")
        st.pyplot(fig)
        st.metric("Dabartinė ETH kaina (Kraken)", f"{dabartine:.2f} €")
    else:
        st.error("Klaida: Net ir Kraken neatsako. Patikrinkite savo API raktus arba interneto ryšį.")
