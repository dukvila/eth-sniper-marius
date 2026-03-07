import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V74 ULTRA-STABLE", layout="wide")
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
                return laikai, kainos
            return [], []
    except Exception:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 60:
    dabartine = kainos[-1]
    
    # --- MATEMATINIS MODELIS ---
    smaz = pd.Series(kainos).rolling(window=20).mean().iloc[-1]
    stdz = pd.Series(kainos).rolling(window=20).std().iloc[-1]
    virsus = smaz + (stdz * 2.1)
    apacia = smaz - (stdz * 2.1)
    
    # RSI (Relative Strength Index)
    delta = pd.Series(kainos).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] > 0 else 100
    
    # Saugumo lygiai
    stop_loss = apacia * 0.995 
    target_1717 = 1717.85 # Tavo Revolut X tikslas
    
    # Prognozė
    momentum = (kainos[-1] - kainos[-8]) / 2.0
    l_fut = [laikai[-1] + timedelta(minutes=30*h) for h in range(1, 11)]
    p_fut = [dabartine + (momentum * h * 0.8) + (stdz * 0.1 * np.sin(h)) for h in range(1, 11)]

    # Signalų logika
    if dabartine <= stop_loss:
        sig, col, txt = "⚠️ STOP LOSS", "#721c24", "Kaina žemiau saugaus lygio!"
    elif dabartine >= virsus or rsi > 76:
        sig, col, txt = "🔴 PARDUOTI", "#dc3545", f"Kaina viršūnėje ({virsus:.1f}€)."
    elif dabartine <= apacia or rsi < 36:
        sig, col, txt = "🟢 PIRKTI", "#28a745", "Dugnas pasiektas. Ruoškis šuoliui."
    elif momentum > 0.3:
        sig, col, txt = "🚀 KILIMAS", "#007bff", f"Tikslas: {target_1717}€."
    else:
        sig, col, txt = "🟡 LAUKTI", "#ff8c00", "Rinka ieško krypties."

    # Interfisas (Pilnai sutvarkytas blokas)
    st.markdown(f"""
    <div style="background-color:{col}; padding:30px; border-radius:15px; text-align:center; color:white; border: 5px solid white;">
        <h1 style="margin:0; font-size:42px;">{sig}</h1>
        <p style="font-size:22px; margin:15px;">{txt}</p>
        <div style="display:flex; justify-content: space-around; background:rgba(0,0,0,0.2); padding:12px; border-radius:10px;">
            <span>Kaina: {dabartine:.2f}€</span>
            <span style="color:#ff4b4b;">STOP: {stop_loss:.1f}€</span>
            <span style="color:#00ffcc;">TIKSLAS: {target_1717}€</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    ax.plot(laikai[-15:], kainos[-15:], color='white', alpha=0.3)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=6, marker='o', markersize=8)
    
    ax.axhline(target_1717, color='cyan', linestyle='--', alpha=0.5, label="Profit Target")
    ax.axhline(stop_loss, color='red', linestyle='-', alpha=0.6, label="Stop Loss")
    
    # Sutvarkytos etiketės (be klaidų)
    for i in [2, 5, 9]:
        ax.text(l_fut[i], p_fut[i] + 1.2, f"{p_fut[i]:.1f}€", color='cyan', fontweight='bold', ha='center')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.grid(True, alpha=0.05)
    plt.legend(loc='upper left', fontsize='small')
    st.pyplot(fig)

    st.success(f"Sistema paruošta prekybai. RSI: {rsi:.1f}")
else:
    st.warning("🔄 Jungiamasi prie Revolut X snaiperio...")
