import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="ETH SNIPER", layout="wide")

st.title("🚀 ETH SNIPER - MOBILE RADAR")

# Naudojame paprastesnį duomenų gavimo būdą per Pandas
@st.cache_data(ttl=60)
def get_eth_data():
    try:url = "https://api1.binance.com/api/v3/klines?symbol=ETHEUR&interval=1h&limit=24"
        df = pd.read_json(url)
        df = df.iloc[:, [0, 4]]
        df.columns = ['laikas', 'kaina']
        df['laikas'] = pd.to_datetime(df['laikas'], unit='ms')
        df['kaina'] = df['kaina'].astype(float)
        return df
    except:
        return pd.DataFrame()

if st.button('ATNAUJINTI RADARĄ'):
    data = get_eth_data()
    if not data.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data['laikas'], data['kaina'], color='#00ffcc', linewidth=2, label='ETH/EUR')
        ax.set_facecolor('#1e1e1e')
        fig.patch.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        
        # Prognozės taškas 1734€
        prognoze = 1734.0
        ax.axhline(y=prognoze, color='red', linestyle='--', label='Target 1734€')
        ax.legend()
        
        st.pyplot(fig)
        st.metric("Dabartinė kaina", f"{data['kaina'].iloc[-1]:.2f} €")
    else:
        st.error("Nepavyko gauti duomenų iš biržos. Bandykite dar kartą.")

st.write("Prognozės modelis: v1.0 [1734€ Target]")
