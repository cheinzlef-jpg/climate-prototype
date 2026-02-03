import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION & STYLE NÉON ---
st.set_page_config(layout="wide", page_title="Digital Twin Industrial Hub")

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

# --- 2. SIDEBAR : PARAMÉTRAGE ---
with st.sidebar:
    st.title("🛡️ HUB RESILIENCE PRO")
    alea = st.selectbox("Aléa Climatique", ["Nominal", "Inondation Majeure", "Sécheresse Critique"])
    horizon = st.select_slider("Horizon Temporel", options=["2024", "2050", "2100"], value="2050")
    
    st.divider()
    st.subheader("🛠️ Leviers d'Adaptation")
    cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
    horiz_strat = st.select_slider("Échéance", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])
    
    risk_level = 0 if alea == "Nominal" else (3 if horizon == "2024" else (6 if horizon == "2050" else 9))

# --- 3. BASE DE DONNÉES STRATÉGIES ---
data_strat = {
    "Physique": {"< 5 ans": "Pose de batardeaux amovibles.", "5 ans": "Surélévation des armoires électriques.", "10 ans": "Digue béton périmétrale.", "20 ans": "Bâtiments sur pilotis / flottants."},
    "Systémique": {"< 5 ans": "Redondance capteurs.", "5 ans": "Maillage réseau secondaire.", "10 ans": "Micro-grid solaire.", "20 ans": "Cycle REUT intégral."},
    "Gouvernance": {"< 5 ans": "Audit de risque.", "5 ans": "IA Alerte Précoce.", "10 ans": "PCA mutualisé.", "20 ans": "Relocalisation stratégique."},
    "R&D": {"< 5 ans": "Jumeau numérique.", "5 ans": "Matériaux hydrophobes.", "10 ans": "IA prédictive.", "20 ans": "Bio-filtration thermique."}
}

# --- 4. MOTEUR DE RENDU 3D MULTI-FORMES ---
def render_industrial_complex(risk):
    fig = go.Figure()

    def get_asset_style(vulnerability):
        if alea == "Nominal": return "#00f2ff", "rgba(0, 242, 255, 0.1)"
        impact = vulnerability + risk
        if impact < 5: return "#00ff64", "rgba(0, 255, 100, 0.1)" # OK
        if impact < 8: return "#ffc800", "rgba(255, 200, 0, 0.2)" # WARNING
        return "#ff3232", "rgba(255, 50, 50, 0.3)"               # CRITICAL

    # --- OBJETS GÉOMÉTRIQUES ---
    def add_box(x, y, z, dx, dy, dz, vulne, name):
        c_line, c_fill = get_asset_style(vulne)
        fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=c_fill, opacity=0.5, name=name))
        fig.add_trace(go.Scatter3d(x=[x,x+dx,x+dx,x,x], y=[y,y,y+dy,y+dy,y], z=[z+dz,z+dz,z+dz,z+dz,z+dz], mode='lines', line=dict(color=c_line, width=3), showlegend=False))

    def add_cylinder(x, y, z, r, h, vulne, name):
        c_line, c_fill = get_asset_style(vulne)
        theta = np.linspace(0, 2*np.pi, 20)
        fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), y=np.outer(y+r*np.sin(theta), np.ones(2)),
            z=np.outer(np.ones(20), [z, z+h]), colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.5, name=name))
        fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(20, z+h), mode='lines', line=dict(color=c_line, width=3), showlegend=False))

    def add_cone(x, y, z, r, h, vulne, name):
        c_line, c_fill = get_asset_style(vulne)
        theta = np.linspace(0, 2*np.pi, 20)
        fig.add_trace(go.Mesh3d(x=np.append(x+r*np.cos(theta), x), y=np.append(y+r*np.sin(theta), y), z=np.append(np.full(20, z), z+h),
            i=np.arange(20), j=(np.arange(20)+1)%20, k=np.full(20, 20), color=c_fill, opacity=0.5, name=name))
        fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(20, z), mode='lines', line=dict(color=c_line, width=2), showlegend=False))

    # --- LAYOUT DU COMPLEXE ---
    add_cylinder(0, 0, 0, 1.5, 0.8, 2, "Bassin A")       # Cylindre
    add_cylinder(3.5, 0, 0, 1.5, 0.8, 2, "Bassin B")     # Cylindre
    add_box(-1, 3, 0, 2, 2, 1.5, 5, "Unité Pompage")     # Carré
    add_box(2, 3, 0, 1.5, 1, 0.7, 1, "Bureau")           # Rectangle
    add_cone(5, 3, 0, 1, 2.5, 3, "Tour de Refroidissement") # Cône
    add_box(2, 4.5, -0.8, 3, 1.5, 0.6, 7, "Sous-sol Elec") # Rectangle bas (VULNÉRABLE)

    # Routes & Réseaux
    fig.add_trace(go.Scatter3d(x=[-3, 8], y=[2.5, 2.5], z=[0,0], mode='lines', line=dict(color="rgba(100,100,100,0.4)", width=12), name="Route"))
    fig.add_trace(go.Scatter3d(x=[0, 0, 3, 3, 5], y=[0.8, 3, 3, 3, 3], z=[0.4, 0.4, 0.4, 0.4, 0.4], mode='lines', line=dict(color="#00f2ff", width=6), name="Réseau"))

    # Eau (Inondation)
    if alea == "Inondation Majeure" and risk > 0:
        fig.add_trace(go.Mesh3d(x=[-3, 8, 8, -3], y=[-1, -1, 6, 6], z=[risk*0.1]*4, color="rgba(0,100,255,0.4)", opacity=0.4))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=650)
    return fig

# --- 5. AFFICHAGE ---
col_v, col_k = st.columns([2.5, 1])

with col_v:
    st.header(f"Digital Twin : Vue {'Nominale' if alea == 'Nominal' else 'Analyse d\'Impact'}")
    st.plotly_chart(render_industrial_complex(risk_level), use_container_width=True)
    st.info(f"**Stratégie {cat_strat} ({horiz_strat}) :** {data_strat[cat_strat][horiz_strat]}")

with col_k:
    st.subheader("📊 INDICATEURS")
    is_out = risk_level > 7
    st.markdown(f"""
    <div class="info-card">
        <p style="opacity:0.8">STATUT</p>
        <h2 class="{'critical' if is_out else ''}">{'⚠️ OUT OF SERVICE' if is_out else '✅ OPÉRATIONNEL'}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Temps de paralysie indexé
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

    st.write("**Matrice de Paralysie :**")
    st.table({"Intensité": ["Faible", "Modérée", "Majeure", "Critique"], "Arrêt": ["0j", "15j", "45j", "180j"]})



### Ce qui a été amélioré :
1.  **Diversité Géométrique :** Le site contient désormais des **cylindres** (bassins), un **cône** (tour de refroidissement) et des **parallélépipèdes** de tailles variées.
2.  **Zonage Dynamique :** Chaque bâtiment a son propre score de vulnérabilité. Le **Sous-sol électrique** (vulné 7) devient rouge instantanément lors d'une crise, alors que les bureaux restent jaunes.
3.  **Indicateur "Out of Service" :** Le système bascule en "Out of Service" si le risque global dépasse le seuil de rupture des infrastructures critiques.
4.  **Temps de paralysie :** Intégration d'une table de correspondance réaliste (de l'arrêt simple à la reconstruction lourde de 6 mois).

Souhaites-tu que je rajoute des **étiquettes de texte flottantes** au-dessus de chaque bâtiment pour afficher leur nom directement dans la 3D ?
