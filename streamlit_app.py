import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Pagrindiniai puslapio nustatymai
st.set_page_config(page_title="ETH SNIPER", layout="wide")
st.title("🚀 ETH SNIPER - MOBILE RADAR")

# 2. Funkcija duomenims gauti
def get_eth_data():
    try:
        # Naudojame alternatyvų Binance API adresą (api1), kad išvengtume blokavimo
        url = "https://api1.binance.com/api/v3/klines?symbol=ETHEUR&interval=1h&limit=24"
        df = pd.read_json(url)
        df = df.iloc[:, [0, 4]]
        df.columns = ['laikas', 'kaina']
        df['laikas'] = pd.to_datetime(df['laikas'], unit='ms')
        df['kaina'] = df['kaina'].astype(float)
        return df
    except Exception as e:
        # Jei įvyksta klaida, grąžiname tuščią lentelę
        return pd.DataFrame()

# 3. Mygtukas ir grafiko braižymas
if st.button('ATNAUJINTI RADARĄ'):
    data = get_eth_data()
    
    if not data.empty:
        # Sukuriame tamsaus stiliaus grafiką
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data['laikas'], data['kaina'], color='#00ffcc', linewidth=2, label='ETH/EUR')
        
        # Estetika pritaikyta telefonui
        ax.set_facecolor('#1e1e1e')
        fig.patch.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.grid(color='gray', linestyle='--', alpha=0.3)
        
        # Prognozės linija ties 1734€
        prognoze = 1734.0
        ax.axhline(y=prognoze, color='red', linestyle='--', label='Target 1734€')
        ax.legend()
        
        # Rodome grafiką ir kainą
        st.pyplot(fig)
        st.metric("Dabartinė kaina", f"{data['kaina'].iloc[-1]:.2f} €")
    else:
        # Pranešimas, jei Binance neatsako
        st.error("Nepavyko gauti duomenų. Palaukite 10 sekundžių ir spauskite dar kartą.")

st.write("Prognozės modelis: v1.2 [1734€ Target]")
