import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Digital Twin - Pumping Station")

# --- STYLE CSS (Fond sombre, textes néon, conteneurs stylisés) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #00f2ff;
        box-shadow: 2px 0 10px rgba(0, 242, 255, 0.2);
    }
    h1, h2, h3, h4, p, label, .stSlider > div > div > label, .stSelectbox label { color: #00f2ff !important; }

    /* Styles pour les conteneurs d'information */
    .info-card {
        background: rgba(0, 20, 30, 0.8);
        border: 1px solid #00f2ff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.3);
    }
    .metric-value {
        font-size: 1.8em;
        font-weight: bold;
        color: #ff4b4b; /* Rouge pour les alertes/coûts par défaut */
    }
    .status-critical { color: #ff4b4b; font-weight: bold; }
    .status-ok { color: #00ff00; font-weight: bold; }
    
    /* Boutons de navigation dans la sidebar */
    .sidebar-button {
        background-color: #003344;
        color: #00f2ff;
        border: 1px solid #00f2ff;
        padding: 10px 15px;
        border-radius: 5px;
        width: 100%;
        text-align: left;
        margin-bottom: 5px;
        cursor: pointer;
        transition: background-color 0.3s, box-shadow 0.3s;
    }
    .sidebar-button:hover {
        background-color: #005060;
        box-shadow: 0 0 8px rgba(0, 242, 255, 0.5);
    }
    .sidebar-button.active {
        background-color: #00f2ff;
        color: #050505;
        font-weight: bold;
        box-shadow: 0 0 15px #00f2ff;
    }
    
    /* Titre d'alerte central */
    .alert-title {
        color: #ff4b4b;
        font-size: 2.5em;
        font-weight: bold;
        text-shadow: 0 0 15px #ff4b4b;
        text-align: center;
        margin-bottom: 20px;
    }

</style>
""", unsafe_allow_html=True)

# --- SIDEBAR : HUB DE CONTRÔLE ET NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Digital_twin_concept_symbol.svg/1200px-Digital_twin_concept_symbol.svg.png", width=50) # Icône "Digital Twin"
    st.title("Digital Twin - Pumping Station")
    st.write("Lwpp model Twin - Alevstation") # Texte sous le titre

    st.markdown("---")
    st.subheader("Hub de Contrôle")
    
    # Boutons de navigation principaux
    if st.button(" scénarios", key="nav_scenarios", help="Gérer les scénarios d'aléas"):
        st.session_state.active_tab = "Scenarios"
    if st.button(" aléa", key="nav_alea", help="Définir le type d'aléa climatique"):
        st.session_state.active_tab = "Alea"
    if st.button(" horizon temporel", key="nav_horizon", help="Choisir l'horizon de projection"):
        st.session_state.active_tab = "Horizon"
    
    # Initialisation de l'état si non existant
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Scenarios" # Onglet par défaut

    st.markdown("---")
    
    # Contenu conditionnel de la sidebar
    if st.session_state.active_tab == "Scenarios":
        st.subheader("Scénarios")
        st.write("Type d'aléa:")
        alea = st.radio(" ", ["Hors Crise", "Inondation", "Sécheresse"], key="alea_radio")
        rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon = st.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"], value="2050")
        
        # Logique de calcul du niveau de risque global
        # "Hors Crise" override le risque pour être minimal
        if alea == "Hors Crise":
            risk_level = 0
            alert_active = False
        else:
            risk_level = 0
            if horizon == "2050": risk_level += 1
            if horizon == "2100": risk_level += 2
            if rcp == "4.5": risk_level += 1
            if rcp == "8.5": risk_level += 2
            alert_active = risk_level >= 3 # Activer l'alerte visuelle à partir d'un certain risque
        
        # Pour simuler le "Aléa Actif" dans la visualisation
        st.session_state.alea_type = alea
        st.session_state.rcp = rcp
        st.session_state.horizon = horizon
        st.session_state.risk_level = risk_level
        st.session_state.alert_active = alert_active

    elif st.session_state.active_tab == "Alea":
        st.subheader("Type d'aléa")
        st.write("Détails sur les aléas et leur modélisation.")
        # Ici tu pourrais mettre des graphiques ou du texte explicatif
    elif st.session_state.active_tab == "Horizon":
        st.subheader("Horizon Temporel")
        st.write("Informations sur les projections climatiques et leur incertitude.")
        # Plus d'informations contextuelles ici


# --- Initialisation des états si le script est re-chargé ---
if 'alea_type' not in st.session_state: st.session_state.alea_type = "Hors Crise"
if 'rcp' not in st.session_state: st.session_state.rcp = "8.5"
if 'horizon' not in st.session_state: st.session_state.horizon = "2050"
if 'risk_level' not in st.session_state: st.session_state.risk_level = 0
if 'alert_active' not in st.session_state: st.session_state.alert_active = False


# --- LOGIQUE DE COULEUR DYNAMIQUE DES ZONES ---
def get_zone_color_config(zone_key, alea_type, current_risk_level):
    if alea_type == "Hors Crise":
        return "rgba(0, 242, 255, 0.2)", "#00f2ff" # Bleu X-Ray partout
    
    base_sens = zones[zone_key]["base_sensitivity"]
    
    # Ajuster la sensibilité en fonction de l'aléa
    if alea_type == "Inondation":
        if "Cuve" in zone_key or "Bassin" in zone_key: base_sens += 2 
        if "Pompe" in zone_key or "Elec" in zone_key: base_sens += 1
    elif alea_type == "Sécheresse":
        if "Cuve" in zone_key or "Bassin" in zone_key: base_sens += 2 
        if "Filtre" in zone_key: base_sens += 1

    final_score = base_sens + current_risk_level

    # Couleurs néon pour le schéma
    if final_score <= 3: return "rgba(0, 255, 0, 0.2)", "#00ff00"       # Vert (faible risque)
    if final_score <= 5: return "rgba(255, 255, 0, 0.3)", "#ffff00"     # Jaune (modéré)
    if final_score <= 7: return "rgba(255, 165, 0, 0.4)", "#ffa500"     # Orange (élevé)
    return "rgba(255, 0, 0, 0.5)", "#ff0000"                            # Rouge (critique)


# --- DÉFINITION DÉTAILLÉE DES ZONES DE LA STATION (avec sous-sol et routes) ---
# Chaque élément est une boîte ou un cylindre, avec des coordonnées 3D
zones = {
    # NIVEAU SOL
    "Base_Plateforme": {"type": "box", "x": [0, 6], "y": [0, 4], "z": [-0.1, 0], "base_sensitivity": 0},
    "Clarificateur_1_Cyl": {"type": "cylinder", "x": [1, 2], "y": [0.5, 1.5], "z": [0, 1], "base_sensitivity": 2, "name": "Clarificateur 1"},
    "Clarificateur_2_Cyl": {"type": "cylinder", "x": [3, 4], "y": [0.5, 1.5], "z": [0, 1], "base_sensitivity": 2, "name": "Clarificateur 2"},
    "Bat_Pompes_Surface": {"type": "box", "x": [0.5, 1.5], "y": [2.5, 3.5], "z": [0, 0.8], "base_sensitivity": 3, "name": "Bâtiment Pompes"},
    "Bat_Controle_Surface": {"type": "box", "x": [2.5, 3.5], "y": [2.5, 3.5], "z": [0, 0.6], "base_sensitivity": 1, "name": "Bâtiment Contrôle"},
    "Cuve_Traitement_1": {"type": "cylinder", "x": [4.5, 5.5], "y": [2.0, 3.0], "z": [0, 0.7], "base_sensitivity": 2, "name": "Cuve Traitement 1"},
    "Cuve_Traitement_2": {"type": "cylinder", "x": [4.5, 5.5], "y": [0.8, 1.8], "z": [0, 0.7], "base_sensitivity": 2, "name": "Cuve Traitement 2"},
    "Filtres_Aeration": {"type": "box", "x": [0.5, 2.0], "y": [-0.5, 0.0], "z": [0, 0.5], "base_sensitivity": 1, "name": "Filtres Aération"}, # Zone plus en avant
    
    # SOUS-SOL (représenté légèrement en dessous du niveau 0 ou comme une "tranchée")
    "Zone_Sous_Sol_Gen": {"type": "box", "x": [0.8, 4.2], "y": [0.3, 3.7], "z": [-0.5, -0.1], "base_sensitivity": 1, "name": "Sous-sol Général"},
    "Gal_Cables_SousSol": {"type": "box", "x": [2.8, 3.2], "y": [0.2, 3.8], "z": [-0.7, -0.2], "base_sensitivity": 2, "name": "Galerie Câbles"},
    "Chambre_Vanne_SousSol": {"type": "box", "x": [1.3, 1.7], "y": [1.8, 2.2], "z": [-0.6, -0.2], "base_sensitivity": 2, "name": "Chambre Vanne"},
}

# --- DÉFINITION DES CONDUITES/TUYAUX (LIGNES 3D) ---
# Chaque conduite est une série de points 3D pour simuler un chemin
pipes = [
    {"points": [[1.5,1,0.5], [1.5,2,0.5], [0.8,2,0.5]], "color_key": "Clarificateur_1_Cyl"}, # De C1 vers bâtiment pompes
    {"points": [[3.5,1,0.5], [3.5,2,0.5], [4.2,2,0.5]], "color_key": "Clarificateur_2_Cyl"}, # De C2 vers traitement
    {"points": [[0.8,3,0.3], [2.8,3,0.3], [2.8,2.7,0.3]], "color_key": "Bat_Pompes_Surface"}, # Connexion électrique (ex)
    {"points": [[4.5,2.5,0.4], [3.8,2.5,0.4], [3.8,2.7,0.4]], "color_key": "Cuve_Traitement_1"}, # De Cuve1 vers contrôle
    {"points": [[4.5,1.3,0.4], [3.8,1.3,0.4], [3.8,1,0.4]], "color_key": "Cuve_Traitement_2"}, # De Cuve2 vers traitement
    # Tuyaux sous-terrains
    {"points": [[1.5,2.8,-0.3], [1.5,3.2,-0.3], [3,3.2,-0.3], [3,2.8,-0.3]], "color_key": "Gal_Cables_SousSol"}, # Câbles sous-sol
    {"points": [[1.0,0.0,-0.1], [1.0,0.5,-0.1], [0.5,0.5,-0.1]], "color_key": "Filtres_Aeration"}, # Tuyau filtration
]

# --- DÉFINITION DES ROUTES INTERNES (LIGNES 3D plus larges) ---
roads = [
    {"points": [[0, 2, 0.01], [6, 2, 0.01]], "color": "rgba(100,100,100,0.7)"}, # Route principale
    {"points": [[2, 0, 0.01], [2, 4, 0.01]], "color": "rgba(100,100,100,0.7)"}, # Route secondaire
]


# --- FONCTION DE CRÉATION DE LA SCÈNE 3D SCHÉMATIQUE ---
def create_schematic_3d_view(alea_type, current_risk_level, alert_active):
    fig = go.Figure()

    # Ajout des zones (boîtes et cylindres)
    for zone_key, props in zones.items():
        fill_color, line_color = get_zone_color_config(zone_key, alea_type, current_risk_level)
        x_coords, y_coords, z_coords = props["x"], props["y"], props["z"]

        if props["type"] == "cylinder":
            radius = (x_coords[1] - x_coords[0]) / 2
            center_x = (x_coords[0] + x_coords[1]) / 2
            center_y = (y_coords[0] + y_coords[1]) / 2
            
            theta = np.linspace(0, 2 * np.pi, 30)
            x_circle = center_x + radius * np.cos(theta)
            y_circle = center_y + radius * np.sin(theta)
            
            # Surface du cylindre
            fig.add_trace(go.Surface(
                x=np.outer(x_circle, np.ones(2)),
                y=np.outer(y_circle, np.ones(2)),
                z=np.outer(np.ones(len(theta)), [z_coords[0], z_coords[1]]),
                surfacecolor=np.full((len(theta), 2), 0.5), 
                colorscale=[[0, fill_color], [1, fill_color]], 
                opacity=0.4, # Plus transparent pour l'effet X-ray
                showscale=False,
                name=props.get("name", zone_key)
            ))
            # Bordures pour l'effet X-ray
            fig.add_trace(go.Scatter3d(
                x=np.append(x_circle, x_circle[0]), y=np.append(y_circle, y_circle[0]),
                z=np.full_like(np.append(x_circle, x_circle[0]), z_coords[1]),
                mode='lines', line=dict(color=line_color, width=3), showlegend=False
            ))
            fig.add_trace(go.Scatter3d(
                x=np.append(x_circle, x_circle[0]), y=np.append(y_circle, y_circle[0]),
                z=np.full_like(np.append(x_circle, x_circle[0]), z_coords[0]),
                mode='lines', line=dict(color=line_color, width=3), showlegend=False
            ))

        elif props["type"] == "box":
            # Dessine des boîtes pour les bassins et bâtiments
            x_b = [x_coords[0], x_coords[1], x_coords[1], x_coords[0], x_coords[0], x_coords[1], x_coords[1], x_coords[0]]
            y_b = [y_coords[0], y_coords[0], y_coords[1], y_coords[1], y_coords[0], y_coords[0], y_coords[1], y_coords[1]]
            z_b = [z_coords[0], z_coords[0], z_coords[0], z_coords[0], z_coords[1], z_coords[1], z_coords[1], z_coords[1]]

            fig.add_trace(go.Mesh3d(
                x=x_b, y=y_b, z=z_b,
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                color=fill_color, name=props.get("name", zone_key), opacity=0.4, showscale=False
            ))
            # Bordures pour l'effet X-ray
            fig.add_trace(go.Scatter3d(
                x=[x_coords[0], x_coords[1], x_coords[1], x_coords[0], x_coords[0], x_coords[0], x_coords[0], x_coords[1], x_coords[1], x_coords[1], x_coords[1], x_coords[0]],
                y=[y_coords[0], y_coords[0], y_coords[1], y_coords[1], y_coords[0], y_coords[0], y_coords[1], y_coords[1], y_coords[0], y_coords[0], y_coords[1], y_coords[1]],
                z=[z_coords[0], z_coords[0], z_coords[0], z_coords[0], z_coords[0], z_coords[1], z_coords[1], z_coords[1], z_coords[1], z_coords[0], z_coords[0], z_coords[0]],
                mode='lines', line=dict(color=line_color, width=3), showlegend=False
            ))

    # Ajout des conduites/tuyaux
    for pipe in pipes:
        pipe_points = np.array(pipe["points"])
        # La couleur du tuyau est basée sur la zone à laquelle il est rattaché
        fill_color_pipe, line_color_pipe = get_zone_color_config(pipe["color_key"], alea_type, current_risk_level)
        
        fig.add_trace(go.Scatter3d(
            x=pipe_points[:,0], y=pipe_points[:,1], z=pipe_points[:,2],
            mode='lines',
            line=dict(color=line_color_pipe, width=5, dash='solid'), # Ligne lumineuse
            showlegend=False,
            name=f"Tuyau {pipe['color_key']}"
        ))

    # Ajout des routes internes (lignes plus larges)
    for road in roads:
        road_points = np.array(road["points"])
        fig.add_trace(go.Scatter3d(
            x=road_points[:,0], y=road_points[:,1], z=road_points[:,2],
            mode='lines',
            line=dict(color=road["color"], width=10), # Plus large pour une route
            showlegend=False
        ))

    # Mise à jour du layout pour la vue 3D
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-1, 7]),
            yaxis=dict(visible=False, range=[-1, 5]),
            zaxis=dict(visible=False, range=[-1, 1.5]), # Range étendu pour le sous-sol
            aspectmode='manual',
            aspectratio=dict(x=1, y=0.7, z=0.5), # Perspective isométrique
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=0.8), # Vue isométrique
                up=dict(x=0, y=0, z=1)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=700, # Hauteur plus grande pour la 3D
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False # Pas de légende pour les nombreux éléments
    )
    return fig

# --- LAYOUT PRINCIPAL ---
st.header("Mode Crise (Aléa Actif)") # Titre en haut à gauche
st.markdown("---") # Séparateur

# Texte explicatif (remplace par ton texte réel)
st.write("Ce modèle numérique simule les impacts d'aléas climatiques sur la station de pompage. Il permet d'évaluer la vulnérabilité des différentes infrastructures et d'anticiper les coûts de dommages, la continuité de service et les impacts systémiques sur le territoire. Utilisez le Hub de Contrôle pour explorer différents scénarios et horizons temporels.")
st.markdown("---")


col_3d, col_impacts = st.columns([2.5, 1])

with col_3d:
    # Affiche l'alerte centrale si besoin
    if st.session_state.alert_active:
        st.markdown(f"""
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1000; width: 400px;">
            <div style="background: rgba(255, 0, 0, 0.7); border: 2px solid #ff0000; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 0 20px #ff0000;">
                <h3 style="color: white; margin: 0;">⚠️ STRUCTURAL FAILURE IMMINENT</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.plotly_chart(create_schematic_3d_view(st.session_state.alea_type, st.session_state.risk_level, st.session_state.alert_active), use_container_width=True)


with col_impacts:
    st.subheader("📊 ANALYSE DES IMPACTS")
    
    # Coûts des dégâts (simulés)
    base_cost_multiplier = st.session_state.risk_level * 0.7 + 1 
    cost_6m = 1000000 * base_cost_multiplier
    cost_2y = 5000000 * base_cost_multiplier
    cost_5y = 10000000 * base_cost_multiplier

    st.markdown(f"""
    <div class="info-card">
        <h4>COÛTS DÉGÂTS ({st.session_state.horizon}):</h4>
        <p>6 mois: <span class="metric-value">-{cost_6m:,.0f} €</span></p>
        <p>2 ans: <span class="metric-value">-{cost_2y:,.0f} €</span></p>
        <p>5 ans: <span class="metric-value">-{cost_5y:,.0f} €</span></p>
    </div>
    """, unsafe_allow_html=True)

    # Continuité de service
    service_continuity = max(0, 100 - (st.session_state.risk_level * 18)) 
    status_class = "status-critical" if service_continuity < 60 else "status-ok"
    
    st.markdown(f"""
    <div class="info-card">
        <h4>CONTINUITÉ SERVICE</h4>
        <p>Status: <span class="{status_class}">{service_continuity:.0f}%</span></p>
        <div style="background:#333; height:10px; border-radius:5px;"><div style="width:{service_continuity}%; background:{'#ff4b4b' if service_continuity < 60 else '#00ff00'}; height:10px; border-radius:5px;"></div></div>
    </div>
    """, unsafe_allow_html=True)

    # Impacts systémiques
    st.markdown("""
    <div class="info-card">
        <h4>IMPACTS SYSTÉMIQUES:</h4>
        <ul>
            <li>- Eau potable contaminée</li>
            <li>- Coupure électrique régionale</li>
            <li>- Pertes agricoles majeures</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---") # Séparateur avant les stratégies
st.subheader("🛠️ STRATÉGIES D'ADAPTATION")

# Boutons de stratégies
st.markdown("""
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <button class="strategy-button">Physique</button>
        <button class="strategy-button">Systémique</button>
        <button class="strategy-button">Gouvernance</button>
        <button class="strategy-button">Approvisionnement</button>
        <button class="strategy-button">R&D</button>
    </div>
""", unsafe_allow_html=True)

# Contenu des stratégies (simplifié, tu peux ajouter des onglets ou plus de texte)
st.markdown("""
    <ul>
        <li>**Physique** : Surélévation des infrastructures critiques, renforcement des digues, utilisation de matériaux hydrofuges et résistants à la corrosion.</li>
        <li>**Systémique** : Redondance des systèmes de pompage et d'alimentation électrique, optimisation des circuits d'approvisionnement en eau brute, mise en place de bassins tampons.</li>
        <li>**Gouvernance** : Établissement de protocoles d'urgence clairs, collaboration inter-sectorielle avec les autorités locales, révision des plans d'urbanisme.</li>
        <li>**Approvisionnement** : Diversification des sources d'eau (alternatives de forage), gestion optimisée des stocks de réactifs et de carburant.</li>
        <li>**R&D** : Développement de capteurs intelligents pour la détection précoce d'anomalies, innovation en matière de traitement des eaux, modélisation prédictive avancée.</li>
    </ul>
""", unsafe_allow_html=True)
