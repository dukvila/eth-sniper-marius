import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta

# 1. Terminalo Konfigūracija
st.set_page_config(page_title="ETH V21.1 ELITE", layout="wide")
st.title("🛡️ ETH SNIPER V21.1 | ELITE TERMINAL")

def get_pro_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            d = res['result']['XETHZEUR'][-60:]
            laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
            kainos = [float(z[4]) for z in d]
            return laikai, kainos
    except: return [], []

laikai, kainos = get_pro_data()

if kainos:
    dabartine = kainos[-1]
    jega = (kainos[-1] - kainos[-4]) / 4 
    nuokrypis = statistics.stdev(kainos[-20:])
    
    # --- VOLATILITY ALERT SISTEMA ---
    # Skaičiuojame momentinį svyravimą (procentais)
    svyravimas = (nuokrypis / dabartine) * 100
    
    if svyravimas > 0.5: # Jei svyravimas viršija 0.5%, tai jau pavojinga
        st.error(f"⚠️ DĖMESIO: DIDELIS SVYRAVIMAS ({svyravimas:.2f}%)! Rinka tampa nenuspėjama.")
    elif svyravimas < 0.1:
        st.success(f"✅ RAMI RINKA ({svyravimas:.2f}%). Svyravimai minimalūs.")
    else:
        st.warning(f"🟡 VIDUTINIS JUDĖJIMAS ({svyravimas:.2f}%). Stebėkite momentumą.")

    # Prognozės generavimas (8 valandos)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(9)]
    p_fut = []
    for h in range(9):
        val = dabartine + (jega * h) + (math.sin(h/2) * (nuokrypis * 0.5))
        p_fut.append(val)

    # Braižymas
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#060606')
    ax.set_facecolor('#060606')
    ax.plot(laikai[-20:], kainos[-20:], color='#1a73e8', alpha=0.4, label="ISTORIJA")
    ax.plot(l_fut, p_fut, color='#00ffcc', linewidth=3, label="PROGNOZĖ")
    
    # Tikslai
    pikas, dugnas = max(p_fut), min(p_fut)
    for i, val in enumerate(p_fut):
        if val == pikas or val == dugnas:
            ax.scatter(l_fut[i], val, color='#ff4444' if val == pikas else '#ffbb00', s=120, zorder=5)
            ax.text(l_fut[i], val + 1, f"{val:.1f}€", color='white', ha='center', fontweight='bold')

    ax.grid(True, alpha=0.05, color='white')
    st.pyplot(fig)

    c1, c2, c3 = st.columns(3)
    c1.metric("REALI KAINA", f"{dabartine:.2f} €")
    c2.metric("MOMENTUM", f"{jega:.2f}", delta=f"{jega:.2f} €/15min")
    c3.metric("VOLATILITY INDEX", f"{svyravimas:.3f}%")
else:
    st.error("Terminalas negali pasiekti duomenų.")
