import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="STEP Resilience Master", page_icon="🛡️")

st.markdown("""
<style>
    .stApp { background-color: #010203; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #05080a; border-right: 1px solid #00f2ff; }
    .strat-box { background: rgba(0, 242, 255, 0.07); border-left: 5px solid #00f2ff; padding: 15px; border-radius: 8px; margin-top: 10px; }
    .info-card { background: rgba(0, 20, 35, 0.9); border: 1px solid #00f2ff; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .legend-icon { display: inline-block; width: 12px; height: 12px; margin-right: 8px; border: 1px solid #00f2ff; }
    .status-critical { color: #ff3232; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

# --- 2. HUB DE CONTRÔLE ---
with st.sidebar:
    st.title("🛡️ RESILIENCE HUB")
    tab = st.radio("VUE", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    st.divider()
    alea = st.selectbox("Aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
    rcp = st.select_slider("Trajectoire RCP", options=["2.6", "4.5", "8.5"], value="8.5")
    horizon = st.select_slider("Horizon", options=["Actuel", "2050", "2100"], value="2050")
    st.divider()
    cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
    horiz_strat = st.select_slider("Échéance", options=["Court Terme", "Moyen Terme", "Long Terme"])
    mode_cine = st.checkbox("🎬 Rotation Automatique")

    # Score d'intensité de l'aléa (0 à 10)
    intensite = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (7 if horizon == "2050" else 10))
    if rcp == "8.5" and alea != "Hors Crise": intensite = min(10, intensite + 1)

# --- 3. MOTEUR 3D DYNAMIQUE ---
def create_step_view(risk_score, angle=1.0):
    fig = go.Figure()

    # Calcul dynamique de la couleur par bâtiment
    def get_dynamic_color(vulnerabilite, height_z):
        if alea == "Hors Crise": return "#00f2ff", "rgba(0, 242, 255, 0.2)"
        
        # Niveau d'eau simulé
        water_level = -0.8 + (risk_score * 0.15)
        # Si l'eau dépasse la base du bâtiment + sa tolérance
        if water_level > (height_z + (1 - vulnerabilite/10)):
            return "#ff3232", "rgba(255, 50, 50, 0.5)" # CRITIQUE
        elif water_level > height_z - 0.2:
            return "#ffc800", "rgba(255, 200, 0, 0.4)" # ALERTE
        return "#00ff64", "rgba(0, 255, 100, 0.3)"    # OK

    def add_asset(x, y, z, dx, dy, dz, r, shape_type, vulne, name):
        c_line, c_fill = get_dynamic_color(vulne, z)
        if shape_type in ["tank", "tower"]:
            theta = np.linspace(0, 2*np.pi, 32)
            fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), y=np.outer(y+r*np.sin(theta), np.ones(2)),
                z=np.outer(np.ones(32), [z, z+dz]), colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.6))
            fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(32, z+dz), mode='lines', line=dict(color=c_line, width=3), showlegend=False))
        elif shape_type == "block":
            fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x]*2, y=[y, y, y+dy, y+dy]*2, z=[z]*4+[z+dz]*4, color=c_fill, opacity=0.6, i=[7,0,0,0,4,4,6,6], j=[3,4,1,2,5,6,5,2], k=[0,7,2,3,6,7,1,1]))
            edges = [[0,1,2,3,0], [4,5,6,7,4], [0,4], [1,5], [2,6], [3,7]]
            for s in edges:
                fig.add_trace(go.Scatter3d(x=[[x,x+dx,x+dx,x,x,x+dx,x+dx,x][i] for i in s], y=[[y,y,y+dy,y+dy,y,y,y+dy,y+dy][i] for i in s], z=[[z,z,z,z,z+dz,z+dz,z+dz,z+dz][i] for i in s], mode='lines', line=dict(color=c_line, width=2), showlegend=False))

    # Infrastructure
    add_asset(-6, -4, 0, 3, 2, 1.2, 0, "block", 5, "Prétraitement")
    add_asset(-5, 4, 0, 0, 0, 1.0, 2.5, "tank", 2, "Décanteur")
    add_asset(2, 4, 0, 6, 3, 1.5, 0, "block", 3, "Bassin Aération")
    add_asset(8, -4, 0, 0, 0, 1.0, 3.0, "tank", 2, "Clarificateur")
    add_asset(-1, -6, 0, 0, 0, 5, 1.8, "tower", 4, "Digesteur")
    add_asset(0, 0.5, -1.2, 2.5, 2.5, 2, 0, "block", 9, "HUB SCADA") # Très vulnérable (z bas)

    if alea == "Inondation Majeure" and intensite > 0:
        z_w = -0.8 + (intensite * 0.15)
        fig.add_trace(go.Mesh3d(x=[-10, 15, 15, -10], y=[-10, -10, 10, 10], z=[z_w]*4, color="rgba(0, 120, 255, 0.3)", opacity=0.4))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=1.8*np.cos(angle), y=1.8*np.sin(angle), z=1.2))), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), height=600)
    return fig

# --- 4. AFFICHAGE PRINCIPAL ---
if tab == "🖥️ Simulation 3D":
    col_v, col_k = st.columns([2.5, 1])
    with col_v:
        st.header(f"💠 Digital Twin : {alea}")
        st.plotly_chart(create_step_view(intensite), use_container_width=True)
        
        # LÉGENDE DYNAMIQUE AVEC FORMES
        st.markdown("### 🗺️ Guide des Infrastructures")
        l1, l2, l3 = st.columns(3)
        l1.markdown('<div class="legend-icon" style="border-radius:50%"></div> **Cylindre :** Décanteur / Clarificateur (Sédimentation)', unsafe_allow_html=True)
        l2.markdown('<div class="legend-icon"></div> **Bloc Long :** Bassins Bio (Traitement Bactérien)', unsafe_allow_html=True)
        l3.markdown('<div class="legend-icon" style="background:#ff3232; border:none;"></div> **Bloc Enterré :** HUB Énergie (Point de Rupture)', unsafe_allow_html=True)

    with col_k:
        st.subheader("📊 Diagnostic")
        paralysie = (intensite * 18) if alea != "Hors Crise" else 0
        p_color = "#ff3232" if paralysie > 60 else "#ffc800"
        st.markdown(f'<div class="info-card">ARRÊT ESTIMÉ : <span style="color:{p_color}; font-size:1.5em; font-weight:bold;">{paralysie} Jours</span></div>', unsafe_allow_html=True)
        st.metric("Dommages Financiers", f"{intensite * 3.2:.1f} M€", delta="-12% vs sans adaptation", delta_color="normal")
        
        st.markdown("### 🛠️ Stratégie active")
        desc_db = {"Physique": "Protection matérielle", "Systémique": "Logique réseau", "Gouvernance": "Humain/Assurance", "R&D": "Innovation"}
        st.info(f"**{cat_strat} ({horiz_strat})**")
        st.caption("Cliquez sur 'Méthodologie' pour le détail des calculs.")

else:
    st.header("ℹ️ Méthodologie et Modèle Économique")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("⏱️ Calcul de la Paralysie")
        st.write("La durée d'indisponibilité $T_p$ est modélisée par la somme des temps de réaction, de décontamination et de remise en service technique :")
        st.latex(r"T_p = D_{alerte} + \sum (S_{bâti} \times K_{nettoyage}) + T_{recap}")
        st.markdown("""
        * **Décontamination :** 5 à 15 jours selon la turbidité de l'eau.
        * **Séchage Électrique :** 10 jours incompressibles pour les armoires SCADA.
        * **Réamorçage Bio :** 15 à 20 jours pour stabiliser la biomasse bactérienne.
        """)

    with col_m2:
        st.subheader("💶 Calcul des Dommages")
        st.write("Le coût $C_d$ inclut les dommages directs et les pénalités de rejet environnemental :")
        st.latex(r"C_d = \sum (Valeur_{actif} \times \%Dégâts) + (T_p \times Pénalité_{jour})")
        
    st.divider()
    st.subheader("📉 Référentiel des Coûts (Estimations M€)")
    st.table({
        "Échéance": ["Court Terme (Barrières)", "Moyen Terme (Rehausse)", "Long Terme (Digue/R&D)"],
        "Coût Investissement": ["0.5 - 1.2 M€", "3.0 - 7.5 M€", "15.0 - 45.0 M€"],
        "Réduction Risque": ["-15%", "-45%", "-90%"],
        "ROI Estimé": ["2 ans", "8 ans", "25 ans"]
    })
