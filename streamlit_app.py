import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V58 QUANTUM PRO-GRAPH", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            if 'result' in res:
                d = res['result']['XETHZEUR'][-160:]
                # Lietuvos laikas (+2h)
                laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
                kainos = [float(z[4]) for z in d]
                return laikai, kainos
            return [], []
    except:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 50:
    dabartine = kainos[-1]
    
    # --- ANALIZĖS VARIKLIS ---
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    volatilumas = statistics.stdev(kainos[-40:])
    
    # Rinkos efektyvumas (ER)
    direction = abs(kainos[-1] - kainos[-10])
    vol_sum = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    er = direction / vol_sum if vol_sum > 0 else 0
    
    # Tikimybė (0-100%)
    tikimybe = (er * 80) + (15 if momentum > 0 else 5)
    tikimybe = max(min(tikimybe, 99), 1)

    # --- INFORMACINIS BLOKAS (Pataisyta logika) ---
    if tikimybe > 65 and momentum > 0:
        busena = "🚀 VERTA PIRKTI (SAUGU)"
        bg_color = "#28a745"
    elif momentum > 0:
        busena = "⚠️ KYLA, BET RIZIKINGA"
        bg_color = "#ff8c00"
    elif tikimybe < 40:
        busena = "🛑 PAVOJUS - CHAOSAS"
        bg_color = "#dc3545"
    else:
        busena = "🧐 STEBĖTI RINKĄ"
        bg_color = "#6c757d"

    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:20px; border-radius:15px; text-align:center; color:white; font-family:sans-serif;">
        <h1 style="margin:0;">{busena}</h1>
        <p style="margin:10px; font-size:18px;">Tikimybė: {tikimybe:.1f}% | Momentum: {momentum:.2f}€/h | ER: {er:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- PROGNOZĖS SKAIČIAVIMAS ---
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Ištaisyta: Dinaminis bangavimas
        posukis = (volatilumas * 0.75 * (1 if h % 2 == 0 else -1))
        trendas = momentum * h * (er + 0.1)
        p_fut.append(dabartine + trendas + posukis)

    # --- GRAFIKO BRAIŽYMAS (Ištaisyta ax.scatter ir ax.text) ---
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija
    ist_nuo = laikai[-1] - timedelta(hours=4)
    idx = next((i for i, t in enumerate(laikai) if t >= ist_nuo), 0)
    ax.plot(laikai[idx:], kainos[idx:], color='#1a46ba', linewidth=4, alpha=0.8)
    
    # Prognozės linija
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, marker='o', markersize=4)
    
    # SUMOS ANT VISŲ LŪŽIŲ (Ištaisyta NameError)
    for i in range(len(p_fut)):
        if i > 0 and i < len(p_fut)-1:
            is_peak = p_fut[i] > p_fut[i-1] and p_fut[i] > p_fut[i+1]
            is_bottom = p_fut[i] < p_fut[i-1] and p_fut[i] < p_fut[i+1]
            if is_peak or is_bottom:
                txt_c = 'white' if is_peak else '#
