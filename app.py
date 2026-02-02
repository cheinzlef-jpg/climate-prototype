import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Tunnel Mont-Blanc X-Ray V2")

# --- CSS PERSONNALISÉ POUR LE FOND NOIR ET L'ESTHÉTIQUE ---
st.markdown("""
<style>
    .reportview-container {
        background: #050505; /* Presque noir */
        color: white;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #00f2ff; /* Cyan néon pour les titres */
    }
    .stSlider > div > div > div > div {
        background: #00f2ff; /* Curseur néon */
    }
    .stSelectbox > div > div > label {
        color: white;
    }
    .stMarkdown {
        color: white;
    }
</style>
""", unsafe_allow_html=True)


st.title("🚇 Modélisation X-Ray du Tunnel du Mont-Blanc")

# --- CONTRÔLES DYNAMIQUES ---
st.sidebar.header("Paramètres du Scénario")
annee = st.sidebar.slider("Année", 2024, 2100, 2050, 10)
rcp = st.sidebar.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"])

# --- SIMULATION DES DONNÉES DE RISQUE ---
def get_risk_profile(rcp_val, year_val, num_segments=50):
    length = 11.6 # km
    segments = np.linspace(0, length, num_segments)
    
    # Logique de risque simplifiée : plus l'année et le RCP sont élevés, plus le risque est grand
    # Facteurs de risque différents pour chaque RCP et année
    base_risk = 0.5 + np.sin(segments / (length/5)) * 0.2 + np.cos(segments / (length/3)) * 0.1 # Variation le long du tunnel

    if rcp_val == "2.6":
        risk_factor = 0.1 + (year_val - 2024) / 100 * 0.8
    elif rcp_val == "4.5":
        risk_factor = 0.3 + (year_val - 2024) / 100 * 1.5
    else: # RCP 8.5
        risk_factor = 0.6 + (year_val - 2024) / 100 * 2.5
        
    total_risk = (base_risk + np.random.normal(0, 0.05, num_segments)) * risk_factor * 10
    
    # Mettre en évidence des pics de risque pour des zones spécifiques
    # Par exemple, risque d'inondation à la fin (Portail IT)
    if year_val > 2050 and rcp_val in ["4.5", "8.5"]:
        total_risk[-5:] += total_risk[-5:] * 0.5 # Augmente le risque à la fin du tunnel
    # Risque de glissement de terrain au début (Portail FR)
    if year_val > 2050 and rcp_val in ["4.5", "8.5"]:
        total_risk[:5] += total_risk[:5] * 0.5

    return segments, np.clip(total_risk, 0, 10) # Risque entre 0 et 10

segments_km, risk_values = get_risk_profile(rcp, annee)

# --- MISE EN PAGE : 3D + PLOTLY ---
st.markdown("---") # Séparateur visuel

# Conteneur pour la 3D et les infos à droite
col_3d, col_info = st.columns([2, 1])

with col_3d:
    # --- Three.js pour la modélisation 3D du tunnel ---
    # La couleur de base du tunnel 3D (cyan) et la couleur du "pic" (rouge)
    # L'opacité du rouge est basée sur le niveau de risque moyen
    mean_risk = np.mean(risk_values) / 10 # Normalize pour 0-1
    red_opacity = min(0.8, mean_risk * 1.5) # Plus le risque est haut, plus le rouge est intense

    # JavaScript pour le rendu Three.js
    three_js_code = f"""
    <div id="container-3d" style="width: 100%; height: 500px; background-color: transparent;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, document.getElementById('container-3d').clientWidth / 500, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(document.getElementById('container-3d').clientWidth, 500);
        document.getElementById('container-3d').appendChild(renderer.domElement);
        renderer.setClearColor(0x000000, 0); // Fond transparent pour s'intégrer au style Streamlit

        // Lumière ambiante
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        // Lumière directionnelle pour faire ressortir les détails
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, 1, 1);
        scene.add(directionalLight);

        // Tunnel (cylindre creux pour l'effet tube)
        const tunnelGeometry = new THREE.CylinderGeometry(5, 5, 120, 32, 1, true);
        const tunnelMaterial = new THREE.MeshBasicMaterial({{
            color: 0x00f2ff, // Cyan néon
            wireframe: true,
            transparent: true,
            opacity: 0.2 // Très transparent pour l'effet X-Ray
        }});
        const tunnelMesh = new THREE.Mesh(tunnelGeometry, tunnelMaterial);
        tunnelMesh.rotation.z = Math.PI / 2; // Orienter horizontalement
        scene.add(tunnelMesh);

        // Courbe de risque rouge sur le sol du tunnel (simulé par un plan)
        const riskPoints = [
            // Ajouter les points de risque simulés pour former la courbe rouge
            // Cela nécessiterait de passer `segments_km` et `risk_values` au JS, ce qui est complexe directement.
            // On va simuler une courbe de base ici, ou créer un plan simple coloré.
        ];
        // Pour simplifier, on crée un plan simple au sol pour la couleur de risque
        const groundGeometry = new THREE.PlaneGeometry(120, 10);
        const groundMaterial = new THREE.MeshBasicMaterial({{
            color: 0xff0000, // Rouge vif
            transparent: true,
            opacity: {red_opacity} // Opacité basée sur le risque moyen
        }});
        const groundMesh = new THREE.Mesh(groundGeometry, groundMaterial);
        groundMesh.rotation.x = -Math.PI / 2; // Placer horizontalement
        groundMesh.position.y = -5; // Sous le tunnel
        scene.add(groundMesh);


        // Ajout de "tronçons" visuels (anneaux)
        for (let i = -60; i <= 60; i += 10) {{
            const ringGeo = new THREE.TorusGeometry(5.2, 0.08, 16, 100);
            const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, transparent: true, opacity: 0.3 }});
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.position.x = i;
            ring.rotation.y = Math.PI / 2;
            scene.add(ring);
        }}

        camera.position.set(0, 10, 20); // Position de la caméra
        camera.lookAt(0, 0, 0);

        // Animation de rotation (légère)
        function animate() {{
            requestAnimationFrame(animate);
            tunnelMesh.rotation.y += 0.001; // Rotation très légère
            groundMesh.rotation.y += 0.001;
            scene.children.forEach(obj => {{
                if (obj.geometry && obj.geometry.type === 'TorusGeometry') {{ // Rotation des anneaux
                    obj.rotation.y += 0.001;
                }}
            }});
            renderer.render(scene, camera);
        }}
        animate();

        // Répondre au redimensionnement de la fenêtre
        window.addEventListener('resize', () => {{
            camera.aspect = document.getElementById('container-3d').clientWidth / 500;
            camera.updateProjectionMatrix();
            renderer.setSize(document.getElementById('container-3d').clientWidth, 500);
        }});
    </script>
    """
    components.html(three_js_code, height=520)

