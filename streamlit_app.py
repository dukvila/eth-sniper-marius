# --- V30 SPRENDIMŲ ANALIZATORIUS ---
tikslo_kaina = max_p  # Aukščiausias prognozės taškas
pelnas_eur = tikslo_kaina - dabartine
pelnas_proc = (pelnas_eur / dabartine) * 100

# Vertinimo logika
if momentum > 0.5 and pelnas_eur > 3.0:
    st.markdown(f"""
        <div style="background-color:#28a745; padding:20px; border-radius:15px; color:white; text-align:center;">
            <h1>🚀 VERTA PIRKTI</h1>
            <p style="font-size:20px;">Prognozuojamas pelnas: <b>+{pelnas_eur:.2f}€</b> ({pelnas_proc:.2f}%)</p>
            <p>Tikslas: <b>{tikslo_kaina:.1f}€</b> iki {l_fut[piko_idx].strftime('%H:%M')}</p>
            <small>⚠️ Riziką prisiimate patys. Sistema remiasi statistine prognoze.</small>
        </div>
    """, unsafe_allow_html=True)
elif momentum < -0.5:
    st.markdown(f"""
        <div style="background-color:#dc3545; padding:20px; border-radius:15px; color:white; text-align:center;">
            <h1>📉 NEVERTA PIRKTI / PARDUOTI</h1>
            <p>Momentumas neigiamas. Kaina krenta.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("⌛ LAUKITE palankesnio momento (per mažas pelno potencialas).")
