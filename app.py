import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mont-Blanc 3D X-Ray", layout="wide")

st.title("🚇 Modélisation 3D Dynamique : Tunnel du Mont-Blanc")

# --- INTERFACE DE CONTRÔLE ---
col1, col2, col3 = st.columns(3)
with col1:
    rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"])
with col2:
    annee = st.select_slider("Année", options=[2024, 2050, 2100])
with col3:
    vitesse = st.slider("Vitesse de rotation", 0.0, 0.05, 0.01)

# --- LOGIQUE DE COULEUR (STYLE RAYON X) ---
# Plus le risque est haut, plus le tunnel passe du Cyan au Rouge vif
intensite = 0
if rcp == "8.5" and annee == 2100:
    intensite = 0.8
elif annee == 2050:
    intensite = 0.4

# --- CODE THREE.JS (Le moteur 3D) ---
# On utilise du HTML/JavaScript injecté pour le rendu 3D temps réel
three_js_code = f"""
<div id="container" style="width: 100%; height: 500px; background-color: #050505;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(window.innerWidth, 500);
    document.getElementById('container').appendChild(renderer.domElement);

    // Création du Tunnel (Cylindre creux)
    const geometry = new THREE.CylinderGeometry(5, 5, 100, 32, 1, true);
    const material = new THREE.MeshBasicMaterial({{ 
        color: new THREE.Color({1-intensite}, {0.2}, {intensite}), 
        wireframe: true, 
        transparent: true, 
        opacity: 0.5 
    }});
    const tunnel = new THREE.Mesh(geometry, material);
    tunnel.rotation.z = Math.PI / 2;
    scene.add(tunnel);

    // Ajout de "tronçons" (Anneaux lumineux)
    for (let i = -50; i <= 50; i += 10) {{
        const ringGeo = new THREE.TorusGeometry(5.2, 0.05, 16, 100);
        const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff }});
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.position.x = i;
        ring.rotation.y = Math.PI / 2;
        scene.add(ring);
    }}

    camera.position.z = 20;

    function animate() {{
        requestAnimationFrame(animate);
        tunnel.rotation.y += {vitesse}; // Rotation dynamique
        renderer.render(scene, camera);
    }}
    animate();
</script>
"""

components.html(three_js_code, height=520)

# --- ANALYSE STRATÉGIQUE ---
st.markdown(f"""
### 📊 Rapport d'impact : Tronçon Central
* **Risque thermique :** {"Élevé" if rcp == "8.5" else "Modéré"}
* **Stratégie d'adaptation :** Renforcement de la ventilation par tronçons. 
* **Coût estimé :** {150 if annee == 2100 else 45} M€ 
* **Bénéfice Social :** Maintien de 2000 emplois directs liés au fret.
""")
