import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V27.3 TARGET LOCK", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🎯 ETH SNIPER V27.3 | TARGET LOCK")

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
    momentum = (kainos[-1] - kainos[-8]) / 8 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # Prognozės generavimas (8 valandos į priekį)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.7))
        p_fut.append(val)

    # --- PIKŲ IR DUGNŲ RADIMAS ---
    max_p = max(p_fut)
    min_p = min(p_fut)
    piko_idx = p_fut.index(max_p)
    dugno_idx = p_fut.index(min_p)
    
    pelnas = max_p - dabartine

    # --- REKOMENDACIJOS SKYDELIS ---
    if momentum > 0.1 and pelnas > 1.5:
        st.success(f"🚀 PIRKTI | Tikslas: {max_p:.1f}€ iki {l_fut[piko_idx].strftime('%H:%M')}")
    else:
        st.warning(f"⌛ LAUKTI | Galimas dugnas: {min_p:.1f}€ apie {l_fut[dugno_idx].strftime('%H:%M')}")

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Praeitis (mažiau) ir Ateitis (daugiau)
    ax.plot(laikai[-15:], kainos[-15:], color='#2962ff', linewidth=3, alpha=0.4)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5)
    
    # 1. VIRŠŪNĖS FIKSAVIMAS (Parduoti)
    ax.scatter(l_fut[piko_idx], max_p, color='white', s=150, zorder=15, edgecolors='#00ffcc')
    ax.text(l_fut[piko_idx], max_p + 1.5, f"PARDUOTI: {max_p:.1f}€\n({l_fut[piko_idx].strftime('%H:%M')})", 
            color='white', fontweight='bold', ha='center', fontsize=10)

    # 2. DUGNO FIKSAVIMAS (Pirkti/Pradeda kilti)
    ax.scatter(l_fut[dugno_idx], min_p, color='white', s=150, zorder=15, edgecolors='#ff4b4b')
    ax.text(l_fut[dugno_idx], min_p - 3.5, f"DUGNAS: {min_p:.1f}€\n({l_fut[dugno_idx].strftime('%H:%M')})", 
            color='#ff4b4b', fontweight='bold', ha='center', fontsize=10)

    # Senų pikų žymėjimas
    for i in range(len(kainos[-15:])-2):
        idx = i + (len(kainos) - 15)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    ax.grid(True, alpha=0.03, color='white')
    st.pyplot(fig)

    # Skaitikliai
    c1, c2, c3 = st.columns(3)
    c1.metric("DABARTINĖ KAINA", f"{dabartine:.2f} €")
    c2.metric("PELNO POTENCIALAS", f"+{pelnas:.2f} €")
    c3.info(f"🕒 Atnaujinta: {(datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')}")
else:
    st.error("Jungiamasi prie Kraken...")
