import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(layout="wide", page_title="STEP Digital Twin Resilience", page_icon="🛡️")

st.markdown("""
<style>
    .stApp { background-color: #010203; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #05080a; border-right: 1px solid #00f2ff; }
    .strat-box { background: rgba(0, 242, 255, 0.07); border-left: 5px solid #00f2ff; padding: 20px; border-radius: 8px; margin-top: 15px; border: 1px solid rgba(0, 242, 255, 0.1); }
    .info-card { background: rgba(0, 20, 35, 0.9); border: 1px solid #00f2ff; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    .status-critical { color: #ff3232; font-weight: bold; text-shadow: 0 0 10px #ff3232; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    .legend-text { font-size: 0.85em; color: #e0e0e0; line-height: 1.4; }
</style>
""", unsafe_allow_html=True)

# --- 2. HUB DE CONTRÔLE (SIDEBAR) ---
with st.sidebar:
    st.title("🛡️ RESILIENCE HUB")
    st.markdown("---")
    tab = st.radio("SÉLECTIONNER VUE", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    
    st.subheader("📡 Paramètres Climatiques")
    alea = st.selectbox("Type d'Aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
    rcp = st.select_slider("Trajectoire RCP", options=["2.6", "4.5", "8.5"], value="8.5")
    horizon = st.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"], value="2050")
    
    st.divider()
    st.subheader("🛠️ Stratégies d'Adaptation")
    cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
    horiz_strat = st.select_slider("Échéance", options=["Court Terme", "Moyen Terme", "Long Terme"])
    
    mode_cine = st.checkbox("🎬 Rotation Cinématique")

    # Calcul du Risque Global (Score 0-10)
    risk_val = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (6 if horizon == "2050" else 9))
    if rcp == "8.5" and alea != "Hors Crise": risk_val = min(10, risk_val + 1)

# --- 3. BASE DE DONNÉES DES STRATÉGIES ---
strat_db = {
    "Physique": {
        "Court Terme": "**Batardeaux amovibles & Étanchéité.** Installation de barrières rapides sur les seuils des bâtiments critiques. *Objectif : Empêcher l'intrusion d'eau lors de crues soudaines.*",
        "Moyen Terme": "**Surélévation des Actifs.** Rehaussement des armoires électriques et pompes de +1.2m sur socles béton. *Objectif : Maintenir le fonctionnement même en cas de submersion partielle du site.*",
        "Long Terme": "**Digue de Protection Périmétrale.** Construction d'un mur de protection étanche (muret ou digue) autour de l'enceinte. *Objectif : Protection totale contre le scénario RCP 8.5 horizon 2100.*"
    },
    "Systémique": {
        "Court Terme": "**Modes Dégradés & Délestage.** Programmation des automates pour isoler les secteurs secondaires et sauver la file de traitement principale. *Objectif : Éviter la paralysie totale.*",
        "Moyen Terme": "**Autonomie Énergétique (Micro-grid).** Panneaux photovoltaïques et batteries pour assurer 24h d'autonomie en cas de coupure réseau. *Objectif : Résilience face aux pannes d'infrastructure externe.*",
        "Long Terme": "**Modularité Hydraulique.** Refonte du réseau pour permettre le 'bypass' de n'importe quel bassin endommagé. *Objectif : Flexibilité totale du process face aux aléas.*"
    },
    "Gouvernance": {
        "Court Terme": "**Plans d'Urgence & Audit.** Révision des contrats d'astreinte et des procédures de sécurité. *Objectif : Réaction humaine optimisée en moins de 2h.*",
        "Moyen Terme": "**Alerte Prédictive IoT.** Déploiement de capteurs de niveau connectés en amont de la rivière avec IA prédictive. *Objectif : Anticiper la crise 12h avant l'impact.*",
        "Long Terme": "**Relocalisation Stratégique.** Déplacement des équipements les plus sensibles (HUB Energie) vers des zones topographiques hautes. *Objectif : Zéro risque résiduel.*"
    },
    "R&D": {
        "Court Terme": "**Jumeau Numérique de Crise.** Modélisation hydraulique 3D pour tester les points de rupture virtuellement. *Objectif : Optimiser les investissements de protection.*",
        "Moyen Terme": "**Bio-procédés Thermorésistants.** Recherche sur des bactéries épuratrices capables de supporter les chocs thermiques des sécheresses. *Objectif : Maintenir la qualité de l'eau rejetée.*",
        "Long Terme": "**Matériaux Auto-Réparateurs.** Bétons innovants pour les bassins résistant aux cycles de fissuration sécheresse/gel. *Objectif : Allonger la durée de vie de l'infra de 50 ans.*"
    }
}

# --- 4. MOTEUR DE RENDU 3D ---
def create_step_view(risk_score, angle=1.0):
    fig = go.Figure()

    def get_style(vulnerabilite):
        if alea == "Hors Crise": return "#00f2ff", "rgba(0, 242, 255, 0.2)"
        impact = min(10, vulnerabilite + risk_score)
        if impact < 7: return "#00ff64", "rgba(0, 255, 100, 0.3)"
        if impact < 11: return "#ffc800", "rgba(255, 200, 0, 0.4)"
        return "#ff3232", "rgba(255, 50, 50, 0.5)"

    def add_asset(x, y, z, dx, dy, dz, r, shape_type, vulne, name):
        c_line, c_fill = get_style(vulne)
        if shape_type in ["tank", "tower"]:
            theta = np.linspace(0, 2*np.pi, 32)
            fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), 
                y=np.outer(y+r*np.sin(theta), np.ones(2)), z=np.outer(np.ones(32), [z, z+dz]),
                colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.6, name=name))
            fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(32, z+dz), 
                mode='lines', line=dict(color=c_line, width=3), showlegend=False))
        elif shape_type == "block":
            fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x]*2, y=[y, y, y+dy, y+dy]*2, z=[z]*4+[z+dz]*4,
                color=c_fill, opacity=0.6, i=[7,0,0,0,4,4,6,6], j=[3,4,1,2,5,6,5,2], k=[0,7,2,3,6,7,1,1], name=name))
            edges = [[0,1,2,3,0], [4,5,6,7,4], [0,4], [1,5], [2,6], [3,7]]
            for s in edges:
                fig.add_trace(go.Scatter3d(x=[[x,x+dx,x+dx,x,x,x+dx,x+dx,x][i] for i in s],
                    y=[[y,y,y+dy,y+dy,y,y,y+dy,y+dy][i] for i in s], z=[[z,z,z,z,z+dz,z+dz,z+dz,z+dz][i] for i in s],
                    mode='lines', line=dict(color=c_line, width=2), showlegend=False))

    # Routes de connexion
    route_col = "rgba(100, 100, 100, 0.4)"
    fig.add_trace(go.Scatter3d(x=[-8, 12], y=[0, 0], z=[-0.02, -0.02], mode='lines', line=dict(color=route_col, width=15), showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[-8, 8], z=[-0.02, -0.02], mode='lines', line=dict(color=route_col, width=15), showlegend=False))

    # Implantation de la STEP (11 Structures)
    add_asset(-6, -4, 0, 3, 2, 1.2, 0, "block", 5, "Dégrillage")
    add_asset(-3, -4, 0, 2, 2, 0.8, 0, "block", 4, "Dessablage")
    add_asset(-5, 4, 0, 0, 0, 1.0, 2.8, "tank", 2, "Décanteur Primaire")
    add_asset(2, 4, 0, 6, 3, 1.5, 0, "block", 3, "Bassin Aération 1")
    add_asset(2, 7.5, 0, 6, 3, 1.5, 0, "block", 3, "Bassin Aération 2")
    add_asset(8, -4, 0, 0, 0, 1.0, 3.2, "tank", 2, "Clarificateur Final")
    add_asset(-2, -6, 0, 0, 0, 5, 1.8, "tower", 4, "Digesteur Biogaz")
    add_asset(4, -6, 0, 2, 2, 4, 0.8, "tower", 6, "Silo à Boues")
    add_asset(0, 0.5, -1.2, 2.5, 2.5, 2, 0, "block", 9, "HUB Énergie & SCADA")
    add_asset(4, 0.5, 0, 2, 2, 1.5, 0, "block", 7, "Traitement des Boues")
    add_asset(-7, 0.5, 0, 2, 3, 2, 0, "block", 4, "Administration")

    # Simulation de l'eau (Inondation)
    if alea == "Inondation Majeure" and risk_val > 0:
        z_water = -0.8 + (risk_val * 0.15)
        fig.add_trace(go.Mesh3d(x=[-10, 15, 15, -10], y=[-10, -10, 10, 10], z=[z_water]*4, color="rgba(0, 120, 255, 0.3)", opacity=0.4))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
        camera=dict(eye=dict(x=1.8*np.cos(angle), y=1.8*np.sin(angle), z=1.2)), aspectratio=dict(x=1.5, y=1, z=0.4)),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), height=700)
    return fig

