import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(layout="wide", page_title="Industrial Resilience Command Center")

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

# --- 2. HUB DE CONTRÔLE (SIDEBAR) ---
with st.sidebar:
    st.title("🛡️ HUB RESILIENCE")
    tab = st.radio("SÉLECTION VUE", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    st.divider()
    
    if tab == "🖥️ Simulation 3D":
        st.subheader("📡 Scénario Climatique")
        alea = st.selectbox("Type d'Aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
        rcp = st.select_slider("Trajectoire RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon = st.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"], value="2050")
        
        st.divider()
        st.subheader("🛠️ Stratégies d'Adaptation")
        cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horiz_strat = st.select_slider("Échéance", options=["Court Terme", "Moyen Terme", "Long Terme"])
        
        mode_cine = st.checkbox("🎬 Rotation Cinématique")

        # Logique de calcul du risque (0-10)
        risk_val = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (6 if horizon == "2050" else 9))
        if rcp == "8.5" and alea != "Hors Crise": risk_val += 1
    else:
        risk_val = 0

# --- 3. DONNÉES MÉTIER ---
strategies = {
    "Physique": {"Court Terme": "Batardeaux amovibles.", "Moyen Terme": "Surélévation pompes.", "Long Terme": "Digue béton périmétrale."},
    "Systémique": {"Court Terme": "Protocoles délestage.", "Moyen Terme": "Micro-grid solaire.", "Long Terme": "Cycle REUT intégral."},
    "Gouvernance": {"Court Terme": "Audit assurance.", "Moyen Terme": "Alerte IoT IA.", "Long Terme": "Délocalisation stratégique."},
    "R&D": {"Court Terme": "Jumeau Numérique.", "Moyen Terme": "Matériaux auto-cicatrisants.", "Long Terme": "Bio-filtration thermique."}
}

# --- 4. MOTEUR DE RENDU 3D ---
def create_complex_view(risk_score, angle=1.0):
    fig = go.Figure()

    def get_style(vulnerabilite):
        if alea == "Hors Crise": return "#00f2ff", "rgba(0, 242, 255, 0.1)"
        total = vulnerabilite + risk_score
        if total < 6: return "#00ff64", "rgba(0, 255, 100, 0.1)"
        if total < 10: return "#ffc800", "rgba(255, 200, 0, 0.2)"
        return "#ff3232", "rgba(255, 50, 50, 0.3)"

    def add_cube(x, y, z, dx, dy, dz, vulne, name):
        c_line, c_fill = get_style(vulne)
        fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=c_fill, opacity=0.6, name=name))
        fig.add_trace(go.Scatter3d(x=[x,x+dx,x+dx,x,x], y=[y,y,y+dy,y+dy,y], z=[z+dz,z+dz,z+dz,z+dz,z+dz], mode='lines', line=dict(color=c_line, width=3), showlegend=False))

    def add_cyl(x, y, z, r, h, vulne, name):
        c_line, c_fill = get_style(vulne)
        theta = np.linspace(0, 2*np.pi, 32)
        fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), y=np.outer(y+r*np.sin(theta), np.ones(2)),
            z=np.outer(np.ones(32), [z, z+h]), colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.4))
        fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(32, z+h), mode='lines', line=dict(color=c_line, width=3), showlegend=False))

    # Architecture site industriel
    add_cyl(0, 0, 0, 1.5, 1.2, 2, "Bassin Traitement 1")
    add_cyl(4, 0, 0, 1.5, 1.2, 2, "Bassin Traitement 2")
    add_cube(1, 3, 0, 3, 2, 2, 5, "Unité de Pompage")
    add_cube(5, 4, -1, 2, 2, 0.8, 8, "Local Électrique")
    
    # Réseau tuyauterie
    fig.add_trace(go.Scatter3d(x=[0, 0, 2.5, 5], y=[0, 3, 3, 4], z=[0.6, 0.6, 0.6, 0.6], mode='lines', line=dict(color="#00f2ff", width=5), showlegend=False))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
        camera=dict(eye=dict(x=1.7*np.cos(angle), y=1.7*np.sin(angle), z=1.2))),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=650)
    return fig

# --- 5. LOGIQUE D'AFFICHAGE ---
if tab == "🖥️ Simulation 3D":
    col_v, col_k = st.columns([2.5, 1])
    
    with col_v:
        st.header(f"Digital Twin : Impact {alea}")
        if mode_cine:
            ph = st.empty()
            for i in range(120):
                ph.plotly_chart(create_complex_view(risk_val, angle=i*0.05), use_container_width=True, key=f"v_{i}")
                time.sleep(0.04)
        else:
            st.plotly_chart(create_complex_view(risk_val), use_container_width=True)
        st.info(f"**Stratégie {cat_strat} ({horiz_strat}) :** {strategies[cat_strat][horiz_strat]}")

    with col_k:
        st.subheader("📊 Diagnostic")
        paralysie = (risk_val * 20) if alea != "Hors Crise" else 0
        coût = risk_val * 3.5
        
        style = "status-ok" if paralysie == 0 else ("status-warn" if paralysie < 60 else "status-critical")
        statut = "OPTIMAL" if paralysie == 0 else ("DÉGRADÉ" if paralysie < 60 else "CRITIQUE")

        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7">ÉTAT DU SYSTÈME</p>
            <h2 class="{style}">{statut}</h2>
        </div>
        <div class="info-card">
            <p style="opacity:0.7">PARALYSIE ESTIMÉE</p>
            <span class="metric-value">{paralysie} Jours</span>
        </div>
        <div class="info-card">
            <p style="opacity:0.7">PERTES FINANCIÈRES</p>
            <span class="metric-value" style="color:#ff3232;">-{coût:.1f} M€</span>
        </div>
        """, unsafe_allow_html=True)

else:
    st.header("ℹ️ Méthodologie et Calculs")
    st.markdown("La résilience est calculée selon l'équation de risque de l'UNDRR :")
    st.latex(r"Risque = \frac{Aléa \times Vulnérabilité}{Capacité\ d'Adaptation}")
    
    st.subheader("Modèle de Coûts et Délais")
    st.markdown("""
    - **Dommages :** Basés sur les courbes de fragilité JRC.
    - **Paralysie :** Temps cumulé de décontamination, séchage et mise en conformité électrique.
    """)
    
    st.table({
        "Niveau d'Aléa": ["Faible", "Modéré", "Sévère", "Extrême"],
        "Paralysie (j)": ["5-15", "15-45", "45-90", "90-180"],
        "Coût Moyen (M€)": ["0.5", "4.2", "12.5", "28.0"]
    })
