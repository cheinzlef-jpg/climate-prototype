import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Digital Twin - Station d'Épuration")

# --- STYLE CSS (Fond noir, textes néon, conteneurs stylisés) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #111; }
    h1, h2, h3, h4, p, label { color: #00f2ff !important; }

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
        color: #ff4b4b; /* Rouge pour les alertes/coûts */
    }
    .status-critical {
        color: #ff4b4b;
        font-weight: bold;
    }
    .status-ok {
        color: #00ff00;
        font-weight: bold;
    }
    .strategy-button {
        background-color: #005060;
        color: #00f2ff;
        border: 1px solid #00f2ff;
        padding: 8px 15px;
        border-radius: 5px;
        cursor: pointer;
        margin-right: 10px;
        transition: background-color 0.3s, box-shadow 0.3s;
    }
    .strategy-button:hover {
        background-color: #008090;
        box-shadow: 0 0 8px rgba(0, 242, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- HUB DE CONTRÔLE (SIDEBAR) ---
with st.sidebar:
    st.title("🕹️ HUB DE CONTRÔLE")
    st.subheader("Aléas Climatiques")
    
    # Choix de l'aléa (Sécheresse / Inondation - ici "Active" pour l'image)
    st.write("Aléa Climatique:")
    st.markdown("<h3><span style='color:#ff4b4b;'>Sécheresse / Inondation (ACTIVE)</span></h3>", unsafe_allow_html=True) # Pour simuler l'état "ACTIVE"

    # Scénario RCP
    rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")

    # Horizon Temporel
    horizon_options = ["Actuel", "2050", "2100"]
    horizon = st.select_slider("Horizon Temporel", options=horizon_options, value="2050")

    # Logique de calcul du niveau de risque global (pour les impacts et couleurs)
    risk_level = 0
    if horizon == "2050": risk_level += 1
    if horizon == "2100": risk_level += 2
    if rcp == "4.5": risk_level += 1
    if rcp == "8.5": risk_level += 2

    st.divider()
    st.info("Ce hub pilote la vulnérabilité des zones X-Ray et les impacts.")

# --- DÉFINITION DES ZONES DE LA STATION D'ÉPURATION ---
# Coordonnées arbitraires pour simuler la position des éléments sur la carte
# Les "z" sont de 0 pour les rendre plats, puis on les "élève" avec Plotly
zones = {
    "Clarificateur_1": {"x": [0.3, 0.6], "y": [0.6, 0.9], "z": [0, 0.1], "base_sensitivity": 2, "shape": "circle"},
    "Clarificateur_2": {"x": [0.0, 0.3], "y": [0.6, 0.9], "z": [0, 0.1], "base_sensitivity": 2, "shape": "circle"},
    "Bassin_Primaire": {"x": [0.0, 0.6], "y": [0.0, 0.5], "z": [0, 0.1], "base_sensitivity": 3, "shape": "rectangle"},
    "Floculation_Traitement": {"x": [0.6, 0.9], "y": [0.0, 0.5], "z": [0, 0.1], "base_sensitivity": 1, "shape": "rectangle"},
    "Batiment_Technique": {"x": [0.7, 0.9], "y": [0.6, 0.8], "z": [0, 0.2], "base_sensitivity": 1, "shape": "box"},
}

# --- LOGIQUE DE COULEUR DYNAMIQUE DES ZONES ---
def get_zone_color(zone_key, alea_type, current_risk_level):
    base_sens = zones[zone_key]["base_sensitivity"]
    
    # Ajuster la sensibilité en fonction de l'aléa
    if alea_type == "Inondation":
        if "Clarificateur" in zone_key: base_sens += 1 # Plus sensible aux inondations
        if "Bassin" in zone_key: base_sens += 1
    elif alea_type == "Sécheresse":
        if "Bassin" in zone_key: base_sens += 2 # Très sensible au manque d'eau
        if "Floculation" in zone_key: base_sens += 1

    final_score = base_sens + current_risk_level

    if final_score <= 3: return "rgba(0, 255, 0, 0.5)"    # Vert: Faible risque
    if final_score <= 5: return "rgba(255, 255, 0, 0.5)"  # Jaune: Risque modéré
    if final_score <= 7: return "rgba(255, 165, 0, 0.5)"  # Orange: Risque élevé
    return "rgba(255, 0, 0, 0.6)"                         # Rouge: Risque critique

# --- CRÉATION DE LA SCÈNE 3D AVEC PLOTLY ---
def create_station_3d_view(alea_type, current_risk_level, background_image_url):
    fig = go.Figure()

    # Ajouter l'image satellite en arrière-plan
    fig.add_layout_image(
        source=background_image_url,
        xref="x", yref="y",
        x=0, y=1, sizex=1, sizey=1,  # Étirer l'image sur toute la surface (0 à 1)
        sizing="stretch", opacity=0.8, layer="below"
    )

    for zone_key, props in zones.items():
        color = get_zone_color(zone_key, alea_type, current_risk_level)
        x_min, x_max = props["x"]
        y_min, y_max = props["y"]
        z_min, z_max = props["z"]

        if props["shape"] == "circle":
            # Représenter les clarificateurs comme des cylindres
            theta = np.linspace(0, 2 * np.pi, 50)
            radius = (x_max - x_min) / 2
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            
            x_circle = center_x + radius * np.cos(theta)
            y_circle = center_y + radius * np.sin(theta)
            
            # Surface du cylindre
            fig.add_trace(go.Surface(
                x=np.outer(x_circle, np.ones(2)),
                y=np.outer(y_circle, np.ones(2)),
                z=np.outer(np.ones(len(theta)), [z_min, z_max]),
                surfacecolor=np.full((len(theta), 2), 0.5), # Couleur uniforme
                colorscale=[[0, color], [1, color]], # Appliquer la couleur dynamique
                opacity=0.6,
                showscale=False,
                name=zone_key
            ))
            # Fond et couvercle (facultatif)
            fig.add_trace(go.Mesh3d(
                x=x_circle, y=y_circle, z=np.full_like(x_circle, z_min), opacity=0.6,
                color=color, name=zone_key + "_bottom"
            ))
            fig.add_trace(go.Mesh3d(
                x=x_circle, y=y_circle, z=np.full_like(x_circle, z_max), opacity=0.6,
                color=color, name=zone_key + "_top"
            ))


        elif props["shape"] == "rectangle" or props["shape"] == "box":
            # Représenter les bassins et bâtiments comme des boîtes
            fig.add_trace(go.Mesh3d(
                x=[x_min, x_max, x_max, x_min, x_min, x_max, x_max, x_min],
                y=[y_min, y_min, y_max, y_max, y_min, y_min, y_max, y_max],
                z=[z_min, z_min, z_min, z_min, z_max, z_max, z_max, z_max],
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                color=color, name=zone_key, opacity=0.6, showscale=False
            ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[0, 1]), # Ajuster les ranges pour l'image
            yaxis=dict(visible=False, range=[0, 1]),
            zaxis=dict(visible=False, range=[0, 0.5]), # Hauteur max pour la 3D
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5), # Ratio pour que la 3D ne soit pas trop étirée
            camera=dict(
                eye=dict(x=0.5, y=0.5, z=2), # Vue initiale
                up=dict(x=0, y=1, z=0)
            )
        ),
        images=[
            go.layout.Image(
                source=background_image_url,
                xref="x", yref="y",
                x=0, y=1, sizex=1, sizey=1, # Coordonnées de l'image
                sizing="stretch", opacity=1, layer="below"
            )
        ],
        margin=dict(l=0, r=0, b=0, t=0),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# URL de l'image satellite que tu as fournie
# Il est préférable de l'héberger quelque part pour une meilleure performance
# Pour l'exemple, j'utilise une URL générique, mais tu peux remplacer par la tienne.
SATELLITE_IMAGE_URL = "https://i.imgur.com/your-satellite-image.png" # Remplace cette URL par celle de ton image

# --- LAYOUT PRINCIPAL ---
col_hub, col_3d, col_impacts = st.columns([1, 2.5, 1])

# COLONNE DE GAUCHE : HUB DE CONTRÔLE (déjà en sidebar) et informations textuelles
with col_hub:
    st.markdown("<h4>Floculation / Primary Treatment efficiance</h4>", unsafe_allow_html=True)
    st.progress(0.75) # Exemple de jauge d'efficacité
    st.markdown("<br><h4>HIGH SENSITIVITY</h4>", unsafe_allow_html=True) # Texte d'alerte
    # Ici, tu peux ajouter plus de détails sur les capteurs, etc.

# COLONNE CENTRALE : VUE 3D X-RAY
with col_3d:
    st.markdown("<h3>Station d'Épuration : Vue X-Ray</h3>", unsafe_allow_html=True)
    # Le choix de l'aléa pour les couleurs
    active_alea = "Inondation" # Pour l'image, on suppose "Inondation ACTIVE"
    st.plotly_chart(create_station_3d_view(active_alea, risk_level, SATELLITE_IMAGE_URL), use_container_width=True)
    st.markdown("<br><h4>IMPACTED AT RISK</h4>", unsafe_allow_html=True)

    # --- STRATÉGIES D'ADAPTATION (En bas de la 3D) ---
    st.subheader("🛠️ STRATÉGIES D'ADAPTATION")
    
    # Boutons pour les catégories de stratégies (HTML pour le style)
    st.markdown("""
        <div>
            <button class="strategy-button">Physique</button>
            <button class="strategy-button">Systémique</button>
            <button class="strategy-button">Gouvernance</button>
        </div>
        <br>
    """, unsafe_allow_html=True)

    # Contenu des stratégies (ici, simplifié pour l'exemple)
    st.markdown("""
        <ul>
            <li>- Surélévation Murs</li>
            <li>- Matériaux Hydrofuges</li>
        </ul>
    """, unsafe_allow_html=True)


# COLONNE DE DROITE : ANALYSE DES IMPACTS
with col_impacts:
    st.subheader("📊 ANALYSE DES IMPACTS")
    
    # Coûts des dégâts (simulés)
    base_cost_multiplier = risk_level * 0.5 + 1 # Plus le risque est élevé, plus les coûts augmentent
    cost_6m = 1000000 * base_cost_multiplier
    cost_2y = 5000000 * base_cost_multiplier
    cost_5y = 10000000 * base_cost_multiplier

    st.markdown(f"""
    <div class="info-card">
        <h4>COÛTS DÉGÂTS ({horizon}):</h4>
        <p>6 mois: <span class="metric-value">-{cost_6m:,.0f} €</span></p>
        <p>2 ans: <span class="metric-value">-{cost_2y:,.0f} €</span></p>
        <p>5 ans: <span class="metric-value">-{cost_5y:,.0f} €</span></p>
    </div>
    """, unsafe_allow_html=True)

    # Continuité de service
    service_continuity = max(0, 100 - (risk_level * 15)) # Diminue avec le risque
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
