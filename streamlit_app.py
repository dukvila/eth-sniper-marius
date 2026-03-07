import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V38 SHARP WAVE", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V38 | SHARP WAVE")

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
    except Exception as e:
        return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    momentum = (kainos[-1] - kainos[-8]) / 2 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # --- AŠTRI PROGNOZĖ (Lūžtantys kampai) ---
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Naudojame aštresnį zigzagą vietoj švelnios bangos
        svyravimas = (nuokrypis * 1.8) if h % 3 == 0 else -(nuokrypis * 1.2) if h % 2 == 0 else (nuokrypis * 0.5)
        val = dabartine + (momentum * h) + svyravimas
        p_fut.append(val)

    max_p = max(p_fut)
    min_p_fut = min(p_fut)
    piko_idx = p_fut.index(max_p)
    dugno_idx = p_fut.index(min_p_fut)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija (Tamsiai mėlyna, aštri)
    ax.plot(laikai[-30:], kainos[-30:], color='#1a46ba', linewidth=4, alpha=0.7)
    
    # Istoriniai smaigaliai (Melsvi skaičiai)
    for i in range(len(kainos[-30:])-2):
        idx = i + (len
