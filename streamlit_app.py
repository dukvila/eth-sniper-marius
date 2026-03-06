import streamlit as st
import urllib.request, json, statistics, math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- 🎯 KONFIGŪRACIJA ---
st.set_page_config(page_title="ETH SNIPER CLOUD", layout="wide")
CP_API_KEY = "cb3edbdd0bef024331f39e3d16bbafd8cf61208f"

def get_data():
    sentiment = 1.0
    try:
        url_n = f"https://cryptopanic.com/api/v1/posts/?auth_token={CP_API_KEY}&currencies=ETH&filter=hot"
        with urllib.request.urlopen(url_n, timeout=5) as r:
            posts = json.loads(r.read().decode()).get('results', [])
            pos = sum((p.get('votes', {}).get('positive', 0) + p.get('votes', {}).get('bullish', 0)) for p in posts[:12])
            neg = sum((p.get('votes', {}).get('negative', 0) + p.get('votes', {}).get('bearish', 0)) for p in posts[:12])
            sentiment = 1.0 + (pos - neg) / 180
    except: pass
    try:
        url_b = "https://api.binance.com/api/v3/klines?symbol=ETHEUR&interval=1h&limit=100"
        with urllib.request.urlopen(url_b, timeout=5) as r:
            d = json.loads(r.read().decode())
            return [datetime.fromtimestamp(z[0]/1000) for z in d], [float(z[4]) for z in d], sentiment
    except: return [], [], 1.0

# --- PAGRINDINIS PUSLAPIS ---
st.title("🚀 ETH SNIPER - MOBILE RADAR")
st.write("Skaičiuojama 1734€ prognozė...")
placeholder = st.empty()

# Automatinis atnaujinimas
while True:
    laikai, kainos, sentiment = get_data()
    if kainos:
        with placeholder.container():
            dabartine = kainos[-1]
            nuokrypis = statistics.stdev(kainos[-48:])
            trendas = (kainos[-1] - kainos[-18]) / 18 

            fig, ax = plt.subplots(figsize=(10, 5))
            l_at = [datetime.now() + timedelta(hours=h) for h in range(25)]
            p_at = []
            
            for h in range(25):
                val = dabartine + (trendas * h) + ((math.sin(h/3.8)*(nuokrypis*0.8) + math.sin(h/1.2)*(nuokrypis*0.3)) * sentiment)
                p_at.append(val)

            ax.plot(l_at, p_at, color="#005A5A", linewidth=2, label="Prognozės kreivė")
            ax.set_title(f"Sentiment: {sentiment:.2f} | Atnaujinta: {datetime.now().strftime('%H:%M:%S')}")
            
            # Pikų žymėjimas
            for t in range(1, 24):
                if (p_at[t] > p_at[t-1] and p_at[t] > p_at[t+1]) or (p_at[t] < p_at[t-1] and p_at[t] < p_at[t+1]):
                    prob = min(98.8, max(55.0, (84 + (sentiment-1)*55) + math.cos(t)*4))
                    ax.scatter(l_at[t], p_at[t], color="red" if p_at[t] > p_at[t-1] else "orange")
                    ax.text(l_at[t], p_at[t], f"{p_at[t]:.0f}€\n{prob:.1f}%", fontsize=9, ha='center', weight='bold')

            st.pyplot(fig)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Dabartinė Kaina", f"{dabartine:.2f} €")
            c2.metric("Trendas (1h)", f"{trendas:.2f} €")
            c3.metric("Nuotaika (Sentiment)", f"{sentiment:.2f}")

    import time
    time.sleep(30)
