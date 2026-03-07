import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V69 FINAL-FIX", layout="wide")
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
                volumes = [float(z[6]) for z in d]
                return laikai, kainos, highs, lows, volumes
            return [], [], [], [], []
    except:
        return [], [], [], [], []

laikai, kainos, highs, lows, volumes = get_market_data()

if kainos and len(kainos) > 60:
    dabartine = kainos[-1]
    vid_vol = statistics.mean(volumes[-20:])
    vol_force = volumes[-1] / vid_vol if vid_vol > 0 else 1
    
    # --- SKAIČIAVIMAI (Sutvarkyta logika) ---
    smaz = pd.Series(kainos).rolling(window=20).mean().iloc[-1]
    stdz = pd.Series(kainos).rolling(window=20).std().iloc[-1]
    virsus = smaz + (stdz * 2.1)
    apacia = smaz - (stdz * 2.1)
    
    # RSI skaičiavimas
    delta = pd.Series(kainos).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] > 0 else 100
    
    # Agresyvi prognozė
    momentum = (kainos[-1] - kainos[-8]) / 2.0
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        fut_val = dabartine + (momentum * h * 0.9) + (stdz * 0.1 * np.sin(h))
        p_fut.append(fut_val)
    
    prog_max = max(p_fut)

    # --- SIGNALAI (Ištaisytos SyntaxErrors) ---
    if dabartine >= virsus or rsi > 76:
        signalas = "🔴 PARDUOTI (RIBA PASIEKTA)"
        spalva = "#dc3545"
        txt = f"Kaina virš koridoriaus ({virsus:.1f}€). Rizika didelė."
    elif (dabartine <= apacia or rsi < 36) and vol_force > 1.1:
        signalas = "🟢 PIRKTI (ATSPIRKIMAS)"
        spalva = "#28a745"
        txt = "Dugnas su geromis apimtimis. Geras įėjimo taškas."
    elif momentum > 0.4 and vol_force > 1.0:
        signalas = "🚀 TĘSTI PIRKIMĄ (STIPRUS TRENDAS)"
        spalva = "#007bff"
        txt = f"Trendas stiprus. Tikslas: {prog_max:.1f}€"
    else:
        signalas = "🟡 STEBĖTI SIGNALĄ"
        spalva = "#ff8c00"
        txt = "Rinka be aiškios krypties viduryje koridoriaus."

    st.markdown(f"""
    <div
