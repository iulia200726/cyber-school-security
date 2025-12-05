import streamlit as st
import database as db
import plotly.express as px

# Configurare pagină
st.set_page_config(page_title="Cyber Dashboard", layout="wide")

st.title("🛡️ Cyber Security Center")

# --- BUTON MANUAL DE REFRESH ---
# Acum datele se încarcă doar când apeși tu pe buton sau intri pe pagină
col_btn, col_info = st.columns([1, 5])
with col_btn:
    if st.button('🔄 Actualizează Datele'):
        st.rerun()

# --- ÎNCĂRCARE DATE ---
df = db.get_all_incidents()

if df.empty:
    st.info("Așteptare incidente... Sistemul este sigur momentan.")
    st.write("Încearcă să ataci site-ul `localhost:5000` pentru a genera date!")
else:
    # 1. Metrici Principale (Top)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidente", len(df))
    
    # Calculăm ultimul tip de atac
    ultimul_atac = df.iloc[0]['Tip_Atac']
    col2.metric("Ultimul Atac Detectat", ultimul_atac)
    
    # Statusul sistemului
    status = "SUB ATAC" if len(df) > 0 else "SIGUR"
    col3.metric("Status Securitate", status, delta_color="inverse")

    st.divider()

    # 2. Grafice (Mijloc)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Tipuri de Atacuri")
        # Grafic plăcintă
        fig = px.pie(df, names='Tip_Atac', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("Zone Vulnerabile")
        # Grafic cu bare
        fig2 = px.bar(df, x='zona', color='risc', title="Unde au loc atacurile?")
        st.plotly_chart(fig2, use_container_width=True)

    # 3. Tabel Detaliat (Jos)
    st.subheader("Registru Atacuri")
    st.dataframe(df, use_container_width=True)