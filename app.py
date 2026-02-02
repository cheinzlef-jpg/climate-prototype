
import streamlit as st
import numpy as np
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(layout="wide", page_title="Tunnel Mont-Blanc X-Ray Simulation")

# --- STYLE CSS HUD ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    .neon-panel {
        border: 1px solid #00f2ff;
        border-radius: 5px;
        background: rgba(0, 242, 255, 0.03);
        padding: 15px;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 22px; font-weight: bold; color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# --- HUB CONTROL (GAUCHE) ---
col_ctrl, col_visu, col_anal = st.columns([0.8, 2, 1])

with col_ctrl:
    st.markdown("### 🎛️ HUB CONTROL")
    rcp = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=2)
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea = st.selectbox("ALÉA À SIMULER", ["Inondations", "Glissement de terrain", "Sécheresse"])
    
    intensite = {"2.6": 1, "4.5": 2, "8.5": 3.5}[rcp] * ((horizon-2020)/50)

# --- VISUALISATION 3D DYNAMIQUE (CENTRE) ---
with col_visu:
    st.markdown(f"### 🔬 SCANNER : {alea.upper()} (10 TRONÇONS)")
    
    # Logique JS pour changer les objets 3D selon l'aléa
    js_alea_logic = ""
    if alea == "Inondations":
        js_alea_logic = f"""
            const waterGeo = new THREE.BoxGeometry(95, {min(intensite*2, 8)}, 10);
            const waterMat = new THREE.MeshBasicMaterial({{ color: 0x0077ff, transparent: true, opacity: 0.6 }});
            const water = new THREE.Mesh(waterGeo, waterMat);
            water.position.y = -5 + ({min(intensite, 4)});
            group.add(water);
        """
    elif alea == "Glissement de terrain":
        js_alea_logic = f"""
            for(let i=0; i<15; i++) {{
                const rockGeo = new THREE.DodecahedronGeometry(Math.random()*2 + 1);
                const rockMat = new THREE.MeshBasicMaterial({{ color: 0x888888, wireframe: true }});
                const rock = new THREE.Mesh(rockGeo, rockMat);
                rock.position.set(-45 + Math.random()*20, -4 + Math.random()*3, Math.random()*6 - 3);
                group.add(rock);
            }}
        """
    elif alea == "Sécheresse":
        js_alea_logic = f"""
            const heatGeo = new THREE.CylinderGeometry(2, 2, 90, 16);
            const heatMat = new THREE.MeshBasicMaterial({{ color: 0xff3300, transparent: true, opacity: {min(intensite/4, 0.8)} }});
            const heatCore = new THREE.Mesh(heatGeo, heatMat);
            heatCore.rotation.z = Math.PI / 2;
            group.add(heatCore);
        """

    three_js_code = f"""
    <div id="container-3d" style="width: 100%; height: 450px; border: 1px solid #00f2ff; background: #000;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth/450, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth * 0.55, 450);
        document.getElementById('container-3d').appendChild(renderer.domElement);

        const group = new THREE.Group();
        
        // 10 Tronçons structurels
        for (let i = 0; i < 10; i++) {{
            const segGeo = new THREE.CylinderGeometry(6, 6, 8, 16, 1, true);
            const segMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.2 }});
            const seg = new THREE.Mesh(segGeo, segMat);
            seg.rotation.z = Math.PI / 2;
            seg.position.x = (i - 4.5) * 10;
            group.add(seg);

            const ringGeo = new THREE.TorusGeometry(6.2, 0.1, 8, 40);
            const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, opacity: 0.5, transparent: true }});
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.y = Math.PI / 2;
            ring.position.x = (i - 4.5) * 10;
            group.add(ring);
        }}

        // Injection de la simulation d'aléa spécifique
        {js_alea_logic}

        scene.add(group);
        camera.position.set(60, 20, 70);
        camera.lookAt(0, 0, 0);

        function animate() {{
            requestAnimationFrame(animate);
            group.rotation.y += 0.002;
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js_code, height=470)

# --- ANALYSE DE RISQUES (DROITE) ---
with col_anal:
    st.markdown("### 📊 ANALYSE")
    st.markdown(f'<div class="neon-panel">', unsafe_allow_html=True)
    st.markdown("<p class='metric-title'>IMPACT ÉCONOMIQUE</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>-{round(intensite * 25, 1)} M€</p>", unsafe_allow_html=True)
    st.write(f"**Court terme :** Rupture fret")
    st.write(f"**Long terme :** Baisse PIB local")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="neon-panel">', unsafe_allow_html=True)
    st.markdown("<p class='metric-title'>DÉGÂTS MATÉRIELS</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>-{round(intensite * 15, 1)} M€</p>", unsafe_allow_html=True)
    st.write(f"**Structure :** {alea}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- STRATÉGIES (BAS) ---
st.markdown("---")
st.markdown("### 🛡️ PLAN D'ADAPTATION")
c1, c2 = st.columns(2)
with c1:
    st.info(f"**Stratégie Immédiate ({alea}) :** Déploiement des unités de secours et monitoring actif des parois.")
with c2:
    st.warning(f"**Investissement Résilience :** {round(intensite * 40)} M€ pour sécurisation structurelle à 5 ans.")
