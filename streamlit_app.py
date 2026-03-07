import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V37 PURE WAVE", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V37 | PURE WAVE")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-100:]
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except: return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    momentum = (kainos[-1] - kainos[-8]) / 2 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # --- BANGUOJANTI PROGNOZĖ ---
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Sukuriame svyravimą pagal tavo istorijos braižą
        banga = (math.sin(h/1.2) * (nuokrypis * 1.4)) + (math.cos(h/0.9) * (nuokrypis * 0.5))
        val = dabartine + (momentum * h) + banga
        p_fut.append(val)

    max_p = max(p_fut)
    min_p_fut = min(p_fut)
    piko_idx = p_fut.index(max_p)
    dugno_idx = p_fut.index(min_p_fut)

    # --- PAGRINDINIS GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorijos linija ir istoriniai smaigaliai (melsvi)
    ax.plot(laikai[-25:], kainos[-25:], color='#2962ff', linewidth=3, alpha=0.5)
    for i in range(len(kainos[-25:])-2):
        idx = i + (len(kainos) - 25)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # Neoninė prognozės kreivė
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, alpha=0.9)
    
    # --- SUMŲ ŽYMĖJIMAS ANT PROGNOZĖS ---
    # Piko taškas
    ax.scatter(l_fut[piko_idx], max_p, color='white', s=100, zorder=20)
    ax.text(l_fut[piko_idx], max_p + 1.2, f"{max_p:.1f}€", color='white', fontweight='bold', ha='center', fontsize=10)
    
    # Atšokimo (dugno) taškas
    if dugno_idx != piko_idx:
        ax.scatter(l_fut[dugno_idx], min_p_fut, color='#ff4b4b', s=80, zorder=20)
        ax.text(l_fut[dugno_idx], min_p_fut - 2.5, f"{min_p_fut:.1f}€", color='#ff4b4b', fontweight='bold', ha='center', fontsize=10)

    # --- INDIKATORIAI (Tavo prašytas geltonas taškas) ---
    if momentum > 0.15:
        ax.scatter(laikai[-1], kainos[-1], marker='^', color='#00ff00', s=250, zorder=30)
    elif momentum < -0.15:
        ax.scatter(laikai[-1], kainos[-1], marker='v', color='#ff0000', s=250, zorder=30)
    else:
        ax.scatter(laikai[-1], kainos[-1], marker='o', color='#ffeb3b', s=200, zorder=30) # Geltonas skritulys

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.03, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    st.pyplot(fig)

    # Skaitikliai apačioje (kad netrukdytų vaizdui)
    c1, c2, c3 = st.columns(3)
    c1.metric("DABARTINĖ", f"{dabartine:.2f} €")
    c2.metric("MOMENTUMAS", f"{momentum:.2f} €/h")
    c3.info(f"🕒 Atnaujinta: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.error("Nepavyko įkrauti grafiko.")
