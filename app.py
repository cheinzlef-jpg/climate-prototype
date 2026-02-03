import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(layout="wide", page_title="Digital Twin Resilience Pro")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 1px solid #00f2ff; }
    .info-card { background: rgba(0, 30, 50, 0.8); border: 1px solid #00f2ff; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    .metric-value { font-size: 1.8em; font-weight: bold; color: #ff4b4b; }
    .out-of-service { color: #ff3232; font-weight: bold; text-shadow: 0 0 10px #ff3232; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIQUE DE NAVIGATION ---
with st.sidebar:
    st.title("🛡️ HUB RESILIENCE")
    tab = st.radio("Navigation", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    
    if tab == "🖥️ Simulation 3D":
        st.subheader("⚠️ Scénario Climatique")
        alea = st.selectbox("Type d'aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse"])
        horizon = st.select_slider("Horizon", options=["Actuel", "2050", "2100"], value="2050")
        
        st.divider()
        st.subheader("🛠️ Stratégies d'Adaptation")
        cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horiz_strat = st.select_slider("Échéance", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])
        
        # Calcul du score de risque (0 à 10)
        risk_score = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (6 if horizon == "2050" else 9))

# --- 3. BASE DE DONNÉES STRATÉGIES ---
data_strat = {
    "Physique": {"< 5 ans": "Batardeaux amovibles.", "5 ans": "Surélévation pompes.", "10 ans": "Digue béton.", "20 ans": "Unités flottantes."},
    "Systémique": {"< 5 ans": "Protocoles délestage.", "5 ans": "Bypass réseau.", "10 ans": "Micro-grid solaire.", "20 ans": "Cycle REUT."},
    "Gouvernance": {"< 5 ans": "Audit assurance.", "5 ans": "Alerte IoT.", "10 ans": "Cellule de crise.", "20 ans": "Standards résilience."},
    "R&D": {"< 5 ans": "Jumeau numérique.", "5 ans": "Matériaux auto-cicatrisants.", "10 ans": "IA prédictive.", "20 ans": "Bio-filtration thermique."}
}

# --- 4. FONCTION DE RENDU 3D ---
def create_3d_view(risk_val):
    fig = go.Figure()

    def get_color(vulne_base):
        if alea == "Hors Crise": return "#00f2ff", "rgba(0, 242, 255, 0.1)"
        impact = vulne_base + risk_val
        if impact < 5: return "#00ff64", "rgba(0, 255, 100, 0.1)" # Vert
        if impact < 8: return "#ffc800", "rgba(255, 200, 0, 0.15)" # Orange
        return "#ff3232", "rgba(255, 50, 50, 0.2)" # Rouge

    def add_structure(x, y, z, dx, dy, dz, vulne, name, is_cyl=False):
        c_line, c_fill = get_color(vulne)
        if is_cyl:
            theta = np.linspace(0, 2*np.pi, 20)
            r = dx/2
            cx, cy = x+r, y+r
            fig.add_trace(go.Surface(x=np.outer(cx+r*np.cos(theta), np.ones(2)), y=np.outer(cy+r*np.sin(theta), np.ones(2)),
                z=np.outer(np.ones(20), [z, z+dz]), colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.4))
        else:
            fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=c_fill, opacity=0.4))
        
        # Glow Wireframe
        fig.add_trace(go.Scatter3d(x=[x,x+dx,x+dx,x,x], y=[y,y,y+dy,y+dy,y], z=[z+dz,z+dz,z+dz,z+dz,z+dz], mode='lines', line=dict(color=c_line, width=4), showlegend=False))
        
        # Orbe de santé flottante
        fig.add_trace(go.Scatter3d(x=[x+dx/2], y=[y+dy/2], z=[z+dz+0.4], mode='markers', marker=dict(size=12, color=c_line, opacity=0.8), name=f"Santé {name}"))

    # Structures
    add_structure(0, 0, 0, 1.8, 1.8, 0.8, 2, "Bassin A", True)
    add_structure(2.5, 0, 0, 1.8, 1.8, 0.8, 2, "Bassin B", True)
    add_structure(5, 0, 0, 1.8, 1.8, 0.8, 2, "Bassin C", True)
    add_structure(0, 2.5, 0, 1.5, 1.5, 1.2, 5, "Pompage")
    add_structure(2.5, 2.5, 0, 1, 1, 0.7, 1, "Contrôle")
    add_structure(4.5, 2.5, -0.7, 1.5, 1.5, 0.6, 7, "Sous-sol Elec") # Très vulnérable

    # Routes & Réseau
    fig.add_trace(go.Scatter3d(x=[-2, 8], y=[2.2, 2.2], z=[0,0], mode='lines', line=dict(color="rgba(100,100,100,0.5)", width=10), name="Route"))
    fig.add_trace(go.Scatter3d(x=[1, 1, 3, 3], y=[1, 2.5, 2.5, 3], z=[0.4, 0.4, 0.4, 0.4], mode='lines', line=dict(color="#00f2ff", width=6), name="Tuyaux"))

    # Effet Inondation
    if alea == "Inondation Majeure" and risk_val > 0:
        z_water = risk_val * 0.1
        fig.add_trace(go.Mesh3d(x=[-2, 8, 8, -2], y=[-1, -1, 5, 5], z=[z_water]*4, color="rgba(0, 150, 255, 0.4)", opacity=0.5, name="Eau"))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=600)
    return fig

# --- 5. AFFICHAGE PRINCIPAL ---
if tab == "🖥️ Simulation 3D":
    st.header(f"Digital Twin : Mode {'Analyse' if alea != 'Hors Crise' else 'Veille'}")
    
    col_v, col_k = st.columns([2.5, 1])
    
    with col_v:
        st.plotly_chart(create_3d_view(risk_score), use_container_width=True)
        st.subheader(f"🛠️ Stratégie : {cat_strat}")
        st.markdown(f"**Horizon :** {horiz_strat} | **Détail :** {data_strat[cat_strat][horiz_strat]}")

    with col_k:
        st.subheader("📊 INDICATEURS")
        is_out = risk_score > 7
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.8">STATUT</p>
            <h2 class="{'out-of-service' if is_out else ''}">{'⚠️ OUT OF SERVICE' if is_out else '✅ NOMINAL'}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        days = 0 if risk_score < 3 else (20 if risk_score < 6 else 180)
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.8">PARALYSIE ESTIMÉE</p>
            <span class="metric-value">{days} Jours</span>
            <progress value="{risk_score*10}" max="100" style="width:100%"></progress>
        </div>
        <div class="info-card">
            <p style="opacity:0.8">COÛT DÉGÂTS</p>
            <span class="metric-value">-{risk_score * 3.5:.1f} M€</span>
        </div>
        """, unsafe_allow_html=True)

        st.table({"Intensité": ["Faible", "Majeure", "Critique"], "Arrêt": ["0j", "20j", "180j"]})
else:
    st.header("ℹ️ Méthodologie")
    st.latex(r"Risque = Aléa \times Vulnérabilité")
    st.markdown("Modèle basé sur les courbes de dommages GIEC/OCDE.")