# --- 5. LOGIQUE D'AFFICHAGE PRINCIPAL ---
if tab == "🖥️ Simulation 3D":
    col_vis, col_data = st.columns([2.5, 1])
    
    with col_vis:
        st.header(f"💠 Digital Twin : {alea} (RCP {rcp})")
        
        # Gestion de l'animation
        if mode_cine:
            placeholder = st.empty()
            for i in range(60):
                placeholder.plotly_chart(create_step_view(risk_val, angle=i*0.1), use_container_width=True, key=f"anim_{i}")
                time.sleep(0.05)
        else:
            st.plotly_chart(create_step_view(risk_val), use_container_width=True)
        
        # ZONE STRATÉGIE (DYNAMIQUE)
        st.markdown(f"### 🛡️ Plan d'Adaptation : {cat_strat}")
        desc_strat = strat_db[cat_strat][horiz_strat]
        st.markdown(f"""<div class="strat-box">
            <h4 style='margin-top:0; color:#00f2ff;'>{horiz_strat}</h4>
            <p style='font-size:1.1em;'>{desc_strat}</p>
        </div>""", unsafe_allow_html=True)
        
        # LÉGENDE DES FORMES
        st.markdown("---")
        l1, l2, l3 = st.columns(3)
        l1.markdown("<p class='legend-text'>🔷 <b>Cylindres Larges :</b> Décanteurs et Clarificateurs (Process Physique)</p>", unsafe_allow_html=True)
        l2.markdown("<p class='legend-text'>🟩 <b>Blocs Longs :</b> Bassins d'Aération (Process Biologique)</p>", unsafe_allow_html=True)
        l3.markdown("<p class='legend-text'>🟥 <b>Bloc Enterré :</b> HUB SCADA / Énergie (Point de Rupture)</p>", unsafe_allow_html=True)

    with col_data:
        st.subheader("📊 Diagnostic de Crise")
        paralysie = (risk_val * 15) if alea != "Hors Crise" else 0
        pertes = risk_val * 2.8
        
        statut = "OPTIMAL" if paralysie == 0 else ("CRITIQUE" if paralysie > 50 else "DÉGRADÉ")
        color_stat = "#00ff64" if statut == "OPTIMAL" else ("#ffc800" if statut == "DÉGRADÉ" else "#ff3232")
        
        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7; margin:0;">ÉTIOLOGIE DU SYSTÈME</p>
            <h2 style="color:{color_stat}; margin:0;" class="{'status-critical' if statut=='CRITIQUE' else ''}">{statut}</h2>
        </div>
        <div class="info-card">
            <p style="opacity:0.7; margin:0;">ARRÊT DE SERVICE</p>
            <h2 style="margin:0;">{paralysie} Jours</h2>
        </div>
        <div class="info-card">
            <p style="opacity:0.7; margin:0;">COÛT DES DOMMAGES</p>
            <h2 style="color:#ff3232; margin:0;">-{pertes:.1f} M€</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"**Analyse :** À l'horizon {horizon}, le cumul de l'aléa et de la trajectoire RCP {rcp} engendre un stress hydraulique majeur sur le HUB SCADA situé en zone basse.")

else:
    st.header("ℹ️ Méthodologie du Jumeau Numérique")
    st.markdown("""
    Cette simulation repose sur le croisement de trois jeux de données :
    1. **Données GIEC (RCP) :** Modélisation de l'élévation du niveau des eaux et des épisodes de sécheresse.
    2. **Courbes de Fragilité :** Chaque bâtiment possède un seuil de rupture (ex: immersion > 0.5m pour l'électronique).
    3. **Indice de Résilience :** Calculé en fonction de la stratégie d'adaptation sélectionnée.
    """)
    st.latex(r"Indice\ de\ Rupture = \frac{Intensité\ Aléa \times Vulnérabilité\ Bâti}{Efficacité\ Stratégie}")
    
    
    
    st.table({
        "Composant": ["Poste Électrique", "Clarificateurs", "Digesteurs", "Réseau Tuyauterie"],
        "Sensibilité": ["Ultra-Haute", "Faible", "Moyenne", "Moyenne"],
        "Seuil Critique (Eau)": ["-0.5 m", "+1.2 m", "+2.0 m", "+0.8 m"]
    })
