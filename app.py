import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Digital Twin - Station d'Épuration Schéma")

# --- STYLE CSS (Fond noir, textes néon, conteneurs stylisés) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #111; }
    h1, h2, h3, h4, p, label, .stSlider > div > div > label { color: #00f2ff !important; }

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
    
    /* Boutons de stratégie */
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
    
    /* Ajout pour le "HIGH SENSITIVITY" et le titre en haut à gauche */
    .high-sensitivity {
        color: #00f2ff;
        font-size: 2em;
        font-weight: bold;
        text-shadow: 0 0 10px #00f2ff;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- HUB DE CONTRÔLE (SIDEBAR) ---
with st.sidebar:
    st.title("🕹️ HUB DE CONTRÔLE")
    st.subheader("Aléas Climatiques")
    
    alea = st.selectbox("Type d'aléa", ["Inondation", "Sécheresse"])
    rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")
    horizon = st.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"], value="2050")

    # Logique de calcul du niveau de risque global
    risk_level = 0
    if horizon == "2050": risk_level += 1
    if horizon == "2100": risk_level += 2
    if rcp == "4.5": risk_level += 1
    if rcp == "8.5": risk_level += 2

    st.divider()
    st.info("Ce hub pilote la vulnérabilité des zones et les impacts.")

# --- DÉFINITION DES ZONES DE LA STATION D'ÉPURATION SCHÉMATIQUE ---
# Coordonnées abstraites pour le schéma
zones = {
    "Clarificateur_1": {"x": [-0.5, 0.5], "y": [0.5, 1.5], "z": [0, 0.2], "shape": "cylinder", "base_sensitivity": 2},
    "Clarificateur_2": {"x": [1.0, 2.0], "y": [0.5, 1.5], "z": [0, 0.2], "shape": "cylinder", "base_sensitivity": 2},
    "Bassin_Primaire": {"x": [-0.5, 2.0], "y": [-1.0, 0.0], "z": [0, 0.1], "shape": "box", "base_sensitivity": 3},
    "Floculation_Traitement": {"x": [2.5, 4.0], "y": [-1.0, 0.0], "z": [0, 0.15], "shape": "box", "base_sensitivity": 1},
    "Batiment_Controle": {"x": [2.8, 3.5], "y": [0.5, 1.0], "z": [0, 0.4], "shape": "box", "base_sensitivity": 1},
}

# --- LOGIQUE DE COULEUR DYNAMIQUE DES ZONES ---
def get_zone_color(zone_key, alea_type, current_risk_level):
    base_sens = zones[zone_key]["base_sensitivity"]
    
    # Ajuster la sensibilité en fonction de l'aléa
    if alea_type == "Inondation":
        if "Clarificateur" in zone_key: base_sens += 1 
        if "Bassin" in zone_key: base_sens += 1
        if "Batiment_Controle" in zone_key: base_sens += 1 # Contrôle peut être impacté par inondation
    elif alea_type == "Sécheresse":
        if "Bassin" in zone_key: base_sens += 2 # Très sensible au manque d'eau
        if "Floculation" in zone_key: base_sens += 1

    final_score = base_sens + current_risk_level

    # Couleurs néon pour le schéma
    if final_score <= 3: return "rgba(0, 255, 0, 0.4)", "#00ff00"       # Vert (faible risque)
    if final_score <= 5: return "rgba(255, 255, 0, 0.4)", "#ffff00"     # Jaune (modéré)
    if final_score <= 7: return "rgba(255, 165, 0, 0.4)", "#ffa500"     # Orange (élevé)
    return "rgba(255, 0, 0, 0.5)", "#ff0000"                            # Rouge (critique)

# --- CRÉATION DE LA SCÈNE 3D SCHÉMATIQUE AVEC PLOTLY ---
def create_schematic_3d_view(alea_type, current_risk_level):
    fig = go.Figure()

    for zone_key, props in zones.items():
        fill_color, line_color = get_zone_color(zone_key, alea_type, current_risk_level)
        x_min, x_max = props["x"]
        y_min, y_max = props["y"]
        z_min, z_max = props["z"]

        if props["shape"] == "cylinder":
            # Dessine des cylindres pour les clarificateurs
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
                surfacecolor=np.full((len(theta), 2), 0.5), 
                colorscale=[[0, fill_color], [1, fill_color]], 
                opacity=0.6,
                showscale=False,
                name=zone_key
            ))
            # Bordures pour l'effet X-ray
            fig.add_trace(go.Scatter3d(
                x=np.append(x_circle, x_circle[0]),
                y=np.append(y_circle, y_circle[0]),
                z=np.full_like(np.append(x_circle, x_circle[0]), z_max),
                mode='lines', line=dict(color=line_color, width=3), name=zone_key + "_border_top"
            ))
            fig.add_trace(go.Scatter3d(
                x=np.append(x_circle, x_circle[0]),
                y=np.append(y_circle, y_circle[0]),
                z=np.full_like(np.append(x_circle, x_circle[0]), z_min),
                mode='lines', line=dict(color=line_color, width=3), name=zone_key + "_border_bottom"
            ))


        elif props["shape"] == "box":
            # Dessine des boîtes pour les bassins et bâtiments
            x_coords = [x_min, x_max, x_max, x_min, x_min, x_max, x_max, x_min]
            y_coords = [y_min, y_min, y_max, y_max, y_min, y_min, y_max, y_max]
            z_coords = [z_min, z_min, z_min, z_min, z_max, z_max, z_max, z_max]

            # Corps du cube
            fig.add_trace(go.Mesh3d(
                x=x_coords, y=y_coords, z=z_coords,
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                color=fill_color, name=zone_key, opacity=0.6, showscale=False
            ))
            # Bordures pour l'effet X-ray
            fig.add_trace(go.Scatter3d(
                x=[x_min, x_max, x_max, x_min, x_min, x_min, x_min, x_max, x_max, x_max, x_max, x_min],
                y=[y_min, y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min, y_min, y_max, y_max],
                z=[z_min, z_min, z_min, z_min, z_min, z_max, z_max, z_max, z_max, z_min, z_min, z_min],
                mode='lines', line=dict(color=line_color, width=3), name=zone_key + "_borders"
            ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-1, 5]), # Ajuster les ranges pour le schéma
            yaxis=dict(visible=False, range=[-1.5, 2]),
            zaxis=dict(visible=False, range=[0, 0.6]),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.4), # Ratio pour la perspective
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=0.8), # Vue isométrique
                up=dict(x=0, y=0, z=1)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- LAYOUT PRINCIPAL ---
