import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V67 AGGRESSIVE SNIPER", layout="wide")
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
                return laikai, kainos, highs, lows
            return [], [], [], []
    except:
        return [], [], [], []

laikai, kainos, highs, lows = get_market_data()

if kainos and len(kainos) > 60:
    dabartine = kainos[-1]
    
    # --- SKAIČIAVIMAI ---
    smaz = pd.Series(kainos).rolling(window=20).mean().iloc[-1]
    stdz = pd.Series(kainos).rolling(window=20).std().iloc[-1]
    virsus = smaz + (stdz * 2.0)
    apacia = smaz - (stdz * 2.0)
    
    # RSI skaičiavimas
    delta = pd.Series(kainos).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] > 0 else 100
    
    # AGRESYVI PROGNOZĖ (Revolut X Day-Trading)
    momentum = (kainos[-1] - kainos[-8]) / 2.0
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    for h in range(1, 11):
        # Modelis reaguoja į dabartinį trendą be stabdžių
        fut_val = dabartine + (momentum * h * 0.8) + (stdz * 0.2 * np.sin(h))
        p_fut.append(fut_val)
    
    prognozuojamas_pikas = max(p_fut)
    galimas_pelnas = prognozuojamas_pikas - dabartine

    # --- AGRESYVUS SIGNALAS (Nebėra "Laukti") ---
    if galimas_pelnas > 1.5 and rsi < 75:
        signalas = f"🟢 PIRKTI DABAR (PROGNOZĖ +{galimas_pelnas:.1f}€)"
        spalva = "#28a745"
        zinute = f"Matematinis modelis rodo kilimą link {prognozuojamas_pikas:.1f}€. Revolut X: Atidaryk poziciją."
    elif dabartine >= virsus or rsi > 78:
        signalas = "🔴 PARDUOTI / FIKSUOTI PELNĄ"
        spalva = "#dc3545"
        zinute = "Kaina pasiekė viršutinį koridorių. Rizika apsisukti žemyn yra maksimali."
    else:
        signalas = "🟡 STEBĖTI TRENDĄ"
        spalva = "#ff8c00"
        zinute = "Rinka ieško krypties, bet prognozė išlieka stabili."

    st.markdown(f"""
    <div style="background-color:{spalva}; padding:25px; border-radius:15px; text-align:center; color:white; border: 4px solid white;">
        <h1 style="margin:0; font-size:40px;">{signalas}</h1>
        <p style="font-size:20px; margin:10px;">{zinute}</p>
        <p style="font-size:16px;">Dabartinė: {dabartine:.2f}€ | RSI: {rsi:.1f} | Tikslas: {prognozuojamas_pikas:.1f}€</p>
    </div>
    """, unsafe_allow_html=True)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Minimali praeitis
    ax.plot(laikai[-10:], kainos[-10:], color='white', linewidth=2, alpha=0.3)
    
    # PROGNOZĖ
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=6, marker='o', markersize=8, label="Snaiperio kelias")
    
    # Pasipriešinimo linija iš tavo grafiko
    ax.axhline(1717.8, color='red', linestyle='--', alpha=0.5, label="Revolut pasipriešinimas")
    
    # Kainos etiketės ant prognozės
    for i in [2, 5, 9]:
        ax.text(l_fut[i], p_fut[i] + 1.5, f"{p_fut[i]:.1f}€", color='cyan', fontweight='bold', ha='center')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.05, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    st.pyplot(fig)
    
    st.info(f"Snaiperis paruoštas. Revolut X laikas: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("🔄 Sinchronizuojami agresyvūs skaičiavimai...")
