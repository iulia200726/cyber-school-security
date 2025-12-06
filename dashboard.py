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

    st.divider()
    
    # --- RECOMANDĂRI AUTOMATE ---
    st.subheader("🛡️ Măsuri și Recomandări de Securitate")
    
    # Analizăm ce tipuri de atacuri predomină
    tipuri_atacuri = df['Tip_Atac'].unique()
    
    c_rec1, c_rec2 = st.columns([1, 2])
    
    with c_rec1:
        st.info("Sistemul analizează tiparele de atac și sugerează măsuri:")
        
    with c_rec2:
        if 'SQL Injection' in tipuri_atacuri:
            st.error("🚨 **Critic: SQL Injection Detectat!**")
            st.markdown("- **Soluție:** Folosiți 'Prepared Statements' în codul bazei de date.")
            st.markdown("- **Acțiune:** Instalați un Web Application Firewall (WAF).")
            
        if 'Malware Upload' in tipuri_atacuri:
            st.warning("☣️ **Pericol: Tentativă Upload Malware!**")
            st.markdown("- **Soluție:** Restricționați tipurile de fișiere doar la `.jpg`, `.png`, `.pdf`.")
            st.markdown("- **Acțiune:** Scanați toate fișierele încărcate cu un antivirus de server.")
            
        if 'Brute Force' in tipuri_atacuri:
            st.warning("🔑 **Alertă: Atacuri Brute Force!**")
            st.markdown("- **Soluție:** Implementați blocarea automată a IP-ului după 5 încercări (Activat deja).")
            st.markdown("- **Acțiune:** Impuneți autentificarea în 2 pași (2FA) pentru profesori.")

        if 'Scanning' in tipuri_atacuri:
            st.info("👀 **Info: Scanare porturi/rute detectată.**")
            st.markdown("- **Sfat:** Ascundeți paginile de administrare și schimbați porturile default.")

        if len(tipuri_atacuri) == 0:
            st.success("✅ Nicio vulnerabilitate critică exploatată recent. Mențineți monitorizarea.")