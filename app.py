import streamlit as st
import numpy as np
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(layout="wide", page_title="Mont-Blanc X-Ray Ultimate")

# --- DESIGN CSS : HUD AVANCÉ ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    .neon-panel {
        border: 2px solid #00f2ff;
        border-radius: 10px;
        background: rgba(0, 242, 255, 0.03);
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.1);
        padding: 15px;
        margin-bottom: 15px;
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #ff4b4b; }
    .metric-label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 🎛️ HUD CONTROLS")
    rcp = st.select_slider("SCÉNARIO RCP", options=["2.6", "4.5", "8.5"], value="8.5")
    annee = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)

# Logique de calcul
time_progress = (annee - 2024) / 76
risk_lvl = {"2.6": 1.5, "4.5": 3, "8.5": 5}[rcp] * time_progress

# --- INTERFACE PRINCIPALE ---
col_left, col_right = st.columns([2.5, 1])

with col_left:
    st.markdown("### 🔬 HBB STRUCTURAL SCANNER (ACTIVE MODE)")
    
    # HTML/JS : Le Tunnel Massif + Bulles d'Info
    hud_html = f"""
    <div style="position: relative; width: 100%; height: 500px; border: 2px solid #00f2ff; border-radius: 10px; background: #000;">
        <div id="three-canvas" style="width: 100%; height: 100%;"></div>
        
        <div style="position: absolute; top: 15%; left: 10%; padding: 8px; border: 1px solid #ff4b4b; background: rgba(0,0,0,0.8); color: #ff4b4b; font-family: monospace; font-size: 12px;">
            📍 PORTAIL FR<br>Glissement: {round(risk_lvl*2, 1)}% risk
        </div>
        <div style="position: absolute; bottom: 20%; left: 45%; padding: 8px; border: 1px solid #00f2ff; background: rgba(0,0,0,0.8); color: #00f2ff; font-family: monospace; font-size: 12px;">
            ⚠️ SECTION CENTRALE<br>Stress Thermique: {round(25 + risk_lvl*5, 1)}°C
        </div>
        <div style="position: absolute; top: 30%; right: 10%; padding: 8px; border: 1px solid #ff4b4b; background: rgba(0,0,0,0.8); color: #ff4b4b; font-family: monospace; font-size: 12px;">
            🌊 PORTAIL IT<br>Saturation: {round(risk_lvl*1.5, 1)} bar
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth/500, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth * 0.65, 500);
        document.getElementById('three-canvas').appendChild(renderer.domElement);

        const tunnelGroup = new THREE.Group();
        const segs = 15;
        for (let i = 0; i < segs; i++) {{
            const geo = new THREE.CylinderGeometry(7, 7, 8, 32, 1, true);
            const mat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.1 }});
            const s = new THREE.Mesh(geo, mat);
            s.rotation.z = Math.PI / 2;
            s.position.x = (i - segs/2) * 9;
            tunnelGroup.add(s);

            const rGeo = new THREE.TorusGeometry(7.2, 0.15, 8, 40);
            const rMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, transparent: true, opacity: 0.5 }});
            const ring = new THREE.Mesh(rGeo, rMat);
            ring.position.x = (i - segs/2) * 9;
            ring.rotation.y = Math.PI / 2;
            tunnelGroup.add(ring);
        }}

        // Lame de risque rouge au sol
        const road = new THREE.Mesh(
            new THREE.PlaneGeometry(140, 8),
            new THREE.MeshBasicMaterial({{ color: 0xff4b4b, transparent: true, opacity: {min(risk_lvl/5, 0.7)}, side: THREE.DoubleSide }})
        );
        road.rotation.x = Math.PI / 2; road.position.y = -6.8;
        tunnelGroup.add(road);

        scene.add(tunnelGroup);
        camera.position.set(50, 20, 80);
        camera.lookAt(0,0,0);

        function animate() {{
            requestAnimationFrame(animate);
            tunnelGroup.rotation.y += 0.002;
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(hud_html, height=520)

with col_right:
    # --- PANEL D'ANALYSE DYNAMIQUE ---
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.markdown("#### ⚡ RISQUES TEMPS RÉEL")
    
    st.markdown(f'<div class="metric-label">Impact Économique (6m)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">-{round(risk_lvl * 4, 1)} M€</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="metric-label">Dégâts Matériels (2y)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">-{round(risk_lvl * 15, 1)} M€</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="metric-label">Probabilité Rupture (5y)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{round(risk_lvl * 18)}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="neon-panel" style="border-color: #ff4b4b;">', unsafe_allow_html=True)
    st.markdown("#### 🛡️ STRATÉGIE ADAPTATION")
    if risk_lvl > 3:
        st.write("🔴 **ALERTE CRITIQUE**")
        st.caption("Investissement massif requis : Galeries de drainage + Ventilation cryogénique.")
    else:
        st.write("🟢 **STABLE**")
        st.caption("Maintenance prédictive : Capteurs LiDAR et monitoring fibre optique.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MATRICE DES ALÉAS (EN BAS) ---
st.markdown("### 📊 MATRICE NUANCÉE DES ALÉAS")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.write("**⛰️ GLISSEMENT**")
    st.write(f"Intensité: {round(risk_lvl*1.5,1)}/10")
    st.caption("Impact: Entrées tunnel bloquées.")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.write("**🌊 INONDATION**")
    st.write(f"Intensité: {round(risk_lvl*1.2,1)}/10")
    st.caption("Impact: Systèmes électriques HS.")
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.write("**🌵 SÉCHERESSE**")
    st.write(f"Intensité: {round(risk_lvl*0.8,1)}/10")
    st.caption("Impact: Stress thermique ventilation.")
    st.markdown('</div>', unsafe_allow_html=True)
