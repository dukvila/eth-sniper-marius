import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V35 WAVE PRECISION", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V35 | WAVE PRECISION")

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
    
    # --- ŠOKINĖJANTI PROGNOZĖ (WAVE MODEL) ---
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Sukuriame sudėtinę bangą: trendas + pagrindinė banga + smulkus triukšmas
        banga = (math.sin(h/1.2) * (nuokrypis * 1.5)) + (math.cos(h/0.8) * (nuokrypis * 0.5))
        val = dabartine + (momentum * h) + banga
        p_fut.append(val)

    max_p = max(p_fut)
    min_p_fut = min(p_fut)
    piko_idx = p_fut.index(max_p)
    dugno_idx = p_fut.index(min_p_fut)
    pelnas_eur = max_p - dabartine

    # --- SPRENDIMŲ SKYDELIS ---
    if momentum > 0.3 and pelnas_eur > 3.0:
        st.markdown(f'<div style="background-color:#28a745;padding:20px;border-radius:15px;text-align:center;color:white;"><h1>🚀 VERTA PIRKTI</h1><h3>Pikas: {max_p:.1f}€ | Numatomas atšokimas: {min_p_fut:.1f}€</h3></div>', unsafe_allow_html=True)
    elif momentum < -0.3:
        st.markdown(f'<div style="background-color:#dc3545;padding:20px;border-radius:15px;text-align:center;color:white;"><h1>🪂 RIZIKA / PARDUOTI</h1></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background-color:#ffeb3b;padding:15px;border-radius:10px;text-align:center;color:black;font-weight:bold;">🟡 RAMI RINKA - Stebėkite geltoną tašką.</div>', unsafe_allow_html=True)

    # --- GRAFIKAS ---
    fig, (ax, ax_vol) = plt.subplots(2, 1, figsize=(14, 9), facecolor='black', gridspec_kw={'height_ratios': [3, 1]})
    ax.set_facecolor('#0a0a0a')
    ax_vol.set_facecolor('#0a0a0a')
    
    # Istorinis judėjimas
    ax.plot(laikai[-20:], kainos[-20:], color='#2962ff', linewidth=3, alpha=0.5)
    # Banguojanti prognozė
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, alpha=0.9)
    
    # Istoriniai smaigaliai (Melsvi)
    for i in range(len(kainos[-20:])-2):
        idx = i + (len(kainos) - 20)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # --- DINAMINIAI INDIKATORIAI ---
    if momentum > 0.15:
        ax.
