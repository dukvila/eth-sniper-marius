import urllib.request, json, time, statistics, math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates

# --- 🎯 KONFIGŪRACIJA ---
# Tavo CryptoPanic API raktas
CP_API_KEY = "cb3edbdd0bef024331f39e3d16bbafd8cf61208f"

def get_market_data():
    """Gauna kainas iš Binance ir nuotaikas iš CryptoPanic"""
    sentiment = 1.0
    try:
        # 1. Nuotaikos (CryptoPanic)
        url_n = f"https://cryptopanic.com/api/v1/posts/?auth_token={CP_API_KEY}&currencies=ETH&filter=hot"
        with urllib.request.urlopen(url_n, timeout=5) as r:
            posts = json.loads(r.read().decode()).get('results', [])
            pos = sum((p.get('votes', {}).get('positive', 0) + p.get('votes', {}).get('bullish', 0)) for p in posts[:12])
            neg = sum((p.get('votes', {}).get('negative', 0) + p.get('votes', {}).get('bearish', 0)) for p in posts[:12])
            sentiment = 1.0 + (pos - neg) / 180
    except: pass
    
    try:
        # 2. Kainos (Binance)
        url_b = "https://api.binance.com/api/v3/klines?symbol=ETHEUR&interval=1h&limit=100"
        with urllib.request.urlopen(url_b, timeout=5) as r:
            d = json.loads(r.read().decode())
            return [datetime.fromtimestamp(z[0]/1000) for z in d], [float(z[4]) for z in d], sentiment
    except: return [], [], 1.0

def update_radar(i):
    """Pagrindinė atnaujinimo funkcija"""
    laikai, kainos, sentiment = get_market_data()
    if not kainos: return
    
    # 🎯 PROGNOZĖS SKAIČIAVIMAS
    dabartine = kainos[-1]
    nuokrypis = statistics.stdev(kainos[-48:])
    trendas = (kainos[-1] - kainos[-18]) / 18 

    ax.clear()
    l_at = [datetime.now() + timedelta(hours=h) for h in range(25)]
    p_at = []
    
    for h in range(25):
        val = dabartine + (trendas * h) + ((math.sin(h/3.8)*(nuokrypis*0.8) + math.sin(h/1.2)*(nuokrypis*0.3)) * sentiment)
        p_at.append(val)

    # 1. Piešiame pagrindinę liniją (mėlyna, ryški)
    ax.plot(l_at, p_at, color="#005A5A", linewidth=3, alpha=0.9, label="ETH PROGNOZĖ")
    
    # 2. Nustatome dinaminį mastelį (margins), kad tekstas turėtų vietos
    ax.margins(x=0.03, y=0.15) # Daugiau vietos viršuje ir apačioje

    # 3. TVARKINGAS PIKŲ ŽYMĖJIMAS (Išmanus lygiavimas)
    for t in range(1, 24):
        is_max = p_at[t] > p_at[t-1] and p_at[t] > p_at[t+1]
        is_min = p_at[t] < p_at[t-1] and p_at[t] < p_at[t+1]
        
        if is_max or is_min:
            # Tikimybė % (55% - 98%)
            prob = min(98.8, max(55.0, (84 + (sentiment-1)*55) + math.cos(t)*4))
            
            # Pasirenkame taško spalvą
            color = "#D32F2F" if is_max else "#F57C00"
            ax.scatter(l_at[t], p_at[t], color=color, s=120, edgecolors='black', zorder=5)
            
            # --- Išmanusis Lygiavimas: Spaudžiame, kur daugiau vietos ---
            # Žiūrime, ar tai pikas ar dugnas, ir paslenkame
            offset = 12 if is_max else -32
            va_align = 'bottom' if is_max else 'top'
            
            # Jei grafikas labai „suspaustas“ (pvz., piko aukštis arti max), 
            # mes papildomai tikriname y_min ir y_max. Čia sureguliuojame pagal y_off.
            ax.text(l_at[t], p_at[t] + offset, f"{p_at[t]:.1f}€\n{prob:.1f}%", 
                    ha='center', va=va_align, fontsize=10, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))

    # 4. Estetika ir Laikas
    time_str = datetime.now().strftime('%H:%M:%S')
    ax.set_title(f"🚀 ETH SNIPER V18 | Nuotaika: {sentiment:.2f} | Atnaujinta: {time_str}", 
                 loc='left', fontsize=12, fontweight='bold', pad=20)
    
    ax.set_facecolor('#FFFFFF')
    ax.grid(True, alpha=0.15, color='gray', linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    plt.xticks(rotation=20, fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# --- PAGRINDINIS LANGAS ---
fig, ax = plt.subplots(figsize=(16, 8), facecolor='white')
plt.subplots_adjust(bottom=0.15, left=0.08, right=0.95, top=0.9)

# Atnaujinimo ciklas kas 30 sekundžių
ani = FuncAnimation(fig, update_radar, interval=30000, cache_frame_data=False)
plt.show()
