import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time # Pour les animations

# --- 1. CONFIGURATION ET STYLE NÉON ---
st.set_page_config(layout="wide", page_title="Digital Twin Pro - Visualisation Avancée")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 1px solid #00f2ff; }
    .info-card { background: rgba(0, 20, 30, 0.9); border: 1px solid #00f2ff; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 0 15px rgba(0,242,255,0.1); }
    .metric-value { font-size: 2.2em; font-weight: bold; color: #00f2ff; text-shadow: 0 0 10px #00f2ff; }
    .status-critical { color: #ff3232; font-weight: bold; text-shadow: 0 0 10px #ff3232; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .strategy-box { border-left: 3px solid #00f2ff; padding-left: 15px; margin: 15px 0; font-size: 0.95em; line-height: 1.5; color: #d0d0d0; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIQUE DE NAVIGATION ---
with st.sidebar:
    st.title("🛡️ HUB RESILIENCE PRO")
    tab = st.radio("Navigation", ["🖥️ Simulation 3D Avancée", "ℹ️ Méthodologie"])
    
    st.divider()
    if tab == "🖥️ Simulation 3D Avancée":
        st.subheader("📡 Aléa & Horizon")
        alea = st.selectbox("Type d'aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
        rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon = st.select_slider("Horizon", options=["Actuel", "2050", "2100"], value="2050")
        
        st.divider()
        st.subheader("🛠️ Stratégie d'Adaptation")
        cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horiz_strat = st.select_slider("Mise en œuvre", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])
        
        # Score de risque (0-10)
        risk_val = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (6 if horizon == "2050" else 9))
        if rcp == "8.5" and alea != "Hors Crise": risk_val += 1
    else:
        risk_val = 0

# --- 3. DONNÉES STRATÉGIES ---
data_strat = {
    "Physique": {"< 5 ans": "Batardeaux amovibles.", "5 ans": "Surélévation pompes.", "10 ans": "Digue béton.", "20 ans": "Unités flottantes."},
    "Systémique": {"< 5 ans": "Protocoles délestage.", "5 ans": "Bypass réseau.", "10 ans": "Micro-grid solaire.", "20 ans": "Cycle REUT."},
    "Gouvernance": {"< 5 ans": "Audit assurance.", "5 ans": "Alerte IoT.", "10 ans": "Cellule de crise.", "20 ans": "Standards résilience."},
    "R&D": {"< 5 ans": "Jumeau numérique.", "5 ans": "Matériaux auto-cicatrisants.", "10 ans": "IA prédictive.", "20 ans": "Bio-filtration thermique."}
}

# --- 4. FONCTIONS DE RENDU AVANCÉ ---
def create_advanced_xray_structure(risk_score, alea_type):
    fig = go.Figure()
    
    # Palette de couleurs dynamique
    def get_color(vulnerabilite):
        if alea_type == "Hors Crise": return "#00f2ff", "rgba(0, 242, 255, 0.08)", "#00ff64" # Ligne, Surface, Indicateur
        total = vulnerabilite + risk_score
        if total < 5: return "#00ff64", "rgba(0, 255, 100, 0.1)", "#00ff64"
        if total < 8: return "#ffc800", "rgba(255, 200, 0, 0.15)", "#ffc800"
        return "#ff3232", "rgba(255, 50, 50, 0.2)", "#ff3232"

    # Fonction pour dessiner un cube (avec wireframe et surface)
    def draw_cube(x, y, z, dx, dy, dz, vulne, name):
        color_line, color_fill, indicator_color = get_color(vulne)
        
        # Faces semi-transparentes
        fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                color=color_fill, opacity=0.3, showscale=False, hoverinfo='name', name=name))
        # Arêtes (Wireframe)
        edges_x, edges_y, edges_z = [], [], []
        for s in [[0,1,2,3,0], [4,5,6,7,4], [0,4], [1,5], [2,6], [3,7]]:
            for i in s:
                edges_x.append([x,x+dx,x+dx,x,x,x+dx,x+dx,x][i])
                edges_y.append([y,y,y+dy,y+dy,y,y,y+dy,y+dy][i])
                edges_z.append([z,z,z,z,z+dz,z+dz,z+dz,z+dz][i])
            edges_x.append(None); edges_y.append(None); edges_z.append(None) # Séparateur pour tracer de nouvelles lignes
        fig.add_trace(go.Scatter3d(x=edges_x, y=edges_y, z=edges_z, mode='lines', line=dict(color=color_line, width=3), showlegend=False))

        # Indicateur de santé au-dessus du bâtiment
        indicator_size = 0.2 + (total * 0.05) # Plus le risque est élevé, plus l'indicateur est gros
        fig.add_trace(go.Scatter3d(x=[x+dx/2], y=[y+dy/2], z=[z+dz+0.2],
                                   mode='markers', marker=dict(size=indicator_size*15, color=indicator_color, opacity=0.8, symbol='circle'),
                                   name=f"Indicateur {name}", hoverinfo='name'))

    # Fonction pour dessiner un cylindre (clarificateur)
    def draw_cyl(x, y, z, r, h, vulne, name):
        color_line, color_fill, indicator_color = get_color(vulne)
        theta = np.linspace(0, 2*np.pi, 32)
        cx, cy = x+r, y+r
        # Surface
        fig.add_trace(go.Surface(x=np.outer(cx+r*np.cos(theta), np.ones(2)), y=np.outer(cy+r*np.sin(theta), np.ones(2)),
                                 z=np.outer(np.ones(32), [z, z+h]), colorscale=[[0, color_fill], [1, color_fill]], showscale=False, opacity=0.3))
        # Cercles haut/bas (Wireframe)
        fig.add_trace(go.Scatter3d(x=cx+r*np.cos(theta), y=cy+r*np.sin(theta), z=np.full(32, z+h), mode='lines', line=dict(color=color_line, width=3), showlegend=False))
        fig.add_trace
