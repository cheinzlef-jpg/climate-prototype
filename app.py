import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. SETUP UI ---
st.set_page_config(layout="wide", page_title="Digital Twin Resilience Pro")

st.markdown("""
<style>
    .stApp { background-color: #010203; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #05080a; border-right: 1px solid #00f2ff; }
    .info-card { background: rgba(0, 20, 35, 0.9); border: 1px solid #00f2ff; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    .metric-value { font-size: 2.2em; font-weight: bold; text-shadow: 0 0 10px #00f2ff; }
    .status-ok { color: #00ff64; }
    .status-warn { color: #ffc800; text-shadow: 0 0 10px #ffc800; }
    .status-critical { color: #ff3232; font-weight: bold; text-shadow: 0 0 15px #ff3232; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIQUE DE CALCUL DU RISQUE ---
with st.sidebar:
    st.title("🛡️ HUB RESILIENCE")
    alea = st.selectbox("ALÉA CLIMATIQUE", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
    rcp = st.select_slider("SCÉNARIO RCP", options=["2.6", "4.5", "8.5"], value="8.5")
    horizon = st.select_slider("HORIZON", options=["Actuel", "2050", "2100"], value="2050")
    
    # Calcul d'intensité du risque (0-10)
    intensite = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (6 if horizon == "2050" else 9))
    if rcp == "8.5": intensite += 1
    if rcp == "2.6": intensite -= 1
    intensite = max(0, min(10, intensite))

    # Calcul de paralysie (jours) cohérent
    if alea == "Hors Crise":
        paralysie = 0
    else:
        # Formule : base + facteur temps + facteur RCP
        paralysie = (intensite * 15) if intensite > 2 else 0
    
    st.divider()
    mode_cine = st.checkbox("🎬 MODE CINÉMATIQUE")

# --- 3. MOTEUR DE RENDU COHÉRENT ---
def create_xray_structure(risk_score, angle=1.0):
    fig = go.Figure()

    def get_asset_style(vulnerabilite):
        # Un bâtiment est "en danger" si (son score + risque global) est élevé
        score_final = vulnerabilite + risk_score
        if alea == "Hors Crise": return "#00f2ff", "rgba(0, 242, 255, 0.1)"
        if score_final < 6: return "#00ff64", "rgba(0, 255, 100, 0.1)"
        if score_final < 10: return "#ffc800", "rgba(255, 200, 0, 0.2)"
        return "#ff3232", "rgba(255, 50, 50, 0.3)"

    def draw_cube(x, y, z, dx, dy, dz, vulne, name):
        color, fill = get_asset_style(vulne)
        fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=fill, opacity=0.6, name=name))
        lines = [[0,1,2,3,0], [4,5,6,7,4], [0,4], [1,5], [2,6], [3,7]]
        for s in lines:
            lx = [[x,x+dx,x+dx,x,x,x+dx,x+dx,x][i] for i in s]
            ly = [[y,y,y+dy,y+dy,y,y,y+dy,y+dy][i] for i in s]
            lz = [[z,z,z,z,z+dz,z+dz,z+dz,z+dz][i] for i in s]
            fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color=color, width=3), showlegend=False))

    # Assets avec vulnérabilités variables
    draw_cube(0, 0, 0, 2, 2, 1, 2, "Stockage")
    draw_cube(3, 0, 0, 1.5, 1.5, 2, 4, "Traitement")
    draw_cube(1, 3, -0.8, 2, 2, 0.7, 8, "Énergie (Sous-sol)") # Très vulnérable

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
        camera=dict(eye=dict(x=1.6*np.cos(angle), y=1.6*np.sin(angle), z=1.2))),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=650)
    return fig

# --- 4. AFFICHAGE ET ANALYSE ---
col_v, col_k = st.columns([2.5, 1])

with col_v:
    st.header(f"💠 DIGITAL TWIN | ALÉA : {alea.upper()}")
    if mode_cine:
        ph = st.empty()
        for i in range(100):
            ph.plotly_chart(create_xray_structure(intensite, angle=i*0.06), use_container_width=True, key=f"v_{i}")
            time.sleep(0.04)
    else:
        st.plotly_chart(create_xray_structure(intensite), use_container_width=True)

with col_k:
    st.subheader("📊 DIAGNOSTIC")
    
    # Détermination du statut textuel basé sur la paralysie
    if paralysie == 0:
        statut, style = "NOMINAL", "status-ok"
    elif paralysie < 45:
        statut, style = "DÉGRADÉ", "status-warn"
    else:
        statut, style = "CRITIQUE", "status-critical"

    st.markdown(f"""
    <div class="info-card">
        <p style="opacity:0.7">STATUT OPÉRATIONNEL</p>
        <h2 class="{style}">{statut}</h2>
    </div>
    <div class="info-card">
        <p style="opacity:0.7">INDICE DE RUPTURE</p>
        <span class="metric-value" style="color:{'#ff3232' if intensite > 7 else '#00f2ff'}">{paralysie} Jours</span>
        <br><small>Temps estimé de remise en service</small>
    </div>
    """, unsafe_allow_html=True)

    st.table({"Scénario": ["Actuel", "2050 (RCP 8.5)", "2100 (RCP 8.5)"], 
              "Impact": ["Faible", "Moyen", "Sévère"],
              "Risque Arrêt": ["<5j", "45j", "150j"]})