with col_info:
    st.markdown(f"""
    <div style="background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #00f2ff;">
        <h3>Horizon Temporel: <span style="color:white;">{annee}</span></h3>
        <h3>Scénario RCP: <span style="color:white;">{rcp}</span></h3>
        <br>
        <p style="font-size: 18px; color:#ff4b4b;">Risque Thermique: 
            <span style="color:white;">{"Élevé" if mean_risk > 0.6 else "Modéré" if mean_risk > 0.3 else "Faible"}</span>
        </p>
        <p style="font-size: 18px; color:#ff4b4b;">Risque Glissement: 
            <span style="color:white;">{"Élevé" if risk_values[0] > 7 else "Modéré" if risk_values[0] > 4 else "Faible"}</span>
        </p>
        <p style="font-size: 18px; color:#ff4b4b;">Risque Inondation: 
            <span style="color:white;">{"Élevé" if risk_values[-1] > 7 else "Modéré" if risk_values[-1] > 4 else "Faible"}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- GRAPHIQUE DES NIVEAUX DE RISQUE (au-dessus du tunnel 3D pour l'effet "sol") ---
st.subheader("Profil de Vulnérabilité par Tronçon du Tunnel")

fig_risk = go.Figure()
fig_risk.add_trace(go.Scatter(
    x=segments_km, y=risk_values,
    mode='lines',
    line=dict(color='#ff0000', width=3), # Ligne rouge vif
    fill='tozeroy', # Remplir sous la ligne pour créer la forme de la "courbe rouge"
    fillcolor='rgba(255,0,0,0.3)', # Légèrement transparent
    name="Niveau de Risque"
))

# Ajout d'icônes/zones d'aléas comme sur l'image
hazard_points = {
    "Portail FR": {"pos": 1, "icon": "⛰️ Glissement"}, # Simuler des positions le long des 11.6km
    "Tronçon Central": {"pos": 5.8, "icon": "🔥 Thermique"},
    "Portail IT": {"pos": 10, "icon": "🌊 Inondation"}
}

for name, data in hazard_points.items():
    # Trouver l'index le plus proche pour la position
    idx = np.argmin(np.abs(segments_km - data["pos"]))
    fig_risk.add_annotation(
        x=segments_km[idx], y=risk_values[idx] + 1, # Un peu au-dessus de la courbe
        text=data["icon"],
        showarrow=False,
        font=dict(size=12, color="white"),
        bgcolor="rgba(0,242,255,0.2)", # Fond cyan transparent
        bordercolor="#00f2ff",
        borderwidth=1,
        borderpad=4,
        # Ajoute un petit cercle pour marquer la position
        xanchor="center"
    )

fig_risk.update_layout(
    xaxis_title="Distance le long du Tunnel (km)",
    yaxis_title="Niveau de Risque (0-10)",
    template="plotly_dark", # Thème sombre
    plot_bgcolor='#050505',
    paper_bgcolor='#050505',
    font_color="white",
    hovermode="x unified",
    height=300
)

st.plotly_chart(fig_risk, use_container_width=True)


st.markdown("""
<br>
<div style="background-color: #1a1a1a; padding: 15px; border-radius: 8px; border: 1px solid #00f2ff; text-align: center;">
    <h3 style="color: #00f2ff;">Analyse Synthétique</h3>
    <p>Cette modélisation interactive simule la vulnérabilité du Tunnel du Mont-Blanc face aux aléas climatiques (glissements, stress thermique, inondations) en fonction des scénarios RCP et des horizons temporels.</p>
    <p>La **courbe rouge** en bas de la modélisation 3D représente la distribution des risques. Les **points lumineux cyan** dans la 3D indiquent les tronçons du tunnel.</p>
</div>
""", unsafe_allow_html=True)
