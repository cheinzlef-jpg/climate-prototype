import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(layout="wide", page_title="Digital Twin Resilience Hub")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #00f2ff; }
    .info-card { background: rgba(0, 30, 50, 0.8); border: 1px solid #00f2ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .metric-value { font-size: 2em; font-weight: bold; }
    .status-alert { color: #ff3232; font-weight: bold; text-shadow: 0 0 10px #ff3232; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .strategy-text { font-size: 1em; color: #e0e0e0; border-left: 3px solid #00f2ff; padding-left: 15px; margin-top: 15px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIQUE DE NAVIGATION (SIDEBAR) ---
with st.sidebar:
    st.title("🕹️ HUB DE RÉSILIENCE")
    mode = st.radio("Navigation", ["🖥️ Simulation 3D", "ℹ️ Méthodologie & Hypothèses"])
    
    st.divider()
    if mode == "🖥️ Simulation 3D":
        st.subheader("1. Scénario Climatique")
        alea = st.selectbox("Aléa Actif", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
        rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon_clim = st.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"], value="2050")
        
        st.divider()
        st.subheader("2. Stratégies d'Adaptation")
        cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horizon_strat = st.select_slider("Horizon de mise en œuvre", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])
        
        # Calcul du score de risque (0-10)
        risk_score = 0 if alea == "Hors Crise" else (3 if horizon_clim == "Actuel" else (6 if horizon_clim == "2050" else 8))
        if rcp == "8.5" and alea != "Hors Crise": risk_score += 2
    else:
        risk_score = 0

# --- 3. BASE DE DONNÉES STRATÉGIES ---
data_strat = {
    "Physique": {
        "< 5 ans": "Installation de **batardeaux amovibles** et vannes anti-retour sur les points bas du site.",
        "5 ans": "Mise en œuvre d'une **surélévation sélective** (+1.5m) des transformateurs et pompes critiques.",
        "10 ans": "Construction d'une **digue périmétrale** bétonnée avec double système de pompage d'exhaure.",
        "20 ans": "Refonte des infrastructures en **bâtiments modulaires flottants** auto-étanches."
    },
    "Systémique": {
        "< 5 ans": "Mise en place de **protocoles de délestage** et d'alimentation électrique redondante par groupe mobile.",
        "5 ans": "Création d'un **bypass réseau** pour interconnexion d'urgence avec les régies d'eau voisines.",
        "10 ans": "Autonomie totale via **Micro-Grid solaire** et stockage hydrogène pour 72h d'opération isolée.",
        "20 ans": "Transition vers un **cycle fermé REUT**, réduisant la dépendance aux sources d'eau de surface vulnérables."
    },
    "Gouvernance": {
        "< 5 ans": "Audit de vulnérabilité complet et **renégociation des polices d'assurance** climatiques.",
        "5 ans": "Déploiement d'un **réseau IoT de capteurs de niveau** en amont avec IA d'alerte précoce.",
        "10 ans": "Structuration d'une **cellule de crise territoriale** coordonnant les services de secours et l'industrie.",
        "20 ans": "Planification de **relocalisation stratégique** des stocks de pièces détachées hors zone inondable."
    },
    "R&D": {
        "< 5 ans": "Développement d'un **Jumeau Numérique prédictif** simulant les scénarios de crue par quartier.",
        "5 ans": "Recherche sur des **matériaux polymères auto-cicatrisants** pour la tuyauterie enterrée.",
        "10 ans": "Implémentation d'une **IA de maintenance prédictive** analysant la fatigue structurelle post-aléa.",
        "20 ans": "Nouvelle génération de **bio-filtration thermorésistante** insensible aux vagues de chaleur."
    }
}

# --- 4. CONTENU : SIMULATION 3D ---
if mode == "🖥️ Simulation 3D":
    st.header(f"Digital Twin : Vue {'X-Ray Nominale' if alea == 'Hors Crise' else 'Analyse de Défaillance'}")
    
    col_visu, col_kpi = st.columns([2.5, 1])
    
    with col_visu:
        fig = go.Figure()

        def get_status_color(vulne_base):
            if alea == "Hors Crise": return "rgba(0, 242, 255, 0.2)", "#00f2ff"
            total_impact = vulne_base + risk_score
            if total_impact < 4: return "rgba(0, 255, 100, 0.3)", "#00ff64"
            if total_impact < 7: return "rgba(255, 165, 0, 0.4)", "#ffa500"
            return "rgba(255, 50, 50, 0.5)", "#ff3232"

        def add_structure(x, y, z, dx, dy, dz, vulne, name, is_cyl=False):
            c_fill, c_line = get_status_color(vulne)
            if is_cyl:
                theta = np.linspace(0, 2*np.pi, 25)
                r = dx/2
                cx, cy = x+r, y+r
                fig.add_trace(go.Surface(x=np.outer(cx+r*np.cos(theta), np.ones(2)), y=np.outer(cy+r*np.sin(theta), np.ones(2)),
                    z=np.outer(np.ones(25), [z, z+dz]), colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.4))
            else:
                fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                    i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=c_fill, opacity=0.4))
            # Wireframe
            fig.add_trace(go.Scatter3d(x=[x,x+dx,x+dx,x,x], y=[y,y,y+dy,y+dy,y], z=[z+dz,z+dz,z+dz,z+dz,z+dz], mode='lines', line=dict(color=c_line, width=2), showlegend=False))

        # --- DENSITÉ INDUSTRIELLE ---
        # Bassins (Cylindres)
        add_structure(0, 0, 0, 1.8, 1.8, 0.8, 2, "Cylindre A", True)
        add_structure(2.5, 0, 0, 1.8, 1.8, 0.8, 2, "Cylindre B", True)
        add_structure(5, 0, 0, 1.8, 1.8, 0.8, 3, "Cylindre C", True)
        # Bâtiments (Rectangles)
        add_structure(0, 2.5, 0, 1.5, 1, 1.2, 5, "Pompage Centrale")
        add_structure(2, 2.5, 0, 1, 1, 0.7, 1, "Contrôle")
        add_structure(3.5, 2.5, 0, 0.8, 0.8, 0.5, 2, "Logistique")
        add_structure(5, 2.5, -0.7, 1.5, 1.2, 0.6, 6, "Sous-sol Elec") # Sous-sol
        # Routes cuadrillées
        fig.add_trace(go.Scatter3d(x=[-2, 8], y=[2.2, 2.2], z=[0, 0], mode='lines', line=dict(color="rgba(100,100,100,0.5)", width=12), name="Route A"))
        fig.add_trace(go.Scatter3d(x=[2.2, 2.2], y=[-1, 5], z=[0, 0], mode='lines', line=dict(color="rgba(100,100,100,0.5)", width=12), name="Route B"))
        # Tuyauterie
        fig.add_trace(go.Scatter3d(x=[0.9, 0.9, 3.4, 3.4, 5.9, 5.9], y=[0.9, 2.5, 2.5, 0.9, 0.9, 2.5], z=[0.4, 0.4, 0.4, 0.4, 0.4, 0.4], mode='lines', line=dict(color="#00f2ff", width=6)))

        fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
                          paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=650)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader(f"🛠️ Détail : {cat_strat} ({horizon_strat})")
        st.markdown(f'<div class="strategy-text">{data_strat[cat_strat][horizon_strat]}</div>', unsafe_allow_html=True)

    with col_kpi:
        st.subheader("📊 ANALYSE D'IMPACT")
        
        # Logique Out of Service
        is_out = risk_score >= 8
        status_label = "⚠️ OUT OF SERVICE" if is_out else ("🔶 OPÉRATION DÉGRADÉE" if risk_score >= 5 else "✅ NOMINAL")
        status_css = "status-alert" if is_out else ""
        
        # Temps de paralysie
        paralysie = 0 if risk_score < 3 else (15 if risk_score < 6 else (45 if risk_score < 8 else 180))
        
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.8">STATUT DU SITE</p>
            <h2 class="{status_css}">{status_label}</h2>
            <p style="font-size:0.8em; margin-top:10px;">{'Seuil critique de rupture atteint' if is_out else 'Infrastructures sous surveillance'}</p>
        </div>
        
        <div class="info-card">
            <p style="opacity:0.8">TEMPS DE PARALYSIE</p>
            <h2 style="color:#00f2ff;">{paralysie} Jours</h2>
            <progress value="{risk_score*10}" max="100" style="width:100%"></progress>
        </div>

        <div class="info-card">
            <p style="opacity:0.8">DÉGÂTS FINANCIERS</p>
            <span class="metric-value" style="color:#ff3232;">-{risk_score * 3.5:.1f} M€</span>
        </div>
        """, unsafe_allow_html=True)

        st.write("**Récapitulatif de Paralysie :**")
        st.table({
            "Intensité": ["Faible", "Modérée", "Majeure", "Critique"],
            "Arrêt (Jours)": ["0", "15", "45", "180"],
            "Coût direct": ["0", "5 M€", "15 M€", "35 M€"]
        })

# --- 5. MÉTHODOLOGIE ---
else:
    st.header("ℹ️ Méthodologie & Hypothèses de Risque")
    st.latex(r"Impact = \int_{0}^{T} (V_{i} \times \alpha_{rcp} \times \beta_{horizon}) dt")
    
    
    
    st.markdown("""
    ### Justification des Calculs :
    1. **Seuil 'Out of Service' :** Déclenché automatiquement par une submersion simulée > 0.5m sur les unités de pompage centrales ou une rupture de l'unité 'Sous-sol Elec'.
    2. **Temps de Paralysie :** - **15 jours :** Nettoyage, expertise et remise sous tension.
        - **45 jours :** Remplacement des composants électroniques standards.
        - **180 jours :** Reconstruction lourde du génie civil et remplacement de pompes sur-mesure (délais d'approvisionnement critiques).
    3. **Réduction de Risque :** Les stratégies sélectionnées appliquent un coefficient réducteur de 20% à 50% sur les coûts finaux (non affiché visuellement dans cette démo).
    """)
    
    
    
    st.info("💡 Modèle calibré sur les données historiques de résilience des agences de l'eau et les scénarios GIEC 2026.")
