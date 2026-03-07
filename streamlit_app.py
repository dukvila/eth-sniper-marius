import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V27 PROFIT ANALYZER", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")
st.title("💰 ETH SNIPER V27 | PROFIT ANALYZER")

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
    
    # Prognozės generavimas (iki 9 valandų į priekį)
    l_fut = [laikai[-1] + timedelta(hours=h) for h in range(1, 10)]
    p_fut = []
    for h in range(1, 10):
        val = dabartine + (momentum * h) + (math.sin(h/2.2) * (nuokrypis * 0.7))
        p_fut.append(val)

    # --- PELNO IR LAIKO ANALIZĖ ---
    max_p_fut = max(p_fut)
    tikėtinas_pelnas = max_p_fut - dabartine
    piko_idx = p_fut.index(max_p_fut)
    piko_laikas = l_fut[piko_idx]
    
    # Strategijos nustatymas
    if momentum > 0.1 and tikėtinas_pelnas > 2.0:
        statusas = "🚀 PIRKTI"
        spalva = "#28a745" # Žalia
        detalės = f"Tikėtinas pelnas: +{tikėtinas_pelnas:.2f}€ | Parduoti iki {piko_laikas.strftime('%H:%M')}"
    elif momentum < -0.1:
        statusas = "📉 PARDUOTI / LAUKTI"
        spalva = "#dc3545" # Raudona
        detalės = "Rinka krenta. Kitas galimas dugnas prognozuojamas žemiau."
    else:
        statusas = "⌛ NEUTRALU"
        spalva = "#ffc107" # Geltona
        detalės = "Per mažas pelno potencialas arba rinka stovi vietoje."

    # --- REKOMENDACIJOS SKYDELIS ---
    st.markdown(f"""
        <div style="background-color: {spalva}; padding: 25px; border-radius: 15px; text-align: center; color: white;">
            <h1 style="margin: 0;">{statusas}</h1>
            <h3 style="margin: 10px 0 0 0; opacity: 0.9;">{detalės}</h3>
        </div>
    """, unsafe_allow_html=True)

    # --- GRAFIKAS ---
    fig, ax = plt.subplots(figsize=(14, 6), facecolor='black')
    ax.set_facecolor('#0a0a0a')
    ax.plot(laikai[-
