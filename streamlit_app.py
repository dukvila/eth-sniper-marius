import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija (V31 stilius)
st.set_page_config(page_title="ETH V33 RECOV", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V33 | RECOV")

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
    
    # Prognozės generavimas (V31 aštrumas)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.8))
        p_fut.append(val)

    max_p = max(p_fut)
    piko_idx = p_fut.index(max_p)
    pelnas_eur = max_p - dabartine

    # --- ATSTATYTAS VERTA PIRKTI SKYDELIS ---
    if momentum > 0.4 and pelnas_eur > 3.0:
        st.markdown(f'<div style="background-color:#28a745;padding:20px;border-radius:15px;text-align:center;color:white;"><h1>🚀 VERTA PIRKTI</h1><h3>Prognozuojamas pikas: {max_p:.1f}€ (+{pelnas_eur:.2f}€)</h3></div>', unsafe_allow_html=True)
    elif momentum < -0.4:
        st.markdown(f'<div style="background-color:#dc3545;padding:20px;border-radius:15px;text-align:center;color:white;"><h1>🪂 RIZIKA / PARDUOTI</h1><h3>Kaina krenta, momentumas neigiamas.</h3></div>', unsafe_allow_html=True)
    else:
        st.info("🏊‍♂️ LAUKTI (Neutralu) - Rinkos judėjimas plokščias.")

    # --- GRAFIKAS (V31 + Pulsas) ---
    fig, (ax, ax_vol) = plt.subplots(2, 1, figsize=(14, 9), facecolor='black', gridspec_kw={'height_ratios': [3, 1]})
    ax.set_facecolor('#0a0a0a')
    ax_vol.set_facecolor('#0a0a0a')
    
    # Istorija ir
