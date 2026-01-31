import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION ---
st.set_page_config(page_title="TCS - Stratégie Tunnel Mont-Blanc", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; color: #1e293b; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .impact-card { background-color: #fff1f2; padding: 15px; border-left: 5px solid #e11d48; border-radius: 4px; margin-bottom: 10px; }
    h1, h2, h3 { color: #0f172a; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ The Climate Standards | Terminal de Résilience")
st.markdown("### Analyse Prédictive de Niveau 3 : Tunnel du Mont-Blanc (OIV)")

# --- SIDEBAR : PARAMÈTRES AVANCÉS ---
st.sidebar.header("🎛️ Paramètres de Simulation")
horizon = st.sidebar.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"])
alea = st.sidebar.selectbox("Aléa Climatique", ["Inondation / Crue", "Sécheresse / Permafrost", "Glissement de terrain"])
intensite = st.sidebar.slider("Sévérité du scénario (RCP 8.5)", 1, 5, 2)

# --- LOGIQUE D'IMPACT (MATRICE TCS) ---
# Facteur d'aggravation selon l'année
aggravation = {"Actuel": 1.0, "2050": 1.4, "2100": 2.1}
score_final = intensite * aggravation[horizon]

# --- DONNÉES DES SECTIONS ---
data = {
    'Section': ['Portail France', 'Galerie Tech 1', 'Cœur du Massif', 'Galerie Tech 2', 'Portail Italie'],
    'Lat': [45.903, 45.885, 45.860, 45.845, 45.832],
    'Lon': [6.861, 6.900, 6.940, 6.980, 7.015],
    'Vulnerabilité': [0.8, 0.5, 0.3, 0.4, 0.9]
}
df = pd.DataFrame(data)

def get_risk_status(vuln, score):
    res = vuln * score
    if res > 1.2: return "🔴 RUPTURE CRITIQUE", "red"
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
    
    if score_final < 1.0:
        st.success("Aucun impact majeur détecté sur le trafic.")
    elif score_final < 2.5:
        st.markdown('<div class="impact-card"><b>Trafic interrompu :</b> Circulation alternée mise en place. Capacité réduite de 50%.</div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card"><b>Sécurité :</b> Tunnel de secours sous surveillance accrue.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="impact-card"><b>ARRÊT TOTAL DU TRAFIC :</b> Risque d\'effondrement ou submersion totale des portails.</div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card"><b>SÉCURITÉ CONDAMNÉE :</b> Galerie de secours inutilisable (asphyxie/inondation).</div>', unsafe_allow_html=True)
        st.markdown('<div class="impact-card"><b>ÉCONOMIE :</b> Perte estimée à 1.2M€ / jour de fermeture.</div>', unsafe_allow_html=True)

    st.metric("Indice de Continuité de Service", f"{max(0, int(100 - score_final*20))}%")

st.markdown("---")

# --- STRATÉGIES D'ADAPTATION DÉTAILLÉES ---
st.header("🛠️ Plan d'Adaptation Stratégique")

tabs = st.tabs(["🏗️ Génie Civil", "🔌 Systèmes SCADA & Énergie", "📉 Gestion des Flux & Assurance"])

with tabs[0]:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Mesures Prioritaires (0-2 ans)**")
        st.write("- **Blindage des Portails :** Construction de déflecteurs de crue en béton armé.")
        st.write("- **Étanchéité :** Injection de résine hydro-expansive dans les voussoirs fissurés.")
    with col_b:
        st.markdown("**Mesures Long Terme (2050)**")
        st.write("- **Réhaussement :** Modification altimétrique des plateformes d'entrée (+2.5m).")
        st.write("- **Galerie de Décharge :** Creusement d'un conduit d'évacuation des eaux torrentielles.")

with tabs[1]:
    st.write("**Résilience des systèmes critiques :**")
    st.info("💡 *L'analyse montre que le système de ventilation est le premier point de défaillance SCADA.*")
    st.write("1. **Redondance Énergie :** Groupes électrogènes déplacés en zone d'altitude (hors zone inondable).")
    st.write("2. **Capteurs IP68+ :** Remplacement de l'intégralité des capteurs de CO2 et opacité par des modèles submersibles.")
    st.write("3. **IA Prédictive :** Intégration des flux météo temps réel dans l'automate de gestion du trafic.")

with tabs[2]:
    st.write("**Optimisation de la valeur d'actif :**")
    st.write("- **Renégociation Assurancielle :** Utilisation du rapport TCS pour justifier une baisse de 15% de la prime de risque via la preuve de résilience.")
    st.write("- **Conformité Directive CER :** Génération automatique du dossier de conformité pour la préfecture.")
