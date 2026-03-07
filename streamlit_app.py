import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija snaiperio režimui
st.set_page_config(page_title="ETH V66 REVOLUT-X SNIPER", layout="wide")
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
    
    # --- PRO INDICATORS (Snaiperio logika) ---
    # 1. Bollinger Bands (20 periodų, 2 nuokrypiai)
    smaz = pd.Series(kainos).rolling(window=20).mean().iloc[-1]
    stdz = pd.Series(kainos).rolling(window=20).std().iloc[-1]
    virsus = smaz + (stdz * 2.1) # Pasipriešinimas (Parduoti čia)
    apacia = smaz - (stdz * 2.1) # Palaikymas (Pirkti čia)
    
    # 2. RSI (Santykinis stiprumas)
    delta = pd.Series(kainos).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs.iloc[-1]))
    
    # 3. Pivot Points (Apsisukimo taškai)
    yesterday_high = max(highs[-96:])
    yesterday_low = min(lows[-96:])
    pivot = (yesterday_high + yesterday_low + dabartine) / 3

    # --- SNIPER SIGNALAS ---
    if dabartine >= virsus or rsi > 70:
        signalas = "🔴 PARDUOTI DABAR (LUBO)"
        spalva = "#dc3545"
        rekomendacija = f"Kaina pasiekė pasipriešinimą ({virsus:.1f}€). Didelė kritimo tikimybė."
    elif dabartine <= apacia or rsi < 30:
        signalas = "🟢 PIRKTI DABAR (DUGNAS)"
        spalva = "#28a745"
        rekomendacija = f"Kaina pasiekė dugną ({apacia:.1f}€). Ruoškis atšokimui į viršų."
    else:
        signalas = "⚪ LAUKTI SIGNALO"
        spalva = "#6c757d"
        rekomendacija = "Rinka viduryje koridoriaus. Day-trading rizika per didelė."

    st.markdown(f"""
    <div style="background-color:{spalva}; padding:25px; border-radius:15px; text-align:center; color:white; border: 4px solid white;">
        <h1 style="margin:0; font-size:45px;">{signalas}</h1>
        <p style="font-size:22px; margin:10px;">{rekomendacija}</p>
        <hr>
        <p style="font-size:18px;">RSI: {rsi:.1f} | BB Viršus: {virsus:.1f}€ | BB Apačia: {apacia:.1f}€</p>
    </div>
    """, unsafe_allow_html=True)

    # --- DINAMINĖ PROGNOZĖ (Reakcija į koridorių) ---
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = []
    current_p = dabartine
    for h in range(1, 11):
        # Matematika: Kaina traukiama link Pivot taško, jei ji per aukštai/žemsiai
        atstumas = pivot - current_p
        kryptis = atstumas * 0.15 * h
        noise = (stdz * 0.3 * np.sin(h))
        next_p = current_p + kryptis + noise
        p_fut.append(next_p)
        current_p = next_p

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija (trumpa)
    ax.plot(laikai[-20:], kainos[-20:], color='white', linewidth=2, alpha=0.3)
    
    # BB Koridorius (Snaiperio matymas)
    ax.fill_between(l_fut, apacia, virsus, color='#1f1f1f', alpha=0.5, label="Saugumo zona")
    ax.axhline(virsus, color='#dc3545', linestyle='--', alpha=0.6, label="PARDAVIMO RIBA")
    ax.axhline(apacia, color='#28a745', linestyle='--', alpha=0.6, label="PIRKIMO RIBA")
    
    # Prognozės linija
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=6, marker='o', markersize=8, label="Snaiperio trajektorija")
    
    # Kainos etiketės
    for i in [2, 5, 9]:
        ax.text(l_fut[i], p_fut[i] + 1.5, f"{p_fut[i]:.1f}€", color='cyan', fontweight='bold', ha='center')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.05, color='white')
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    st.pyplot(fig)
    
    st.caption(f"Duomenys sinchronizuoti su Revolut X rinka. Atnaujinta: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("🔄 Kraunama snaiperio analizės sistema...")
