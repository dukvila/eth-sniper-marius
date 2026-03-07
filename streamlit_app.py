import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V42 TRUE TIME", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        # Naudojame Kraken API
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-100:]
            # SINCHRONIZACIJA: Pridedame 2 valandas, kad atitiktų Lietuvos laiką
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except:
        return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    # Skaičiuojame momentumą pagal paskutinius duomenis
    momentum = (kainos[-1] - kainos[-10]) / 2.5 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # --- AŠTRI ZIGZAG PROGNOZĖ ---
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        # Sukuriame aštrius lūžius (kaip image_34975f.jpg)
        zigzag = (nuokrypis * 2.2) if h % 3 == 0 else -(nuokrypis * 1.5) if h % 2 == 0 else (nuokrypis * 0.8)
        val = dabartine + (momentum * h) + zigzag
        p_fut.append(val)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(15, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija (Mėlyna aštri linija)
    ax.plot(laikai[-40:], kainos[-40:], color='#1a46ba', linewidth=4, alpha=0.9)
    
    # Istorinės sumos virš smaigalių
    for i in range(len(kainos[-40:])-2):
        idx = i + (len(kainos) - 40)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=9, ha='center')

    # Aštri neoninė prognozė (Žydra)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=6)
    
    # Sumų žymėjimas ant prognozės kampų
    max_p = max(p_fut)
    min_p_fut = min(p_fut)
    piko_idx = p_fut.index(max_p)
    dugno_idx = p_fut.index(min_p_fut)
    
    ax.text(l_fut[piko_idx], max_p + 1.5, f"{max_p:.1f}€", color='white', fontweight='bold', ha='center', fontsize=12)
    ax.text(l_fut[dugno_idx], min_p_fut - 3.0, f"{min_p_fut:.1f}€", color='#ff4b4b', fontweight='bold', ha='center', fontsize=12)

    # --- INDIKATORIUS GALE ---
    if momentum > 0.2:
        ax.scatter(laikai[-1], kainos[-1], marker='^', color='#00ff00', s=350, zorder=30)
    elif momentum < -0.2:
        ax.scatter(laikai[-1], kainos[-1], marker='v', color='#ff0000', s=350, zorder=30)
    else:
        ax.scatter(laikai[-
