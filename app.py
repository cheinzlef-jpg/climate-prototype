import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION ---
st.set_page_config(page_title="TCS - Stratégie Tunnel Mont-Blanc", layout="wide")

# CSS MIS À JOUR : Texte noir et lisibilité accrue
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; color: #1e293b; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    /* Correction couleur police Analyse d'Impact */
    .impact-card { 
        background-color: #fff1f2; 
        padding: 15px; 
        border-left: 5px solid #e11d48; 
        border-radius: 4px; 
        margin-bottom: 10px; 
        color: #000000 !important; /* Force le noir */
        font-weight: 500;
    }
    .impact-card b { color: #991b1b; font-weight: 800; }
    h1, h2, h3 { color: #0f172a; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ The Climate Standards | Terminal de Résilience")
st.markdown("### Analyse Prédictive de Niveau 3 : Tunnel du Mont-Blanc (OIV)")

# --- SIDEBAR ---
st.sidebar.header("🎛️ Paramètres de Simulation")
horizon = st.sidebar.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"])
alea = st.sidebar.selectbox("Aléa Climatique", ["Inondation / Crue", "Sécheresse / Permafrost", "Glissement de terrain"])
intensite = st.sidebar.slider("Sévérité du scénario (RCP 8.5)", 1, 5, 2)

# --- LOGIQUE D'IMPACT ---
aggravation = {"Actuel": 1.0, "2050": 1.5, "2100": 2.2}
score_final = intensite * aggravation[horizon]

data = {
    'Section': ['Portail France', 'Galerie Tech 1', 'Cœur du Massif', 'Galerie Tech 2', 'Portail Italie'],
    'Lat': [45.903, 45.885, 45.860, 45.845, 45.832],
    'Lon': [6.861, 6.900, 6.940, 6.980, 7.015],
    'Vulnerabilité': [0.8, 0.5, 0.3, 0.4, 0.9]
}
df = pd.DataFrame(data)

def get_risk_status(vuln, score):
    res = vuln * score
    if res > 1.3: return "🔴 RUPTURE CRITIQUE", "red"
    if res > 0.7: return "🟠 DÉGRADATION MAJEURE", "orange"
    return "🟢 OPÉRATIONNEL", "green"

df[['Statut', 'Color']] = df.apply(lambda r: pd.Series(get_risk_status(r['Vulnerabilité'], score_final)), axis=1)

# --- AFFICHAGE PRINCIPAL ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown(f"#### 🌍 Cartographie des Risques - Horizon {horizon}")
    m = folium.Map(location=[45.86, 6.94], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['Lat'], row['Lon']],
            icon=folium.Icon(color=row['Color'], icon='warning', prefix='fa'),
            popup=row['Section']
        ).add_to(m)
    st_folium(m, width="100%", height=450)

with col2:
    st.markdown("#### ⚠️ Analyse d'Impact Opérationnel")
    
    if score_final < 1.1:
        st.success("Trafic fluide. Aucune alerte SCADA détectée.")
    elif score_final < 2.8:
        st.markdown('<div class="impact-card"><b>Trafic interrompu :</b> Circulation alternée obligatoire. Capacité -50%.</div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card"><b>Sécurité :</b> Tunnel de secours sous surveillance (risque infiltration).</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="impact-card"><b>ARRÊT TOTAL DU TRAFIC :</b> Risque structurel majeur. Évacuation immédiate.</div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card"><b>SÉCURITÉ CONDAMNÉE :</b> Galerie de secours inaccessible. Protocoles de crise activés.</div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card"><b>ÉCONOMIE :</b> Perte de revenus directe > 1.2M€ / jour.</div>', unsafe_allow_html=True)

    st.metric("Indice de Continuité de Service", f"{max(0, int(100 - score_final*18))}%", delta=f"-{int(score_final*3)}% vs Ref.")

st.markdown("---")

# --- STRATÉGIES ---
st.header("🛠️ Plan d'Adaptation Stratégique (Niveau 3)")
t1, t2, t3 = st.tabs(["🏗️ Génie Civil", "🔌 SCADA & Tech", "📄 Assurance & CER"])

with t1:
    st.markdown("##### Mesures Structurelles")
    st.write("• **Portails :** Surélévation des seuils d'entrée pour parer aux crues centennales.")
    st.write("• **Drainage :** Création d'une galerie de décharge de 2.5m de diamètre sous la chaussée.")
    st.write("• **Renforcement :** Bétonnage des zones de failles sensibles au dégel du permafrost.")

with t2:
    st.markdown("##### Modernisation des Systèmes")
    st.write("• **SCADA :** Déploiement de capteurs ultrasoniques pour détection précoce d'éboulis.")
    st.write("• **Énergie :** Déplacement des transformateurs dans des zones 'safe' à +1500m d'altitude.")

with t3:
    st.markdown("##### Conformité & Finance")
    st.write("• **Directive CER :** Rapport automatique certifié pour l'Autorité Nationale.")
    st.write("• **Assurance :** Preuve de réduction du risque pour renégocier les primes d'interruption de service.")
