import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Digital Twin - Station de Pompage")

# --- STYLE CSS (Fond noir et look HUD) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #111; }
    .metric-box { border: 1px solid #00f2ff; padding: 15px; border-radius: 10px; background: rgba(0,242,255,0.05); }
    h1, h2, h3 { color: #00f2ff !important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR : HUB DE CONTRÔLE ---
with st.sidebar:
    st.title("🕹️ HUB DE CONTRÔLE")
    st.subheader("Aléas Climatiques")
    alea = st.selectbox("Type d'aléa", ["Sécheresse", "Inondation"])
    rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"])
    horizon = st.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"])
    
    # Logique de calcul du risque (simplifiée)
    intensite = 1 if horizon == "Actuel" else (2 if horizon == "2050" else 3)
    if rcp == "8.5": intensite += 1
    
    st.divider()
    st.info("Ce hub pilote les paramètres de vulnérabilité des zones X-Ray.")

# --- LOGIQUE DE COULEURS X-RAY ---
# On définit 4 zones : Pompes, Cuves, Électrique, Filtration
def get_color(zone_sensitivity):
    score = zone_sensitivity + intensite
    if score <= 2: return "rgba(0, 255, 0, 0.3)"  # Vert
    if score == 3: return "rgba(255, 255, 0, 0.4)" # Jaune
    if score == 4: return "rgba(255, 165, 0, 0.5)" # Orange
    return "rgba(255, 0, 0, 0.6)"                  # Rouge

# Sensibilité par zone selon l'aléa
sensibilite = {"Pompes": 2, "Cuves": 1, "Elec": 3, "Filtration": 1} if alea == "Inondation" else {"Pompes": 3, "Cuves": 3, "Elec": 1, "Filtration": 2}

# --- VISUALISATION 3D X-RAY (Plotly) ---
def create_xray_factory():
    fig = go.Figure()

    # Fonction pour créer un cube (zone de l'usine)
    def add_zone(x, y, z, name, color):
        fig.add_trace(go.Mesh3d(
            x=[x, x+1, x+1, x, x, x+1, x+1, x],
            y=[y, y, y+1, y+1, y, y, y+1, y+1],
            z=[z, z, z, z, z+1, z+1, z+1, z+1],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color, name=name, opacity=0.5, showscale=False
        ))

    # Ajout des zones de l'usine
    add_zone(0, 0, 0, "Bloc Pompage", get_color(sensibilite["Pompes"]))
    add_zone(1.2, 0, 0, "Stockage Cuves", get_color(sensibilite["Cuves"]))
    add_zone(0, 1.2, 0, "Unité Électrique", get_color(sensibilite["Elec"]))
    add_zone(1.2, 1.2, 0, "Filtration", get_color(sensibilite["Filtration"]))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
        margin=dict(l=0, r=0, b=0, t=0), height=500
    )
    return fig

# --- AFFICHAGE PRINCIPAL ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(f"🏗️ Modèle X-Ray : Station de Pompage ({alea})")
    st.plotly_chart(create_xray_factory(), use_container_width=True)
    
    st.subheader("🛠️ Stratégies d'Adaptation")
    tab1, tab2, tab3 = st.tabs(["Physique", "Systémique", "Gouvernance"])
    with tab1:
        st.write("- **Matériaux** : Béton hydrofuge, surélévation des armoires électriques.")
        st.write("- **Physique** : Installation de clapets anti-retour renforcés.")
    with tab2:
        st.write("- **Approvisionnement** : Doublement des sources d'énergie (Solaire/Diesel).")
        st.write("- **Continuité** : Redondance des pompes (N+1).")
    with tab3:
        st.write("- **Gouvernance** : Contrats d'assurance paramétriques.")
        st.write("- **Réglementation** : Révision des seuils d'alerte selon RCP 8.5.")

with col_right:
    st.subheader("📊 Analyse des Impacts")
    
    # Simulation des coûts
    base_cost = intensite * 500000
    st.markdown(f"""
    <div class="metric-box">
        <p><b>Estimation des Dégâts :</b></p>
        <p>⏱️ 6 mois : {base_cost:,.0f} €</p>
        <p>⏳ 2 ans : {base_cost*2.5:,.0f} €</p>
        <p>🏗️ 5 ans : {base_cost*6:,.0f} €</p>
    </div><br>
    """, unsafe_allow_html=True)
    
    # Continuité de service
    dispo = max(0, 100 - (intensite * 20))
    st.write(f"**Continuité de service :** {dispo}%")
    st.progress(dispo / 100)
    
    # Impacts systémiques
    st.warning("⚠️ **Impacts Systémiques :**")
    st.write("- Rupture chaîne de froid (Industrie)")
    st.write("- Stress hydrique agricole")
    st.write("- Risque sanitaire (Eau potable)")
