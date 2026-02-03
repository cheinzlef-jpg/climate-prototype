import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(layout="wide", page_title="STEP Resilience Master", page_icon="🛡️")

st.markdown("""
<style>
    .stApp { background-color: #010203; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #05080a; border-right: 1px solid #00f2ff; }
    .strat-box { background: rgba(0, 242, 255, 0.07); border-left: 5px solid #00f2ff; padding: 15px; border-radius: 8px; margin-top: 10px; border: 1px solid rgba(0, 242, 255, 0.1); }
    .info-card { background: rgba(0, 20, 35, 0.9); border: 1px solid #00f2ff; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .status-critical { color: #ff3232; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    .legend-item { display: flex; align-items: center; margin-bottom: 8px; font-size: 0.9em; }
    .shape-ico { width: 15px; height: 15px; margin-right: 10px; border: 1px solid #00f2ff; }
</style>
""", unsafe_allow_html=True)

# --- 2. HUB DE CONTRÔLE ---
with st.sidebar:
    st.title("🛡️ RESILIENCE HUB")
    tab = st.radio("SÉLECTION VUE", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    st.divider()
    alea = st.selectbox("Type d'Aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
    rcp = st.select_slider("Trajectoire RCP", options=["2.6", "4.5", "8.5"], value="8.5")
    horizon = st.select_slider("Horizon", options=["Actuel", "2050", "2100"], value="2050")
    st.divider()
    cat_strat = st.selectbox("Catégorie d'Adaptation", ["Physique", "Systémique", "Gouvernance", "R&D"])
    horiz_strat = st.select_slider("Échéance", options=["Court Terme", "Moyen Terme", "Long Terme"])
    mode_cine = st.checkbox("🎬 Rotation Automatique")

    # Calcul intensité (0-10)
    intensite = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (7 if horizon == "2050" else 10))
    if rcp == "8.5" and alea != "Hors Crise": intensite = min(10, intensite + 1)

# --- 3. BASE DE DONNÉES STRATÉGIES ---
strat_db = {
    "Physique": {
        "Court Terme": "**Batardeaux & Obturateurs.** Pose de barrières étanches amovibles sur les 12 accès critiques. Protection immédiate contre les crues flash.",
        "Moyen Terme": "**Rehausse Technique.** Élévation de +1.5m des moteurs et armoires de commande sur socles béton isolés. Réduit la vulnérabilité du HUB de 60%.",
        "Long Terme": "**Digue de Protection.** Ceinture étanche périmétrale avec système de pompage interne. Zéro submersion même sous scénario RCP 8.5."
    },
    "Systémique": {
        "Court Terme": "**Smart Shedding.** Algorithme d'isolation des unités non-critiques pour maintenir la survie des bactéries bio en cas de baisse de tension.",
        "Moyen Terme": "**Micro-Grid Solaire.** 2000m² de panneaux photovoltaïques avec stockage hydrogène. Autonomie de 72h en cas de coupure du réseau externe.",
        "Long Terme": "**File de Traitement Redondante.** Création d'une file de secours 'bypassable'. Permet la maintenance lourde sans arrêt de service."
    },
    "Gouvernance": {
        "Court Terme": "**Audit & Astreinte 2.0.** Révision des protocoles d'intervention d'urgence avec les services de l'État. Temps de réaction réduit à 45min.",
        "Moyen Terme": "**Alerte Prédictive IoT.** Réseau de capteurs ultrasoniques en amont du bassin versant. Anticipation des pics de crue via IA (Précision 95%).",
        "Long Terme": "**Schéma Directeur 2100.** Plan de relocalisation des zones de stockage de boues vers des plateaux hors zone inondable."
    },
    "R&D": {
        "Court Terme": "**Twin Stress-Test.** Simulation numérique (ce modèle) poussée pour identifier les 'maillons faibles' hydrauliques du site actuel.",
        "Moyen Terme": "**Bio-Sélective.** Culture de bactéries extrémophiles capables de traiter les effluents malgré une hausse de 4°C de l'eau (Sécheresse).",
        "Long Terme": "**Matériaux Auto-Cicatrisants.** Bétons intelligents pour les bassins, prévenant les fuites liées aux mouvements de terrain (cycles sécheresse)."
    }
}

# --- 4. MOTEUR 3D REPRÉSENTATION INDUSTRIELLE ---
def create_step_view(risk_score, angle=1.0):
    fig = go.Figure()

    def get_dynamic_color(vulnerabilite, height_z):
        if alea == "Hors Crise": return "#00f2ff", "rgba(0, 242, 255, 0.15)"
        water_level = -0.8 + (risk_score * 0.15)
        # Seuil de criticité : si l'eau dépasse le niveau du sol du bâti + sa tolérance
        if water_level > (height_z + (1 - vulnerabilite/10)):
            return "#ff3232", "rgba(255, 50, 50, 0.4)" # ROUGE (Immergé/HS)
        elif water_level > height_z - 0.2:
            return "#ffc800", "rgba(255, 200, 0, 0.3)" # ORANGE (Alerte)
        return "#00ff64", "rgba(0, 255, 100, 0.2)"    # VERT (Sécure)

    def add_asset(x, y, z, dx, dy, dz, r, shape_type, vulne, name):
        c_line, c_fill = get_dynamic_color(vulne, z)
        if shape_type in ["tank", "tower"]:
            theta = np.linspace(0, 2*np.pi, 32)
            fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), y=np.outer(y+r*np.sin(theta), np.ones(2)),
                z=np.outer(np.ones(32), [z, z+dz]), colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.7))
            fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(32, z+dz), mode='lines', line=dict(color=c_line, width=3), showlegend=False))
        elif shape_type == "block":
            fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x]*2, y=[y, y, y+dy, y+dy]*2, z=[z]*4+[z+dz]*4, color=c_fill, opacity=0.6, i=[7,0,0,0,4,4,6,6], j=[3,4,1,2,5,6,5,2], k=[0,7,2,3,6,7,1,1]))
            edges = [[0,1,2,3,0], [4,5,6,7,4], [0,4], [1,5], [2,6], [3,7]]
            for s in edges:
                fig.add_trace(go.Scatter3d(x=[[x,x+dx,x+dx,x,x,x+dx,x+dx,x][i] for i in s], y=[[y,y,y+dy,y+dy,y,y,y+dy,y+dy][i] for i in s], z=[[z,z,z,z,z+dz,z+dz,z+dz,z+dz][i] for i in s], mode='lines', line=dict(color=c_line, width=2), showlegend=False))

    # --- RÉSEAU ROUTIER ---
    route_c = "rgba(120, 120, 120, 0.3)"
    # Axe vertical
    fig.add_trace(go.Mesh3d(x=[-0.5, 0.5, 0.5, -0.5], y=[-8, -8, 8, 8], z=[-0.05]*4, color=route_c, opacity=0.5))
    # Axe horizontal
    fig.add_trace(go.Mesh3d(x=[-8, 12, 12, -8], y=[1, 1, 2, 2], z=[-0.06]*4, color=route_c, opacity=0.5))

    # --- STRUCTURES STEP ---
    add_asset(-5, -4, 0, 3, 2, 1.2, 0, "block", 5, "Prétraitement")
    add_asset(-4, 4, 0, 0, 0, 1.0, 2.5, "tank", 2, "Décanteur")
    add_asset(2, 4, 0, 6, 3, 1.5, 0, "block", 3, "Bassin Aération")
    add_asset(8, -4, 0, 0, 0, 1.0, 3.0, "tank", 2, "Clarificateur")
    add_asset(-1, -6, 0, 0, 0, 5, 1.8, "tower", 4, "Digesteur")
    add_asset(4, -6, 0, 2, 2, 4, 0.8, "tower", 6, "Silo")
    add_asset(0.5, 2.5, -1.2, 2.5, 2.5, 2, 0, "block", 9, "HUB SCADA") # TRÈS BAS

    # Inondation
    if alea == "Inondation Majeure" and intensite > 0:
        z_w = -0.8 + (intensite * 0.15)
        fig.add_trace(go.Mesh3d(x=[-10, 15, 15, -10], y=[-10, -10, 10, 10], z=[z_w]*4, color="rgba(0, 120, 255, 0.3)", opacity=0.4))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=1.8*np.cos(angle), y=1.8*np.sin(angle), z=1.2)), aspectratio=dict(x=1.5, y=1, z=0.4)), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), height=600)
    return fig

