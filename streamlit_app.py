import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V68 VOLUME-SNIPER", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            if 'result' in res:
                d = res['result']['XETHZEUR'][-160:]
                laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
                kainos = [float(z[4]) for z in d]
                highs = [float(z[2]) for z in d]
                lows = [float(z[3]) for z in d]
                volumes = [float(z[6]) for z in d] # APIMTYS
                return laikai, kainos, highs, lows, volumes
            return [], [], [], [], []
    except:
        return [], [], [], [], []

laikai, kainos, highs, lows, volumes = get_market_data()

if kainos and len(kainos) > 60:
    dabartine = kainos[-1]
    vid_volume = statistics.mean(volumes[-20:])
    dabartinis_vol = volumes[-1]
    
    # --- SKAIČIAVIMAI ---
    smaz = pd.Series(kainos).rolling(window=20).mean().iloc[-1]
    stdz = pd.Series(kainos).rolling(window=20).std().iloc[-1]
    virsus = smaz + (stdz * 2.1)
    apacia = smaz - (stdz * 2.1)
    
    # RSI
    delta = pd.Series(kainos).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] > 0 else 100
    
    # APIMČIŲ ANALIZĖ (Volume Force)
    vol_force = dabartinis_vol / vid_volume if vid_volume > 0 else 1
    
    # PROGNOZĖ (Agresyvi su Volume įtaka)
    momentum = (kainos[-1] - kainos[-8]) / 2.0
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Jei apimtys didelės, trendas stipresnis
        stiprumas = 1.0 + (vol_force * 0.1) if vol_force > 1 else 0.8
        fut_val = dabartine + (momentum * h * stiprumas) + (stdz * 0.15 * np.sin(h))
        p_fut.append(fut_val)
    
    prog_max = max(p_fut)
    
    # --- SNIPER SIGNALAS ---
    if dabartine >= virsus or rsi > 75:
        signalas = "🔴 PARDUOTI (STAB
