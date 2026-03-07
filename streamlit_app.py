import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V70 ULTRA-SNIPER", layout="wide")
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
                vols = [float(z[6]) for z in d]
                return laikai, kainos, highs, lows, vols
            return [], [], [], [], []
    except:
        return [], [], [], [], []

laikai, kainos, highs, lows, vols = get_market_data()

if kainos and len(kainos) > 60:
    dabartine = kainos[-1]
    
    # --- MATEMATINIS MODELIS (Ištaisytas) ---
    smaz = pd.Series(kainos).rolling(window=20).mean().iloc[-1]
    stdz = pd.Series(kainos).rolling(window=20).std().iloc[-1]
    virsus = smaz + (stdz * 2.1)
    apacia = smaz - (stdz * 2.1)
    
    # RSI skaičiavimas
    delta = pd.Series(kainos).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] > 0 else 100
    
    # Prognozė
    momentum = (kainos[-1] - kainos[-8]) / 2.0
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        p_fut.append(dabartine + (momentum * h * 0.85) + (stdz * 0.1 * np.sin(h)))

    # --- AGRESYVŪS SIGNALAI ---
    if dabartine >= virsus or rsi > 76:
        signalas = "🔴 PARDUOTI (STABDYMAS)"
        spalva = "#dc3545"
        zinute = f"Kaina pasiekė viršūnę ({virsus:.1f}€). Rizikinga laikyti."
    elif dabartine <= apacia or rsi < 36:
        signalas = "🟢 PIRKTI (ATSPIRKIMAS)"
        spalva = "#28a745"
        zinute = "Dugnas pasiektas. Galimas kilimas aukštyn."
    elif momentum > 0.4:
        signalas = "🚀 TĘSTI PIRKIMĄ"
        spalva = "#007bff"
        zinute = "Trendas stiprus, apimtys patvirtina judėjimą."
    else:
        signalas = "🟡 STEBĖTI TRENDĄ"
        spalva = "#ff8c00"
        zinute = "Rinka be aiškios krypties."

    st.markdown(f"""
    <div style="background-color:{spalva}; padding:25px; border-radius:15px; text-align:center; color:white; border: 4px solid white;">
        <h1 style="margin:0;">{signalas}</h1>
        <p style="font-size:20px; margin:10px;">{zinute}</p>
        <p style="font-size:16px;">Kaina: {dabartine:.2f}€ | RSI: {rsi:.1f}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- GRAFIKAS (Sutvarkytas braižymas) ---
    fig, ax1 = plt.subplots(figsize=(12, 7), facecolor='black')
    ax1.set_facecolor('#0a0a0a')
    
    # Praeitis ir Prognozė
    ax1.plot(laikai[-10:], kainos[-10:], color='white', alpha=0.3)
    ax1.plot(l_fut, p_fut, color='#00ffcc', linewidth=6, marker='o', markersize=8)
    
    # Tavo 1717€ riba
    ax1.axhline(1717.8, color='red', linestyle='--', alpha=0.4, label="Resistance")
    
    for i in [2, 5, 9]:
        ax1.text(l_fut[i], p_fut[i] + 1.2, f"{p_fut[i]:.1f}€", color='cyan', fontweight='bold', ha='center')

    ax1.
