import streamlit as st
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# --- KONFIGŪRACIJA ---
st.set_page_config(page_title="ETH SNIPER CLOUD", layout="wide")
CP_API_KEY = "cb3edbdd0bef024331f39e3d16bbafd8cf61208f"

def get_data():
    try:
        url_b = "https://api.binance.com/api/v3/klines?symbol=ETHEUR&interval=1h&limit=100"
        with urllib.request.urlopen(url_b, timeout=5) as r:
            d = json.loads(r.read().decode())
            return [datetime.fromtimestamp(z[0]/1000) for z in d], [float(z[4]) for z in d]
    except: return [], []

# --- PAGRINDINIS PUSLAPIS ---
st.title("🚀 ETH SNIPER - MOBILE RADAR")
laikai, kainos = get_data()

if kainos:
    dabartine = kainos[-1]
    nuokrypis = statistics.stdev(kainos[-48:])
    trendas = (kainos[-1] - kainos[-18]) / 18 

    fig, ax = plt.subplots(figsize=(10, 5))
    l_at = [datetime.now() + timedelta(hours=h) for h in range(25)]
    p_at = [dabartine + (trendas * h) + (math.sin(h/3.8)*nuokrypis) for h in range(25)]

    ax.plot(l_at, p_at, color="#005A5A", linewidth=2)
    for t in [6, 12, 18, 24]:
        ax.scatter(l_at[t], p_at[t], color="red")
        ax.text(l_at[t], p_at[t], f"{p_at[t]:.0f}€", fontsize=10, weight='bold')

    st.pyplot(fig)
    st.metric("Dabartinė ETH Kaina", f"{dabartine:.2f} €", f"{trendas:.2f} €")
    st.write("Prognozė 24 valandoms pagal 1734€ modelį.")
    
if st.button('ATNAUJINTI DUOMENIS'):
    st.rerun()
