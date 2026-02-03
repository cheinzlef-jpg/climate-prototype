import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(layout="wide", page_title="Digital Twin X-Ray - Resilience Pro")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #00f2ff; }
    .info-card { background: rgba(0, 25, 40, 0.9); border: 1px solid #00f2ff; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 0 15px rgba(0,242,255,0.1); }
    .metric-value { font-size: 1.7em; font-weight: bold; color: #ff4b4b; }
    .out-of-service { color: #ff3232; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .strategy-detail { font-size: 0.85em; color: #e0e0e0; line-height: 1.4; border-left: 2px solid #00f2ff; padding-left: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIQUE DE NAVIGATION ---
with st.sidebar:
    st.title("🕹️ HUB RESILIENCE")
    tab_choice = st.radio("Navigation", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    
    st.divider()
    if tab_choice == "🖥️ Simulation 3D":
        st.subheader("⚠️ Aléa Climatique")
        alea = st.selectbox("Type d'aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Sévère"])
        rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon = st.select_slider("Horizon", options=["Actuel", "2050", "2100"], value="2050")
        
        # Intensité (Risk Score de 0 à 10)
        risk_score = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (6 if horizon == "2050" else 9))
        if rcp == "8.5": risk_score += 1
        
        st.divider()
        st.subheader("🛠️ Leviers d'Adaptation")
        cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horiz_strat = st.select_slider("Horizon d'implémentation", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])
    else:
        risk_score = 0

# --- 3. BASE DE DONNÉES STRATÉGIES ÉTAYÉES ---
data_strat = {
    "Physique": {
        "< 5 ans": "**Batardeaux Amovibles :** Barrières d'étanchéité à déploiement rapide sur les accès critiques.",
        "5 ans": "**Surélévation Critique :** Rehaussement de 1.5m des transformateurs et pompes de relevage.",
        "10 ans": "**Enceinte de Protection :** Digue périmétrale bétonnée avec système de pompage interne.",
        "20 ans": "**Génie Civil Résilient :** Reconstruction des bassins avec matériaux composites auto-étanches."
    },
    "Systémique": {
        "< 5 ans": "**Backup Électrique :** Groupes électrogènes mobiles et redondance des automates.",
        "5 ans": "**Maillage Territorial :** Bypass permettant de dévier le flux vers une station voisine.",
        "10 ans": "**Micro-Grid local :** Autonomie totale via mix solaire/hydrogène en cas de coupure réseau.",
        "20 ans": "**Station Circulaire :** Cycle fermé sans rejet extérieur, insensible aux crues de surface."
    },
    "Gouvernance": {
        "< 5 ans": "**Audit de Risque :** Mise à jour annuelle des plans de continuité d'activité (PCA).",
        "5 ans": "**IoT Predictive :** Capteurs de niveau d'eau en amont liés à une IA d'alerte précoce.",
        "10 ans": "**Gestion de Crise :** Cellule de pilotage temps-réel avec les services de l'État.",
        "20 ans": "**Zonage Adaptatif :** Sanctuarisation des zones d'expansion de crue hors périmètre industriel."
    },
    "R&D": {
        "< 5 ans": "**Twin Hydraulique :** Simulation CFD pour prédire la submersion exacte du site.",
        "5 ans": "**Revêtements Nanotech :** Peintures anti-corrosion ultra-résistantes aux eaux saumâtres.",
        "10 ans": "**Algorithme de Charge :** IA optimisant le débit en fonction des prévisions pluviométriques.",
        "20 ans": "**Bio-Ingénierie :** Bactéries de traitement résistantes aux chocs thermiques extrêmes."
    }
}

# --- 4. CONTENU CONDITIONNEL : SIMULATION ---
if tab_choice == "🖥️ Simulation 3D":
    st.header(f"Digital Twin : Vue {'Nominale' if alea == 'Hors Crise' else 'Analyse d\'Impact'}")
    
    col_visu, col_kpi = st.columns([2.5, 1])
    
    with col_visu:
        # --- MODÉLISATION 3D COMPLEXE ---
        fig = go.Figure()
        main_color = "rgba(0, 242, 255, 0.2)" if risk_score < 4 else ("rgba(255, 200, 0, 0.4)" if risk_score < 7 else "rgba(255, 50, 50, 0.5)")
        line_color = "#00f2ff" if risk_score < 4 else ("#ffc800" if risk_score < 7 else "#ff3232")

        def add_struct(x, y, z, dx, dy, dz, name, is_cyl=False):
            if is_cyl:
                # Cylindre (Clarificateur)
                theta = np.linspace(0, 2*np.pi, 20)
                r = dx/2
                cx, cy = x+r, y+r
                fig.add_trace(go.Surface(x=np.outer(cx+r*np.cos(theta), np.ones(2)), y=np.outer(cy+r*np.sin(theta), np.ones(2)),
                                         z=np.outer(np.ones(20), [z, z+dz]), colorscale=[[0, main_color], [1, main_color]], showscale=False, opacity=0.4))
            else:
                # Boîte
                fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x], y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                                         z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                         color=main_color, opacity=0.4, showscale=False))
            # Bordures X-ray
            fig.add_trace(go.Scatter3d(x=[x, x+dx, x+dx, x, x], y=[y, y, y+dy, y+dy, y], z=[z+dz, z+dz, z+dz, z+dz, z+dz], mode='lines', line=dict(color=line_color, width=2), showlegend=False))

        # Rendu des éléments (Complexe)
        add_struct(0,0,0,2,2,0.8, "Clarificateur 1", True)
        add_struct(3,0,0,2,2,0.8, "Clarificateur 2", True)
        add_struct(0,3,0,1.5,1,1.2, "Bâtiment Pompes")
        add_struct(2,3,0,1,1,0.7, "Unité Contrôle")
        add_struct(4,3,-0.6,1.2,1,0.6, "Sous-sol Elec") # SOUS-SOL
        
        # Tuyaux et Routes
        fig.add_trace(go.Scatter3d(x=[1, 1, 3.5, 3.5], y=[1, 2.5, 2.5, 3], z=[0.4, 0.4, 0.4, 0.4], mode='lines', line=dict(color=line_color, width=5)))
        fig.add_trace(go.Scatter3d(x=[-1, 6], y=[2.5, 2.5], z=[0.01, 0.01], mode='lines', line=dict(color="rgba(255,255,255,0.2)", width=8))) # Route

        fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
                          paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=550)
        st.plotly_chart(fig, use_container_width=True)
        
        # Stratégie en bas du visuel
        st.markdown(f"**Stratégie active :** {cat_strat} | **Echéance :** {horiz_strat}")
        st.markdown(f'<div class="strategy-detail">{data_strat[cat_strat][horiz_strat]}</div>', unsafe_allow_html=True)

    with col_kpi:
        st.subheader("📊 ANALYSE DE RÉSILIENCE")
        
        # Indicateur Out of Service
        is_out = risk_score > 7
        status_text = "OUT OF SERVICE" if is_out else ("DÉGRADÉ" if risk_score > 4 else "OPÉRATIONNEL")
        status_class = "out-of-service" if is_out else ""
        
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7">STATUT INFRASTRUCTURE</p>
            <h2 class="{status_class}">{status_text}</h2>
        </div>
        """)

        # Temps de paralysie fonction du risque
        paralyse_days = 0 if risk_score < 3 else (7 if risk_score < 6 else (45 if risk_score < 8 else 180))
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7">TEMPS DE PARALYSIE ESTIMÉ</p>
            <h2 style="color:#00f2ff">{paralyse_days} Jours</h2>
            <progress value="{risk_score*10}" max="100" style="width:100%"></progress>
        </div>
        """)

        # Coûts cumulés
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7">COÛTS DÉGÂTS (CAPEX + OPEX)</p>
            <span class="metric-value">-{risk_score * 2.1:.1f} M€</span>
        </div>
        """)

        # TABLEAU DE PARALYSIE (Nouveauté demandée)
        st.write("**Impact selon intensité :**")
        st.table({
            "Intensité": ["Faible", "Modérée", "Critique"],
            "Arrêt": ["0-2 j", "7-15 j", "45-180 j"],
            "Coût": ["< 1M€", "5M€", "> 15M€"]
        })

else:
    # --- 5. MÉTHODOLOGIE ---
    st.header("ℹ️ Méthodologie et Hypothèses")
    
    st.latex(r"R_{risk} = (P_{alea} \times I_{intensity}) \times V_{infra}")
    
    st.markdown("""
    ### Hypothèses de Paralysie :
    1. **Seuil d'arrêt (Out of Service) :** Fixé à une submersion des armoires de commande > 0.40m ou une rupture de l'approvisionnement électrique de 48h.
    2. **Temps de remise en service :** Inclut le nettoyage (3-5j), l'expertise assurance (7j), et le remplacement des composants (14-150j selon la chaîne d'approvisionnement).
    3. **Stratégies :** Les mesures d'adaptation appliquent un coefficient réducteur sur $V_{infra}$ (ex: -40% de dégâts avec batardeaux).
    """)
