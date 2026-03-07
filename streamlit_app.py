import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V40 SHARP PRECISION", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V40 | SHARP PRECISION")

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
    except:
        return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    momentum = (kainos[-1] - kainos[-8]) / 2 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # --- AŠTRI PROGNOZĖ (Kampai ir lūžiai) ---
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 12)]
    p_fut = []
    for h in range(1, 12):
        # Sukuriame aštrų zigzagą vietoj švelnios bangos
        svyravimas = (nuokrypis * 1.6) if h % 4 == 0 else -(nuokrypis * 1.3) if h % 2 == 0 else (nuokrypis * 0.4)
        val = dabartine + (momentum * h) + svyravimas
        p_fut.append(val)

    max_p = max(p_fut)
    min_p_fut = min(p_fut)
    piko_idx = p_fut.index(max_p)
    dugno_idx = p_fut.index(min_p_fut)

    # --- GRAFIKO BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorinis grafikas (Aštri linija)
    ax.plot(laikai[-35:], kainos[-35:], color='#1a46ba', linewidth=4, alpha=0.8)
    
    # Istorinių smaigalių sumos (Melsvos)
    for i in range(len(kainos[-35:])-2):
        idx = i + (len(kainos) - 35)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=9, ha='center')

    # Aštri neoninė prognozė su taškais lūžio vietose
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5, alpha=0.9, marker='o', markersize=5)
    
    # --- SUMOS ANT PROGNOZĖS TAŠKŲ ---
    # Aukščiausias prognozės taškas
    ax.scatter(l_fut[piko_idx], max_p, color='white', s=150, zorder=25)
    ax.text(l_fut[piko_idx], max_p + 1.2, f"{max_p:.1f}€", color='white', fontweight='bold', ha='center', fontsize=11)
    
    # Žemiausias prognozės taškas (Dugnas)
    if dugno_idx != piko_idx:
        ax.scatter(l_fut[dugno_idx], min_p_fut, color='#ff4b4b', s=120, zorder=25)
        ax.text(l_fut[dugno_idx], min_p_fut - 2.8, f"{min_p_fut:.1f}€", color='#ff4b4b', fontweight='bold', ha='center', fontsize=11)

    # --- INDIKATORIUS (Žalias, Raudonas arba Geltonas) ---
    if momentum > 0.15:
        ax.scatter(laikai[-1], kainos[-1], marker='^', color='#00ff00', s=300, zorder=30)
    elif momentum < -0.15:
        ax.scatter(laikai[-1], kainos[-1], marker='v', color='#ff0000', s=300, zorder=30)
    else:
        ax.scatter(laikai[-1], kainos[-1], marker='o', color='#ffeb3b', s=250, zorder=30) # GELTONAS TAŠKAS

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.05, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    st.pyplot(fig)

    # Realaus laiko duomenys apačioje
    c1, c2, c3 = st.columns(3)
    c1.metric("DABARTINĖ", f"{dabartine:.2f} €")
    c2.metric("MOMENTUMAS", f"{momentum:.2f} €/h")
    c3.write(f"🕒 Atnaujinta: **{datetime.now().strftime('%H:%M:%S')}**")
else:
    st.error("Nepavyko gauti duomenų. Patikrinkite interneto ryšį.")
