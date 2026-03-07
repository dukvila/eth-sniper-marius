import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V28.1 VISUAL FINISH", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V28.1 | VISUAL FINISH")

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
    volat = (nuokrypis / dabartine) * 100
    
    # Prognozės generavimas
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.7))
        p_fut.append(val)

    max_p = max(p_fut)
    pelnas = max_p - dabartine
    piko_idx = p_fut.index(max_p)

    # --- BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Rodome paskutines 15 istorinių žvakių
    ax.plot(laikai[-15:], kainos[-15:], color='#2962ff', linewidth=3, alpha=0.4)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=5)
    
    # Skaičių fiksavimas smaigaliuose (V28)
    for i in range(len(kainos[-15:])-2):
        idx = i + (len(kainos) - 15)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')
        elif (kainos[idx] < kainos[idx-1] and kainos[idx] < kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]-1.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # --- KINTANTIS SIMBOLIS (Raketa/Parašiutas/Plaukikas) ---
    if momentum > 0.15: # Stiprus kilimas
        simbolis = '🚀'
    elif momentum < -0.15: # Stiprus kritimas
        simbolis = '🪂'
    else: # Stovi vietoje (Neutralu)
        simbolis = '🏊‍♂️'
        
    ax.text(laikai[-1], kainos[-1], simbolis, fontsize=18, ha='center', va='center', zorder=20)

    # Tikslo žymėjimas (V28)
    ax.scatter(l_fut[piko_idx], max_p, color='white', s=100, zorder=15)
    ax.text(l_fut[piko_idx], max_p + 1.5, f"{max_p:.1f}€\n({l_fut[piko_idx].strftime('%H:%M')})", color='white', fontweight='bold', ha='center', fontsize=9)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    ax.grid(True, alpha=0.03, color='white')
    st.pyplot(fig)

    # Skaitikliai apačioje
    c1, c2, c3 = st.columns(3)
    c1.metric("KAINA", f"{dabartine:.2f} €")
    c2.metric("POTENCIALUS PELNAS", f"+{pelnas:.2f} €")
    c3.info(f"🕒 LT Laikas: {(datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')}")
else:
    st.warning("🔄 Jungiamasi...")