col_hub_info, col_3d, col_impacts = st.columns([1, 2.5, 1])

with col_hub_info:
    st.markdown("<h3><span class='high-sensitivity'>HIGH SENSITIVITY</span></h3>", unsafe_allow_html=True)
    st.markdown("<h4>Floculation / Primary Treatment efficiency</h4>", unsafe_allow_html=True)
    st.progress(0.75) # Exemple de jauge d'efficacité
    st.markdown("<br><h4>IMPACTED AT RISK</h4>", unsafe_allow_html=True) # Texte d'alerte
    # Ici, tu peux ajouter plus de détails sur les capteurs, etc.

with col_3d:
    st.markdown("<h3>🏗️ Schéma X-Ray : Station d'Épuration</h3>", unsafe_allow_html=True)
    
    # Message d'alerte au centre
    if risk_level >= 3:
        st.markdown(f"""
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1000;">
            <div style="background: rgba(255, 0, 0, 0.7); border: 2px solid #ff0000; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 0 20px #ff0000;">
                <h3 style="color: white; margin: 0;">⚠️ STRUCTURAL FAILURE IMMINENT</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.plotly_chart(create_schematic_3d_view(alea, risk_level), use_container_width=True)

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
    base_cost_multiplier = risk_level * 0.7 + 1 # Plus le risque est élevé, plus les coûts augmentent
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
    service_continuity = max(0, 100 - (risk_level * 18)) # Diminue avec le risque
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
