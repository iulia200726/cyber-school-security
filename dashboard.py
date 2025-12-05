import streamlit as st
import database as db
import plotly.express as px
import time

st.set_page_config(page_title="Cyber Dashboard", layout="wide")

st.title("🛡️ Cyber Security Center")

# --- AUTO REFRESH ---
# Adăugăm un checkbox. Dacă e bifat, dashboard-ul se reîncarcă singur.
if st.checkbox("Activează Monitorizarea Live (Auto-Refresh)", value=True):
    time.sleep(2) # Așteaptă 2 secunde
    st.rerun()    # Dă refresh la pagină

# Încărcăm datele proaspete din DB
df = db.get_all_incidents()

if df.empty:
    st.info("Așteptare incidente... Sistemul este sigur momentan.")
else:
    # Top Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidente", len(df))
    col2.metric("Ultimul Atac", df.iloc[0]['Tip_Atac'])
    col3.metric("Status", "SUB ATAC" if len(df) > 0 else "Segur")

    st.divider()

    # Grafice
    c1, c2 = st.columns(2)
    with c1:
        # Pie Chart
        fig = px.pie(df, names='Tip_Atac', title="Distribuția Atacurilor", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        # Bar Chart
        fig2 = px.bar(df, x='zona', color='risc', title="Zone Vulnerabile")
        st.plotly_chart(fig2, use_container_width=True)

    # Tabel Date
    st.subheader("Registru Atacuri (Live)")
    st.dataframe(df, use_container_width=True)