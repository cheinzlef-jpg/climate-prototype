import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(layout="wide", page_title="Digital Twin Resilience")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 1px solid #00f2ff; }
    .info-card { background: rgba(0, 20, 30, 0.9); border: 1px solid #00f2ff; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
    .metric-value { font-size: 1.8em; font-weight: bold; color: #00f2ff; text-shadow: 0 0 10px #00f2ff; }
    .critical { color: #ff3232; text-shadow: 0 0 10px #ff3232; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR : PARAMÈTRES ---
with st.sidebar:
    st.title("🛡️ HUB RESILIENCE")
    alea = st.selectbox("Aléa Climatique", ["Nominal", "Inondation Majeure", "Sécheresse Critique"])
    horizon = st.select_slider("Horizon Temporel", options=["2024", "2050", "2100"], value="2050")
    
    st.divider()
    st.subheader("🛠️ Stratégies d'Adaptation")
    cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
    horiz_strat = st.select_slider("Échéance", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])
    
    # Intensité globale (0-10)
    risk_level = 0 if alea == "Nominal" else (3 if horizon == "2024" else (6 if horizon == "2050" else 9))

# --- 3. LOGIQUE MÉTIER ---
data_strat = {
    "Physique": {"< 5 ans": "Batardeaux amovibles.", "5 ans": "Surélévation pompes.", "10 ans": "Digue béton.", "20 ans": "Unités flottantes."},
    "Systémique": {"< 5 ans": "Redondance capteurs.", "5 ans": "Bypass réseau.", "10 ans": "Micro-grid solaire.", "20 ans": "Cycle REUT."},
    "Gouvernance": {"< 5 ans": "Audit assurance.", "5 ans": "Alerte IoT.", "10 ans": "Cellule de crise.", "20 ans": "Relocalisation."},
    "R&D": {"< 5 ans": "Jumeau numérique.", "5 ans": "Matériaux hydrophobes.", "10 ans": "IA prédictive.", "20 ans": "Bio-filtration."}
}

# --- 4. MOTEUR DE RENDU 3D ---
def render_complex(risk):
    fig = go.Figure()

    def get_style(vulnerabilite):
        if alea == "Nominal": return "#00f2ff", "rgba(0, 242, 255, 0.1)"
        impact = vulnerabilite + risk
        if impact < 5: return "#00ff64", "rgba(0, 255, 100, 0.1)" # Vert
        if impact < 8: return "#ffc800", "rgba(255, 200, 0, 0.2)" # Orange
        return "#ff3232", "rgba(255, 50, 50, 0.3)"               # Rouge

    # Forme : Boîte
    def add_box(x, y, z, dx, dy, dz, vulne, name):
        c_line, c_fill = get_style(vulne)
        fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=c_fill, opacity=0.5, name=name))
        fig.add_trace(go.Scatter3d(x=[x,x+dx,x+dx,x,x], y=[y,y,y+dy,y+dy,y], z=[z+dz,z+dz,z+dz,z+dz,z+dz], mode='lines', line=dict(color=c_line, width=2), showlegend=False))

    # Forme : Cylindre
    def add_cyl(x, y, z, r, h, vulne, name):
        c_line, c_fill = get_style(vulne)
        theta = np.linspace(0, 2*np.pi, 20)
        fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), y=np.outer(y+r*np.sin(theta), np.ones(2)),
            z=np.outer(np.ones(20), [z, z+h]), colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.5, name=name))
        fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(20, z+h), mode='lines', line=dict(color=c_line, width=2), showlegend=False))

    # Forme : Cône (Tour)
    def add_cone(x, y, z, r, h, vulne, name):
        c_line, c_fill = get_style(vulne)
        theta = np.linspace(0, 2*np.pi, 20)
        fig.add_trace(go.Mesh3d(x=np.append(x+r*np.cos(theta), x), y=np.append(y+r*np.sin(theta), y), z=np.append(np.full(20, z), z+h),
            i=np.arange(20), j=(np.arange(20)+1)%20, k=np.full(20, 20), color=c_fill, opacity=0.5, name=name))

    # --- ASSEMBLAGE DU COMPLEXE ---
    add_cyl(0, 0, 0, 1.2, 0.8, 2, "Clarificateur")
    add_cyl(3, 0, 0, 1.2, 1.5, 3, "Silo Stockage")
    add_box(-1, 2.5, 0, 2, 1.5, 1.2, 5, "Bâtiment Pompes")
    add_box(2, 2.5, 0, 1.5, 1, 0.8, 1, "Bureaux")
    add_cone(5, 2, 0, 0.8, 2.5, 3, "Tour Cooling")
    add_box(2, 4, -0.7, 3, 1.2, 0.6, 7, "Sous-sol Critique")

    # Routes
    fig.add_trace(go.Scatter3d(x=[-2, 8], y=[2, 2], z=[0,0], mode='lines', line=dict(color="rgba(100,100,100,0.5)", width=10), showlegend=False))
    # Tuyaux
    fig.add_trace(go.Scatter3d(x=[0, 0, 2], y=[0.8, 2.5, 2.5], z=[0.4, 0.4, 0.4], mode='lines', line=dict(color="#00f2ff", width=5), showlegend=False))

    # Eau
    if alea == "Inondation Majeure" and risk > 0:
        fig.add_trace(go.Mesh3d(x=[-2, 8, 8, -2], y=[-1, -1, 6, 6], z=[risk*0.08]*4, color="rgba(0,150,255,0.4)", opacity=0.4))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=600)
    return fig

# --- 5. INTERFACE ---
col_v, col_k = st.columns([2.5, 1])

with col_v:
    st.header(f"Digital Twin : {alea}")
    st.plotly_chart(render_complex(risk_level), use_container_width=True)
    st.info(f"**Stratégie {cat_strat} :** {data_strat[cat_strat][horiz_strat]}")

with col_k:
    st.subheader("📊 ANALYSE D'IMPACT")
    is_out = risk_level > 7
    st.markdown(f"""
    <div class="info-card">
        <p style="opacity:0.8">STATUT</p>
        <h2 class="{'critical' if is_out else ''}">{'⚠️ OUT OF SERVICE' if is_out else '✅ OPÉRATIONNEL'}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    paralysie = 0 if risk_level < 3 else (15 if risk_level < 6 else (45 if risk_level < 8 else 180))
    st.markdown(f"""
    <div class="info-card">
        <p style="opacity:0.8">TEMPS DE PARALYSIE</p>
        <span class="metric-value">{paralysie} Jours</span>
    </div>
    <div class="info-card">
        <p style="opacity:0.8">COÛT ESTIMÉ</p>
        <span class="metric-value">-{risk_level * 2.8:.1f} M€</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("**Impact selon l'intensité :**")
    st.table({"Aléa": ["Faible", "Modéré", "Critique"], "Arrêt": ["0j", "15j", "180j"]})
