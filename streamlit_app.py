import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta

# 1. Konfigūracija
st.set_page_config(page_title="ETH V22 HYPER-SENSE", layout="wide")
st.title("⚡ ETH SNIPER V22 | HYPER-SENSE TERMINAL")

def get_market_engine():
    try:
        # Kraken 15min duomenys
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-100:]
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            aukstos = [float(z[2]) for z in d]
            zemos = [float(z[3]) for z in d]
            return laikai, kainos, aukstas, zemos
    except: return [], [], [], []

laikai, kainos, aukstas, zemos = get_market_engine()

if kainos:
    # --- PROFESIONALŪS INDIKATORIAI (TradingView logika) ---
    dabartine = kainos[-1]
    ema_20 = statistics.mean(kainos[-20:])
    rsi_val = 50 + ( (dabartine - ema_20) / statistics.stdev(kainos[-40:]) * 10 ) # Emuliuotas RSI
    momentum = (kainos[-1] - kainos[-8]) / 8
    
    # --- PROGNOZĖS IR FAKTŲ SUTAPIMO MODELIS ---
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(10)]
    p_fut = []
    
    # Savireguliacija: jei RSI per aukštas (>70), prognozė automatiškai spaudžiama žemyn
    korekcija = 0.8 if rsi_val > 65 else 1.2 if rsi_val < 35 else 1.0
    
    for h in range(10):
        val = dabartine + (momentum * h * korekcija) + (math.sin(h/1.8) * statistics.stdev(kainos[-20:]) * 0.6)
        p_fut.append(val)

    # --- BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
    ax.set_facecolor('#080808')
    
    # 1. Istorinė linija su kampų žymėjimu
    ax.plot(laikai[-30:], kainos[-30:], color='#2962ff', linewidth=2, alpha=0.8, label="ISTORIJA")
    
    # FAKTINIAI KAMPŲ SKAIČIAI (Praeities pikai)
    for i in range(len(kainos[-30:])-1):
        idx = i + (len(kainos) - 30)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+1, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')
        if (kainos[idx] < kainos[idx-1] and kainos[idx] < kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]-3, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # 2. Prognozės linija
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=4, label="V22 HYPER PROGNOZĖ")
    
    # Prognozės taškai
    for i, val in enumerate(p_fut):
        if val == max(p_fut) or val == min(p_fut):
            ax.scatter(l_fut[i], val, color='#00ffcc', s=100, edgecolors='white')
            ax.text(l_fut[i], val+2, f"TIKSLAS: {val:.1f}€", color='white', fontweight='bold', ha='center')

    ax.grid(True, alpha=0.03, color='white')
    st.pyplot(fig)

    # --- ANALITINIS SKYDELIS (TradingView stiliaus) ---
    st.subheader("📊 TECHNINĖS ANALIZĖS KONSENSUSAS")
    c1, c2, c3, c4 = st.columns(4)
    
    status = "STIPRU PIRKTI" if rsi_val < 40 else "STIPRU PARDUOTI" if rsi_val > 60 else "NEUTRALU"
    c1.metric("REALI KAINA", f"{dabartine:.2f} €", f"{momentum:.2f}")
    c2.metric("EMULIUOTAS RSI", f"{rsi_val:.1f}", status)
    c3.metric("MOMENTUM JĖGA", f"{momentum:.2f}")
    
    volat = (statistics.stdev(kainos[-20:]) / dabartine) * 100
    c4.metric("RINKOS NERVINGUMAS", f"{volat:.2f}%")

    st.info("💡 V22 naudoja hibridinį modelį: Prognozė koreguojama pagal RSI ir Momentum sutapimą.")
else:
    st.error("Nepavyko gauti duomenų.")
