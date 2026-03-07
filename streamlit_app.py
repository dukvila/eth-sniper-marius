import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija ir Automatinis atnaujinimas (kas 60 sekundžių)
st.set_page_config(page_title="ETH V25.1 PRECISION", layout="wide")
st_autorefresh(interval=60000, key="datarefresh") # Atnaujiname kas minutę
st.title("🕒 ETH SNIPER V25.1 | PRECISION TIME")

def get_market_data():
    try:
        # Naudojame Kraken API
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read().decode())
            if 'result' not in res: return [], []
            d = res['result']['XETHZEUR'][-100:]
            
            # SINCHRONIZACIJA: Kraken laikas yra UTC. Lietuvai pridedame +2h.
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except Exception as e:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 0:
    dabartine = kainos[-1]
    momentum = (kainos[-1] - kainos[-8]) / 8 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # Prognozės generavimas (8 valandos į priekį nuo DABARTINIO laiko)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.7))
        p_fut.append(val)

    # --- PROFESIONALUS BRAIŽYMAS ---
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    
    # Istorija (Mėlyna) ir Prognozė (Neoninė)
    ax.plot(laikai[-40:], kainos[-40:], color='#2962ff', linewidth=2, alpha=0.6)
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=4, label="PROGNOZĖ")
    
    # Kampų skaičiai istorijoje
    for i in range(len(kainos[-40:])-2):
        idx = i + (len(kainos) - 40)
        if (kainos[idx] > kainos[idx-1] and kainos[idx] > kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]+0.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')
        elif (kainos[idx] < kainos[idx-1] and kainos[idx] < kainos[idx+1]):
            ax.text(laikai[idx], kainos[idx]-1.5, f"{kainos[idx]:.1f}", color='#4c8bf5', fontsize=8, ha='center')

    # --- LAIKO AŠIES FORMATAVIMAS ---
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
    
    plt.xticks(color='gray', fontsize=9)
    plt.yticks(color='gray', fontsize=9)
    ax.grid(True, which='both', alpha=0.03, color='white')
    
    # Prognozės pikai su LAIKU
    pikas, dugnas = max(p_fut), min(p_fut)
    for i, val in enumerate(p_fut):
        if val == pikas or val == dugnas:
            ax.scatter(l_fut[i], val, color='#ffffff', s=80, zorder=10)
            ax.text(l_fut[i], val + (2 if val==pikas else -4), 
                    f"{val:.1f}€\n({l_fut[i].strftime('%H:%M')})", 
                    color='white', fontweight='bold', ha='center', fontsize=9)

    st.pyplot(fig)

    # --- ANALITIKA ---
    c1, c2, c3 = st.columns(3)
    c1.metric("REALI KAINA", f"{dabartine:.2f} €", f"{momentum:.2f} €/h")
    c2.metric("VOLATILUMAS", f"{(nuokrypis/dabartine*100):.2f}%")
    
    # Tikslus atnaujinimo laikas pagal Lietuvos zoną
    dabar_lt = datetime.now() + timedelta(hours=2)
    st.info(f"🕒 Paskutinis atnaujinimas: {dabar_lt.strftime('%H:%M:%S')} (LT laikas)")
else:
    st.warning("⏳ Kraunami rinkos duomenys... Palaukite 10 sekundžių.")