# --- 5. LOGIQUE D'AFFICHAGE ---
if tab == "🖥️ Simulation 3D":
    col_v, col_k = st.columns([2.5, 1])
    with col_v:
        st.header(f"💠 Digital Twin | Aléa: {alea}")
        st.plotly_chart(create_step_view(intensite), use_container_width=True)
        
        # LÉGENDE INTERFACE
        st.markdown("### 🗺️ Légende des Infrastructures")
        l1, l2, l3 = st.columns(3)
        with l1:
            st.markdown('<div class="legend-item"><div class="shape-ico" style="border-radius:50%"></div><span><b>Cylindre :</b> Décanteurs (Process Eau)</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="legend-item"><div class="shape-ico" style="background:#00ff64; border:none;"></div><span><b>Vert :</b> Intégrité Opérationnelle</span></div>', unsafe_allow_html=True)
        with l2:
            st.markdown('<div class="legend-item"><div class="shape-ico"></div><span><b>Bloc :</b> Bassins & Prétraitement</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="legend-item"><div class="shape-ico" style="background:#ffc800; border:none;"></div><span><b>Orange :</b> Seuil d\'Alerte Atteint</span></div>', unsafe_allow_html=True)
        with l3:
            st.markdown('<div class="legend-item"><div class="shape-ico" style="height:30px"></div><span><b>Tour :</b> Digesteurs & Stockage</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="legend-item"><div class="shape-ico" style="background:#ff3232; border:none;"></div><span><b>Rouge :</b> Bâtiment Submergé / HS</span></div>', unsafe_allow_html=True)

        st.markdown(f"### 🛡️ Plan d'Adaptation : {cat_strat}")
        st.markdown(f'<div class="strat-box"><b>{horiz_strat} :</b> {strat_db[cat_strat][horiz_strat]}</div>', unsafe_allow_html=True)

    with col_k:
        st.subheader("📊 Diagnostic")
        paralysie = (intensite * 18) if alea != "Hors Crise" else 0
        p_color = "#ff3232" if paralysie > 60 else "#ffc800"
        st.markdown(f'<div class="info-card">ARRÊT SERVICE : <span style="color:{p_color}; font-size:1.4em; font-weight:bold;">{paralysie} Jours</span></div>', unsafe_allow_html=True)
        st.metric("Coût Dommages", f"{intensite * 3.2:.1f} M€")
        st.metric("Population Impactée", f"{intensite * 15000} hab.")

