import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Puslapio nustatymai telefonui
st.set_page_config(page_title="ETH SNIPER", layout="wide")
st.title("🚀 ETH SNIPER - MOBILE RADAR")

# 2. Funkcija duomenims gauti iš stabilesnio šaltinio
def get_eth_data():
    try:
        # Naudojame CryptoCompare - jie rečiau blokuoja debesies serverius
        url = "https://min-api.cryptocompare.com/data/v2/histohour?fsym=ETH&tsym=EUR&limit=24"
        df_raw = pd.read_json(url)
        data_list = df_raw['Data']['Data']
        df = pd.DataFrame(data_list)
        
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df[['time', 'close']]
        df.columns = ['laikas', 'kaina']
        return df
    except Exception as e:
        return pd.DataFrame()

# 3. Mygtukas ir grafikas
if st.button('ATNAUJINTI RADARĄ'):
    data = get_eth_data()
    
    if not data.empty:
        # Braižome profesionalų tamsų grafiką
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data['laikas'], data['kaina'], color='#00ffcc', linewidth=3, label='ETH/EUR')
        
        # Estetika pritaikyta tamsiam režimui
        ax.set_facecolor('#1e1e1e')
        fig.patch.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.grid(color='gray', linestyle='--', alpha=0.3)
        
        # Prognozės linija ties 1734€
        prognoze = 1734.0
        ax.axhline(y=prognoze, color='#ff4b4b', linestyle='--', linewidth=2, label='Target 1734€')
        ax.legend()
        
        st.pyplot(fig)
        st.metric("Dabartinė ETH kaina", f"{data['kaina'].iloc[-1]:.2f} €")
        st.success("Radaras atnaujintas!")
    else:
        st.error("Nepavyko prisijungti prie biržos. Bandykite dar kartą.")

st.write("Prognozės modelis: v1.3 [1734€ Target]")
