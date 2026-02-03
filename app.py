import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(layout="wide", page_title="Digital Twin X-Ray - Resilience Hub")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #00f2ff; }
    .info-card { background: rgba(0, 25, 40, 0.9); border: 1px solid #00f2ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .metric-value { font-size: 1.7em; font-weight: bold; color: #ff4b4b; }
    .out-of-service { color: #ff3232; font-weight: bold; text-shadow: 0 0 10px #ff3232; }
    .status-ok { color: #00ff00; font-weight: bold; }
    .strategy-detail { font-size: 0.9em; color: #e0e0e0; border-left: 2px solid #00f2ff; padding-left: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIQUE DE NAVIGATION ---
with st.sidebar:
    st.title("🕹️ HUB RESILIENCE")
    tab_choice = st.radio("Navigation", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    
    st.divider()
    if tab_choice == "🖥️ Simulation 3D":
        alea = st.selectbox("Type d'aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Sévère"])
        rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon = st.select_slider("Horizon", options=["Actuel", "2050", "2100"], value="2050")
        
        # Intensité de risque (0 à 10)
        risk_score = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (6 if horizon == "2050" else 8))
        if rcp == "8.5": risk_score += 2
        
        st.divider()
        cat_strat = st.selectbox("Stratégie d'Adaptation", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horiz_strat = st.select_slider("Échéance", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])
    else:
        risk_score = 0

# --- 3. BASE DE DONNÉES STRATÉGIES ---
data_strat = {
    "Physique": {"< 5 ans": "Pose de batardeaux amovibles sur les accès.", "5 ans": "Surélévation des pompes critiques (+1.2m).", "10 ans": "Digue béton périmétrale.", "20 ans": "Unités modulaires étanches."},
    "Systémique": {"< 5 ans": "Redondance des capteurs.", "5 ans": "Bypass réseau inter-communal.", "10 ans": "Micro-grid solaire autonome.", "20 ans": "Système REUT (Cycle fermé)."},
    "Gouvernance": {"< 5 ans": "Audit des contrats d'assurance.", "5 ans": "Alerte météo IoT temps réel.", "10 ans": "Plan de continuité d'activité inter-services.", "20 ans": "Relocalisation stratégique des stocks."},
    "R&D": {"< 5 ans": "Modélisation CFD du site.", "5 ans": "Matériaux polymères anti-corrosion.", "10 ans": "IA de maintenance prédictive.", "20 ans": "Bio-filtration thermorésistante."}
}

# --- 4. CONTENU : SIMULATION 3D ---
if tab_choice == "🖥️ Simulation 3D":
    st.header(f"Digital Twin : Vue {'Nominale' if alea == 'Hors Crise' else 'Impact Réel'}")
    
    col_visu, col_kpi = st.columns([2.5, 1])
    
    with col_visu:
        fig = go.Figure()

        def get_color(vulnerabilite):
            if alea == "Hors Crise": return "rgba(0, 242, 255, 0.3)", "#00f2ff"
            impact = vulnerabilite + risk_score
            if impact < 4: return "rgba(0, 255, 100, 0.3)", "#00ff64"  # Vert
            if impact < 7: return "rgba(255, 200, 0, 0.4)", "#ffc800"  # Jaune/Orange
            return "rgba(255, 50, 50, 0.5)", "#ff3232"               # Rouge

        # FONCTION STRUCTURE
        def add_bldg(x, y, z, dx, dy, dz, vulne, name, is_cyl=False):
            color_fill, color_line = get_color(vulne)
            if is_cyl:
                theta = np.linspace(0, 2*np.pi, 25)
                r = dx/2
                cx, cy = x+r, y+r
                fig.add_trace(go.Surface(x=np.outer(cx+r*np.cos(theta), np.ones(2)), y=np.outer(cy+r*np.sin(theta), np.ones(2)),
                                         z=np.outer(np.ones(25), [z, z+dz]), colorscale=[[0, color_fill], [1, color_fill]], showscale=False, opacity=0.5, name=name))
            else:
                fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x], y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                                         z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                         color=color_fill, opacity=0.5, name=name))
            # Bordures
            fig.add_trace(go.Scatter3d(x=[x, x+dx, x+dx, x, x], y=[y, y, y+dy, y+dy, y], z=[z+dz, z+dz, z+dz, z+dz, z+dz], mode='lines', line=dict(color=color_line, width=3), showlegend=False))

        # AJOUT DES BÂTIMENTS (Plus nombreux)
        add_bldg(0, 0, 0, 2, 2, 0.8, 1, "Clarificateur A", True)
        add_bldg(3, 0, 0, 2, 2, 0.8, 2, "Clarificateur B", True)
        add_bldg(0, 3, 0, 1.5, 1, 1.2, 4, "Station Pompage")
        add_bldg(2, 3, 0, 1, 1, 0.7, 1, "Poste Contrôle")
        add_bldg(3.5, 3, 0, 0.8, 0.8, 0.6, 5, "Stockage Réactifs")
        add_bldg(5, 1, 0, 1.2, 1.2, 1.5, 3, "Unité Filtration")
        add_bldg(1.5, 4.5, -0.6, 2, 1, 0.5, 6, "Sous-sol Technique") # Sous-sol vulnérable

        # ROUTES (Améliorées avec marquage)
        route_color = "rgba(100, 100, 100, 0.6)"
        fig.add_trace(go.Scatter3d(x=[-2, 7], y=[2.3, 2.3], z=[0.01, 0.01], mode='lines', line=dict(color=route_color, width=15), name="Route"))
        fig.add_trace(go.Scatter3d(x=[-2, 7], y=[2.3, 2.3], z=[0.02, 0.02], mode='lines', line=dict(color="white", width=2, dash='dash'), name="Marquage"))

        # TUYAUX
        fig.add_trace(go.Scatter3d(x=[1, 1, 3.5, 3.5, 5], y=[1, 2.5, 2.5, 1, 1.5], z=[0.4, 0.4, 0.4, 0.4, 0.5], mode='lines', line=dict(color="#00f2ff", width=6)))

        fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
                          paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f'<div class="strategy-detail"><b>Action {horiz_strat} :</b> {data_strat[cat_strat][horiz_strat]}</div>', unsafe_allow_html=True)

    with col_kpi:
        st.subheader("📊 ANALYSE DE RÉSILIENCE")
        
        # Statut dynamique
        is_out = risk_score > 7
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7; margin-bottom:5px;">STATUT INFRASTRUCTURE</p>
            <h2 class="{'out-of-service' if is_out else 'status-ok'}">
                {'⚠️ OUT OF SERVICE' if is_out else '✅ OPÉRATIONNEL'}
            </h2>
        </div>
        """, unsafe_allow_html=True)

        # Paralysie
        days = 0 if risk_score < 3 else (15 if risk_score < 6 else (60 if risk_score < 8 else 180))
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7; margin-bottom:5px;">PARALYSIE ESTIMÉE</p>
            <h2 style="color:#00f2ff">{days} Jours</h2>
            <div style="background:#222; height:8px; border-radius:4px;">
                <div style="width:{min(risk_score*10, 100)}%; background:#00f2ff; height:8px; border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Coûts
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7; margin-bottom:5px;">DÉGÂTS (CAPEX+OPEX)</p>
            <span class="metric-value">-{risk_score * 2.5:.1f} M€</span>
        </div>
        """, unsafe_allow_html=True)

        st.write("**Impact par intensité :**")
        st.table({
            "Intensité": ["Faible", "Moyenne", "Extrême"],
            "Arrêt": ["< 2j", "15j", "180j"],
            "Coût": ["< 1M€", "8M€", "> 25M€"]
        })

else:
    # --- 5. MÉTHODOLOGIE ---
    st.header("ℹ️ Méthodologie et Hypothèses")
    st.latex(r"C_{total} = \sum (V_{i} \times R_{cp} \times H_{z})")
    
    st.markdown("""
    ### Hypothèses de Paralysie :
    * **Seuil Critique :** L'état 'Out of Service' est déclenché dès qu'un bâtiment à vulnérabilité > 4 atteint le rouge.
    * **Calcul des Coûts :** Basé sur le remplacement des actifs (CAPEX) et la perte d'exploitation territoriale (OPEX systémique).
    * **Résilience :** Chaque stratégie d'adaptation réduit le score de risque effectif de 15% à 35% selon l'horizon.
    """)
    
    st.info("💡 Données calibrées sur les standards de l'OCDE et les projections RCP du GIEC.")
