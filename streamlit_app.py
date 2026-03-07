import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V55 QUANTUM RISK SNIPER", layout="wide")
# Automatinis atnaujinimas kas 60 sekundžių
st_autorefresh(interval=60000, key="datarefresh")

def get_market_data():
    try:
        url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR&interval=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            if 'result' in res:
                d = res['result']['XETHZEUR'][-160:]
                # Lietuvos laikas (+2 valandos nuo UTC)
                laikai = [datetime.fromtimestamp(z[0]) + timedelta(hours=2) for z in d]
                kainos = [float(z[4]) for z in d]
                return laikai, kainos
            return [], []
    except:
        return [], []

laikai, kainos = get_market_data()

if kainos and len(kainos) > 50:
    dabartine = kainos[-1]
    
    # --- HARVARD ANALYTICS ENGINE ---
    # Momentum skaičiavimas (kainos kitimo greitis)
    momentum = (kainos[-1] - kainos[-12]) / 3.0
    volatilumas = statistics.stdev(kainos[-40:])
    
    # Efficiency Ratio (ER) - Harvard metodas triukšmui filtruoti
    direction = abs(kainos[-1] - kainos[-10])
    vol_sum = sum(abs(kainos[i] - kainos[i-1]) for i in range(len(kainos)-10, len(kainos)))
    er = direction / vol_sum if vol_sum > 0 else 0
    
    # Tikimybės skaičiavimas (0-100%)
    tikimybe = (er * 80) + (15 if momentum > 0 else 5)
    tikimybe = max(min(tikimybe, 99), 1)

    # --- CRYPTO CRITICAL / RISK MANAGEMENT BLOKAS ---
    if tikimybe > 65 and momentum > 0:
        busena = "🚀 VERTA PIRKTI"
        bg_color = "#28a745" # Ryškiai žalia
    elif tikimybe < 40:
        busena = "⚠️ DIDELĖ RIZIKA - LAUKTI"
        bg_color = "#ff8c00" # Oranžinė (Perspėjimas)
    else:
        busena = "🧐 STEBĖTI RINKĄ"
        bg_color = "#dc3545" # Raudona (Atsargumas)

    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:20px; border-radius:15px; text-align:center; color:white; font-family:sans-
