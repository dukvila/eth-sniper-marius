import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija ir Automatinis atnaujinimas (kas 2 min)
st.set_page_config(page_title="ETH V25 PRECISION", layout="wide")
st_autorefresh(interval=120000, key="datarefresh")
st.title("🕒 ETH SNIPER V25 | PRECISION TIME")

def get_market_data():
    try:
        # Naudojame Kraken API su 15min intervalu
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-100:]
            # SINCHRONIZACIJA: Pridedame 2 valandas Lietuvos laikui
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except: return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    momentum = (kainos[-1] - kainos[-8]) / 8 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # Prognozės generavimas (8 valandos į priekį)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(9)]
    p_fut = []
    for h in range(9):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.7))
        p_fut.append(val)

    # --- PROFESIONALUS BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija (Mėlyna) ir Prognozė (Neoninė)
    ax.plot(laikai[-40:], kainos[-40:], color='#2962ff', linewidth=2, alpha=0.6, label="ISTORIJA")
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=4, label="V25 PROGNOZĖ")
    
    # Praeities pikai su skaičiais (kaip V23/V24)
    for i in range(len(kainos[-40:])-2):
        idx = i + (len(kainos) - 40)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+1, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')
        elif (kainos[idx] < kainos[idx-1] and kainos[idx] < kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]-3, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # --- LAIKO AŠIES FORMATAVIMAS (Svarbiausia dalis) ---
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=60)) # Valandos
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15)) #
