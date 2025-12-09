import streamlit as st
import database as db
import plotly.express as px

st.set_page_config(page_title="Cyber Dashboard", layout="wide")
st.title("🛡️ Cyber Security Center")

# Buton Refresh
if st.button('🔄 Actualizează Datele'):
    st.rerun()

df = db.get_all_incidents()

if df.empty:
    st.info("Așteptare incidente...")
    st.write("Folosește panoul de simulare din site-ul `localhost:5000`.")
else:
    # 1. Metrici
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Incidente", len(df))
    col2.metric("Ultimul Atac", df.iloc[0]['Tip_Atac'])
    
    # Numărăm atacurile detectate de AI
    nr_ai = len(df[df['metoda_detectie'].str.contains('Machine Learning', na=False)])
    col3.metric("Detectate de AI (ML)", nr_ai)
    
    status = "CRITIC" if len(df) > 5 else "MONITORIZARE"
    col4.metric("Status Sistem", status, delta_color="inverse")

    st.divider()

    # 2. Grafice
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribuția Tipurilor de Atac")
        # FIX PIE CHART: Folosim 'Tip_Atac' și la names și la color pentru legenda corectă
        fig = px.pie(df, names='Tip_Atac', color='Tip_Atac', hole=0.4, title="Categorii de Incidente")
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("Severitate Atacuri")
        fig2 = px.bar(df, x='Tip_Atac', color='risc', title="Număr incidente per Tip și Risc")
        st.plotly_chart(fig2, use_container_width=True)

    # 3. Tabel
    st.subheader("Registru Atacuri Detaliat")
    st.dataframe(df, use_container_width=True)

    st.divider()
    
    # --- RECOMANDĂRI AUTOMATE COMPLETE ---
    st.subheader("🛡️ Măsuri și Recomandări de Securitate")
    
    # Lista cu tipurile unice detectate
    tipuri_detectate = df['Tip_Atac'].unique()
    
    # Definim un dicționar cu toate recomandările posibile
    recomandari_db = {
        'SQL Injection': {
            'titlu': "🚨 SQL Injection Detectat",
            'solutie': "Folosiți 'Prepared Statements' și validați input-ul.",
            'actiune': "Activați WAF (Web Application Firewall) reguli OWASP.",
            'tip': 'error'
        },
        'XSS Attack': {
            'titlu': "⚠️ XSS (Cross Site Scripting)",
            'solutie': "Activați header-ul 'Content-Security-Policy' (CSP).",
            'actiune': "Escapați caracterele speciale în output-ul HTML.",
            'tip': 'error'
        },
        'HTML Injection': {
            'titlu': "🔸 HTML Injection",
            'solutie': "Filtrați tag-urile HTML din formularele de input.",
            'actiune': "Verificați sursele iframe-urilor permise.",
            'tip': 'warning'
        },
        'Defacement': {
            'titlu': "🎨 Tentativă Defacement (CSS)",
            'solutie': "Blocați încărcarea stilurilor externe neautorizate.",
            'actiune': "Monitorizați integritatea fișierelor CSS.",
            'tip': 'warning'
        },
        'Malware Upload': {
            'titlu': "☣️ Malware Upload Detectat",
            'solutie': "Permiteți doar extensii sigure (.pdf, .jpg, .doc).",
            'actiune': "Scanați fișierele cu un Antivirus Server-Side.",
            'tip': 'error'
        },
        'Brute Force': {
            'titlu': "🔑 Brute Force Attack",
            'solutie': "Implementați blocarea IP-ului (Rate Limiting).",
            'actiune': "Forțați parole complexe și 2FA.",
            'tip': 'error'
        },
        'Port Scanning': {
            'titlu': "👀 Port Scanning (Recunoaștere)",
            'solutie': "Închideți porturile neutilizate din Firewall.",
            'actiune': "Ascundeți rutele administrative (/admin).",
            'tip': 'info'
        },
        'Trafic Atipic': {
            'titlu': "🤖 AI: Anomalie de Trafic",
            'solutie': "Investigați manual traficul masiv sau neobișnuit.",
            'actiune': "Izolați stația suspectă din rețea.",
            'tip': 'error'
        }
    }

    # Afișăm recomandările doar pentru ce s-a detectat
    cols = st.columns(2)
    idx = 0
    
    for atac in tipuri_detectate:
        rec = recomandari_db.get(atac)
        if rec:
            with cols[idx % 2]: # Distribuim pe 2 coloane
                if rec['tip'] == 'error':
                    st.error(f"**{rec['titlu']}**")
                elif rec['tip'] == 'warning':
                    st.warning(f"**{rec['titlu']}**")
                else:
                    st.info(f"**{rec['titlu']}**")
                
                st.markdown(f"- **Soluție:** {rec['solutie']}")
                st.markdown(f"- **Acțiune:** {rec['actiune']}")
            idx += 1

    if len(tipuri_detectate) == 0:
        st.success("✅ Sistemul este sigur momentan. Nu sunt incidente active.")