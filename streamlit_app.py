import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta

# 1. Konfigūracija
st.set_page_config(page_title="ETH V24 PRECISION", layout="wide")
st.title("🕒 ETH SNIPER V24 | PRECISION TIMELINE")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-100:]
            # Svarbu: Sutvarkome laiką (+2h Lietuvai)
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except: return [], []

laikai, kainos = get_market_data()

if kainos:
    dabartine = kainos[-1]
    momentum = (kainos[-1] - kainos[-8]) / 8 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # Prognozės generavimas su laiko žymomis (8 valandos į priekį)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(9)]
    p_fut = []
    for h in range(9):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.7))
        p_fut.append(val)

    # --- BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija ir Prognozė
    ax.plot(laikai[-40:], kainos[-40:], color='#2962ff', linewidth=2, alpha=0.7, label="Istorija")
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=4, label="V24 Prognozė")
    
    # Kampų skaičiai (kaip V23 versijoje)
    for i in range(len(kainos[-40:])-2):
        idx = i + (len(kainos) - 40)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+1, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')
        elif (kainos[idx] < kainos[idx-1] and kainos[idx] < kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]-3, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # --- LAIKO AŠIES FORMATAVIMAS ---
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) # Rodyti valandas:minutes
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=60)) # Pagrindinės gairės kas valandą
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15)) # Mažosios gairės kas 15 min
    
    plt.xticks(color='gray', fontsize=9, rotation=0)
    plt.yticks(color='gray', fontsize=9)
    ax.grid(True, which='both', alpha=0.05, color='white') # Tinklas kas 15 min
    
    # Prognozės pikai su laiku
    pikas, dugnas = max(p_fut), min(p_fut)
    for i, val in enumerate(p_fut):
        if val == pikas or val == dugnas:
            ax.scatter(l_fut[i], val, color='#ffffff', s=80, zorder=10)
            ax.text(l_fut[i], val + (2 if val==pikas else -5), 
                    f"{val:.1f}€\n({l_fut[i].strftime('%H:%M')})", 
                    color='white', fontweight='bold', ha='center', fontsize=9)

    st.pyplot(fig)

    # Analitika apačioje
    col1, col2, col3 = st.columns(3)
    col1.metric("REALI KAINA", f"{dabartine:.2f} €", f"{momentum:.2f} €/h")
    col2.metric("VOLATILUMAS", f"{(nuokrypis/dabartine*100):.2f}%")
    col3.info(f"Paskutinis atnaujinimas: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.error("Laukiama duomenų...")