else:
    st.header("ℹ️ Méthodologie : Calcul des Impacts")
    m1, m2 = st.columns(2)
    with m1:
        st.subheader("⏱️ Jours de Paralysie")
        st.write("Le temps d'arrêt est calculé selon la formule :")
        st.latex(r"T_{arrêt} = T_{décontamination} + T_{séchage} + T_{biomasse}")
        st.write("* **Séchage :** 12 jours incompressibles pour les équipements électriques immergés.")
        st.write("* **Biomasse :** 20 jours pour stabiliser les bactéries après un choc toxique ou thermique.")
    with m2:
        st.subheader("💰 Coût des Dommages")
        st.write("Le coût direct (Cd) combine la réparation et les amendes environnementales :")
        st.latex(r"C_d = \sum (V_{actif} \times \%dmg) + (J_{arrêt} \times P_{rejet})")
        st.write("* **Pénalité Rejet :** 15,000€ / jour de non-conformité.")

    st.divider()
    st.subheader("💹 Référentiel des Coûts d'Adaptation")
    st.table({
        "Échéance": ["Court Terme", "Moyen Terme", "Long Terme"],
        "Coût Moyen (CAPEX)": ["0.8 M€ (Équipements mobiles)", "5.5 M€ (Génie civil léger)", "25.0 M€ (Infrastructures lourdes)"],
        "Réduction Risque (%)": ["-20%", "-55%", "-92%"],
        "Justification": ["Évitement des dommages mineurs", "Protection contre crues trentennales", "Résilience face au RCP 8.5"]
    })
