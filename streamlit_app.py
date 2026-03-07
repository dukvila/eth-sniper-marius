import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Pagrindinė konfigūracija
st.set_page_config(page_title="ETH V45 ULTRA SNIPER", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            if 'result' in res:
                # Paimame pakankamai duomenų 4 valandų istorijai
                d = res['result']['XETHZEUR'][-150:]
                # Lietuvos laikas (+2 valandos)
                laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
                kainos = [float(z[4]) for z in d]
                return laikai, kainos
            return [], []
    except Exception:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 20:
    dabartine = kainos[-1]
    # Day-trading momentumas
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    nuokrypis = statistics.stdev(kainos[-40:])
    
    # --- AŠTRIAUSIA PROGNOZĖ (ZIG-ZAG) ---
    l_fut = [laikai[-1] + timedelta(minutes=20*h) for h in range(1, 13)]
    p_fut = []
    for h in range(1, 13):
        # Agresyvūs lūžiai dienos prekybai
        kryptis = 2.4 if h % 4 == 0 else -1.9 if h % 2 == 0 else 0.7
        val = dabartine + (momentum * h) + (kryptis * nuokrypis * 1.3)
        p_fut.append(val)

    # --- GRAFIKO BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(15, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # 1. 4 VALANDŲ ISTORIJA
    pradzia_4h = laikai[-1] - timedelta(hours=4)
    r_idx = next(i for i, t in enumerate(laikai) if t >= pradzia_4h)
    
    ax.plot(laikai[r_idx:], kainos[r_idx:], color='#1a46ba', linewidth=4, alpha=0.9)
    
    # Istorinės kainos virš smaigalių (Melsvos)
    for i in range(r_idx + 1, len(kainos) - 1):
        if kainos[i] > kainos[i-1] and kainos[i] > kainos[i+1]:
            ax.text(laikai[i], kainos[i]+0.4, f"{kainos[i]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # 2. ATEITIES PROGNOZĖ (Neoninė kampuota linija)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=6)
    
    # 3. KAINOS ANT KIEKVIENO PROGNOZĖS KAMPORIO
    for i in range(len(p_fut)):
        # Žymime lūžius (pikus/dugnus)
        if i > 0 and i < len(p_fut)-1:
            is_pikas = p_fut[i] > p_fut[i-1] and p_fut[i] > p_fut[i+1]
            is_dugnas
