import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import urllib.request, json, statistics
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigūracija
st.set_page_config(page_title="ETH V73 SAFE-TARGET", layout="wide")
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
    
    # --- ANALITIKA ---
    smaz = pd.Series(kainos).rolling(window=20).mean().iloc[-1]
    stdz = pd.Series(kainos).rolling(window=20).std().iloc[-1]
    virsus = smaz + (stdz * 2.1)
    apacia = smaz - (stdz * 2.1)
    
    # RSI
    delta = pd.Series(kainos).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] > 0 else 100
    
    # --- APSAUGA (STOP-LOSS) ---
    # Skaičiuojame Stop-Loss 0.5% žemiau Bollinger Bands apačios arba paskutinio dugno
    stop_loss_lygis = apacia * 0.995 
    pelnas_tikslas = 1717
