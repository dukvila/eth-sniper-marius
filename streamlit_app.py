import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V26 STRATEGY", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("🛡️ ETH SNIPER V26 | STRATEGY ENGINE")

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
    
    # --- STRATEGIJOS LOGIKA ---
    if momentum > 0.15 and volat < 0.5:
        rekomendacija = "🚀 PIRKTI (STIPRUS TRENDAS)"
        spalva = "green"
    elif momentum < -0.15 and volat < 0.5:
        rekomendacija = "📉 PARDUOTI (KRITIMO RIZIKA)"
        spalva = "red"
    else:
        rekomendacija = "⌛ LAUKTI (NEUTRALŪS DUOMENYS)"
        spalva = "orange"

    # Rekomendacijos rodymas viršuje
    st.markdown(f"""
        <div style="background-color: {spalva}; padding: 20px; border-radius: 10px; text-align: center;">
            <h1 style="color: white; margin: 0;">REKOMENDACIJA: {rekomendacija}</h1>
        </div>
    """, unsafe_allow_html=True)

    # Prognozė (8 valandos)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.7))
        p_fut.append(val)

    # --- BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(14, 6), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    ax.plot(laikai[-40:], kainos[-40:], color='#2962ff', linewidth=2, alpha=0.5)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=4)
    
    # Kampų žymėjimas
    for i in range(len(kainos[-40:])-2):
        idx = i + (len(kainos) - 40)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # Ašies formatas
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(color='gray')
    plt.yticks(color='gray')
    ax.grid(True, alpha=0.03, color='white')
    
    # Prognozės pikai
    pikas, dugnas = max(p_fut), min(p_fut)
    for i, val in enumerate(p_fut):
        if val == pikas or val == dugnas:
            ax.scatter(l_fut[i], val, color='white', s=80, zorder=10)
            ax.text(l_fut[i], val + (2 if val==pikas else -4), f"{val:.1f}€\n({l_fut[i].strftime('%H:%M')})", color='white', ha='center')

    st.pyplot(fig)

    # Apatinis skydelis
    c1, c2, c3 = st.columns(3)
    c1.metric("REALI KAINA", f"{dabartine:.2f} €")
    c2.metric("MOMENTUMAS", f"{momentum:.2f} €/h")
    dabar_lt = datetime.now() + timedelta(hours=2)
    st.info(f"🕒 Atnaujinta: {dabar_lt.strftime('%H:%M:%S')} | Rinka: {'STABILI' if volat < 0.3 else 'AKTYVI'}")
else:
    st.error("Duomenų sinchronizacija...")
