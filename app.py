import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Tunnel X-Ray Pro")

# --- CONFIGURATION VISUELLE ---
# Utilise une image de fond sombre et contrastée pour le côté "Néon"
BG_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1920&q=80"

# --- LOGIQUE DE CONTRÔLE (SIDEBAR) ---
# On déplace les contrôles dans la barre latérale pour libérer l'espace visuel
with st.sidebar:
    st.header("🎛️ PARAMÈTRES")
    rcp = st.select_slider("SCÉNARIO RCP", options=["2.6", "4.5", "8.5"], value="4.5")
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea = st.selectbox("ALÉA À SIMULER", ["Aucun", "Inondations", "Glissement de terrain", "Sécheresse"])
    
    intensite = {"2.6": 0.3, "4.5": 0.6, "8.5": 1.0}[rcp] * ((horizon-2020)/80)

# --- INJECTION DU HUD ET DE LA 3D EN UN SEUL BLOC ---
# On crée une interface "Full Screen" à l'intérieur d'un composant
html_code = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    body {{ margin: 0; overflow: hidden; font-family: 'Orbitron', sans-serif; }}
    
    #bg-container {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: url('{BG_URL}') no-repeat center center;
        background-size: cover;
        z-index: -2;
    }}

    #overlay-dark {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0, 10, 20, 0.4);
        z-index: -1;
    }}

    .hud-panel {{
        position: absolute;
        padding: 20px;
        background: rgba(0, 20, 40, 0.8);
        border: 1px solid #00f2ff;
        color: #00f2ff;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
        pointer-events: none;
    }}

    #risk-panel {{ top: 20px; right: 20px; width: 300px; }}
    #status-panel {{ bottom: 20px; left: 20px; width: 400px; }}
    
    .value {{ color: #ff4b4b; font-size: 24px; font-weight: bold; }}
    .label {{ font-size: 10px; text-transform: uppercase; opacity: 0.7; }}
</style>

<div id="bg-container"></div>
<div id="overlay-dark"></div>

<div class="hud-panel" id="risk-panel">
    <div class="label">Impact Économique</div>
    <div class="value">-{round(intensite * 180, 1)} M€</div>
    <br>
    <div class="label">Probabilité Fermeture</div>
    <div style="color: #00f2ff; font-size: 18px;">{round(intensite * 75)}%</div>
</div>

<div class="hud-panel" id="status-panel">
    <div style="border-bottom: 1px solid #00f2ff; margin-bottom: 10px; padding-bottom: 5px;">
        INTERNAL SENSORS [ACTIVE]
    </div>
    <div style="display: flex; justify-content: space-between;">
        <div><span class="label">Temp:</span> {int(15 + intensite * 20)}°C</div>
        <div><span class="label">O2 Level:</span> {round(100 - intensite * 15)}%</div>
        <div><span class="label">Alert:</span> {alea.upper()}</div>
    </div>
</div>

<div id="three-container" style="width: 100vw; height: 100vh;"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('three-container').appendChild(renderer.domElement);

    // Tunnel Central
    const group = new THREE.Group();
    for(let i=0; i<15; i++) {{
        const x = (i-7) * 12;
        const tube = new THREE.Mesh(
            new THREE.CylinderGeometry(5, 5, 11, 32, 1, true),
            new THREE.MeshBasicMaterial({{ color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.3 }})
        );
        tube.rotation.z = Math.PI/2;
        tube.position.x = x;
        group.add(tube);
    }}
    scene.add(group);

    // Simulation d'Aléa
    if ("{alea}" === "Glissement de terrain") {{
        for(let i=0; i<{int(intensite * 150)}; i++) {{
            const rock = new THREE.Mesh(
                new THREE.DodecahedronGeometry(1.5),
                new THREE.MeshBasicMaterial({{ color: 0x888888, wireframe: true }})
            );
            rock.position.set(Math.random()*60-30, 20+Math.random()*40, Math.random()*20-10);
            scene.add(rock);
        }}
    }}

    camera.position.set(0, 10, 100);
    camera.lookAt(0, 0, 0);

    function animate() {{
        requestAnimationFrame(animate);
        group.rotation.y += 0.002;
        renderer.render(scene, camera);
    }}
    animate();
</script>
"""

components.html(html_code, height=800)
