import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION ET STYLE NÉON ---
st.set_page_config(layout="wide", page_title="Digital Twin Resilience X-Ray")

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
    st.title("🛡️ HUB RESILIENCE")
    tab = st.radio("Navigation", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    
    st.divider()
    if tab == "🖥️ Simulation 3D":
        st.subheader("📡 Aléa & Horizon")
        alea = st.selectbox("Type d'aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
        rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon = st.select_slider("Horizon", options=["Actuel", "2050", "2100"], value="2050")
        
        st.divider()
        st.subheader("🛠️ Stratégie d'Adaptation")
        cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horiz_strat = st.select_slider("Mise en œuvre", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])

        st.divider()
st.subheader("🎬 Rendu Vidéo")
mode_cine = st.checkbox("Activer Rotation Cinématique")

        # Score de risque
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

# --- 4. FONCTIONS DE RENDU X-RAY ---
def create_xray_structure(risk_score):
    fig = go.Figure()
    
    # Palette de couleurs dynamique
    def get_color(vulnerabilite):
        if alea == "Hors Crise": return "#00f2ff", "rgba(0, 242, 255, 0.1)"
        total = vulnerabilite + risk_score
        if total < 5: return "#00ff64", "rgba(0, 255, 100, 0.05)"
        if total < 8: return "#ffc800", "rgba(255, 200, 0, 0.1)"
        return "#ff3232", "rgba(255, 50, 50, 0.2)"

    def draw_cube(x, y, z, dx, dy, dz, vulne, name):
        color, fill = get_color(vulne)
        # Faces semi-transparentes
        fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                color=fill, opacity=0.5, showscale=False, hoverinfo='name', name=name))
        # Arêtes (Wireframe)
        edges_x, edges_y, edges_z = [], [], []
        for s in [[0,1,2,3,0], [4,5,6,7,4], [0,4], [1,5], [2,6], [3,7]]:
            for i in s:
                edges_x.append([x,x+dx,x+dx,x,x,x+dx,x+dx,x][i]); edges_y.append([y,y,y+dy,y+dy,y,y,y+dy,y+dy][i]); edges_z.append([z,z,z,z,z+dz,z+dz,z+dz,z+dz][i])
            edges_x.append(None); edges_y.append(None); edges_z.append(None)
        fig.add_trace(go.Scatter3d(x=edges_x, y=edges_y, z=edges_z, mode='lines', line=dict(color=color, width=3), showlegend=False))

    def draw_cyl(x, y, z, r, h, vulne, name):
        color, fill = get_color(vulne)
        theta = np.linspace(0, 2*np.pi, 32)
        cx, cy = x+r, y+r
        # Surface
        fig.add_trace(go.Surface(x=np.outer(cx+r*np.cos(theta), np.ones(2)), y=np.outer(cy+r*np.sin(theta), np.ones(2)),
                                 z=np.outer(np.ones(32), [z, z+h]), colorscale=[[0, fill], [1, fill]], showscale=False, opacity=0.3))
        # Cercles haut/bas
        fig.add_trace(go.Scatter3d(x=cx+r*np.cos(theta), y=cy+r*np.sin(theta), z=np.full(32, z+h), mode='lines', line=dict(color=color, width=3), showlegend=False))

    # --- ARCHITECTURE DU SITE ---
    draw_cyl(0, 0, 0, 1.2, 0.8, 2, "Clarificateur 1")
    draw_cyl(3, 0, 0, 1.2, 0.8, 2, "Clarificateur 2")
    draw_cyl(6, 0, 0, 1.2, 0.8, 3, "Clarificateur 3")
    draw_cube(0, 3, 0, 2.5, 1.5, 1.5, 5, "Unité de Pompage")
    draw_cube(3.5, 3.5, 0, 1, 1, 0.8, 1, "Centre de Contrôle")
    draw_cube(5.5, 3, -0.8, 1.5, 1.5, 0.6, 7, "Sous-sol Électrique") # VULNÉRABLE
    draw_cube(7.5, 3.5, 0, 0.8, 0.8, 2.5, 2, "Cheminée / Évent")

    # ROUTES
    fig.add_trace(go.Scatter3d(x=[-2, 10], y=[2.5, 2.5], z=[0,0], mode='lines', line=dict(color="rgba(100,100,100,0.4)", width=15), showlegend=False))
    fig.add_trace(go.Scatter3d(x=[2.8, 2.8], y=[-2, 6], z=[0,0], mode='lines', line=dict(color="rgba(100,100,100,0.4)", width=15), showlegend=False))
    
    # TUYAUX NÉON
    fig.add_trace(go.Scatter3d(x=[1.2, 1.2, 4.2, 4.2, 6], y=[1.2, 3, 3, 4, 4], z=[0.5, 0.5, 0.5, 0.5, 0.5], mode='lines', line=dict(color="#00f2ff", width=6), name="Réseau Principal"))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, 
                      aspectmode='data', camera=dict(eye=dict(x=1.5, y=1.5, z=1))),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=600)
    return fig

# --- 5. AFFICHAGE PRINCIPAL ---
if tab == "🖥️ Simulation 3D":
    st.header(f"Digital Twin : Vue {'X-Ray' if alea == 'Hors Crise' else 'Alerte Système'}")
    
    col_v, col_k = st.columns([2.5, 1])
    
    with col_v:
        st.plotly_chart(create_xray_structure(risk_val), use_container_width=True)
        st.subheader(f"🛠️ Stratégie : {cat_strat} ({horiz_strat})")
        st.markdown(f'<div class="strategy-box">{data_strat[cat_strat][horiz_strat]}</div>', unsafe_allow_html=True)

    with col_k:
        st.subheader("📊 ANALYSE")
        is_out = risk_val > 7
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7">STATUT INFRASTRUCTURE</p>
            <h2 class="{'status-critical' if is_out else ''}">{'⚠️ OUT OF SERVICE' if is_out else '✅ NOMINAL'}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Temps de paralysie
        days = 0 if risk_val < 3 else (20 if risk_val < 6 else (60 if risk_val < 8 else 180))
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7">PARALYSIE ESTIMÉE</p>
            <span class="metric-value">{days} Jours</span>
            <div style="background:#222; height:10px; border-radius:5px; margin-top:10px;">
                <div style="width:{min(risk_val*10, 100)}%; background:#00f2ff; height:10px; border-radius:5px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.table({"Intensité": ["Faible", "Moyenne", "Critique"], "Arrêt": ["0j", "20j", "180j"], "Coût": ["<1M", "8M", ">20M"]})

else:
    st.header("ℹ️ Méthodologie")
    st.latex(r"R = P \times V \times E")
    st.markdown("Estimation basée sur les courbes de fragilité des infrastructures critiques (Source OCDE).")
