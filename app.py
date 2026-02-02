import streamlit as st
import numpy as np
import streamlit.components.v1 as components
import pandas as pd

# Configuration plein écran
st.set_page_config(layout="wide", page_title="Tunnel Mont-Blanc X-Ray HUD")

# --- DESIGN CSS : INTERFACE FUTURISTE ---
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
    .metric-title { font-size: 10px; text-transform: uppercase; color: #00f2ff; opacity: 0.8; }
    .metric-value { font-size: 20px; font-weight: bold; color: #ff4b4b; }
    .stSelectbox label, .stSlider label { color: #00f2ff !important; }
</style>
""", unsafe_allow_html=True)

# --- LOGIQUE DE CALCUL DES RISQUES ---
def calculate_risks(rcp, horizon, alea):
    h_factor = {2024: 0.1, 2050: 0.5, 2100: 1.0}[horizon]
    rcp_factor = {"2.6": 1.2, "4.5": 2.5, "8.5": 5.0}[rcp]
    
    base = h_factor * rcp_factor
    
    # Pondération par aléa
    impacts = {
        "Inondations": {"eco": base * 12, "mat": base * 8, "soc": "Évacuation portail IT"},
        "Sécheresse": {"eco": base * 5, "mat": base * 15, "soc": "Stress thermique ventilation"},
        "Glissement de terrain": {"eco": base * 20, "mat": base * 30, "soc": "Enclavement Vallée Arve"}
    }
    return impacts[alea], base

# --- MISE EN PAGE : 3 COLONNES ---
col_ctrl, col_visu, col_anal = st.columns([0.7, 2, 1])

# 1. HUB CONTROL (GAUCHE)
with col_ctrl:
    st.markdown("### 🎛️ HUB CONTROL")
    rcp_choice = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=1)
    horizon_choice = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea_choice = st.selectbox("ALÉA PRIORITAIRE", ["Inondations", "Sécheresse", "Glissement de terrain"])
    
    impact_data, raw_risk = calculate_risks(rcp_choice, horizon_choice, alea_choice)
    
    st.markdown(f"""
    <div class="neon-panel">
        <p class="metric-title">Niveau de Menace</p>
        <p class="metric-value">{round(raw_risk * 20)}%</p>
    </div>
    """, unsafe_allow_html=True)

# 2. VISUALISATION 3D (CENTRE)
with col_visu:
    st.markdown(f"### 🔬 SCANNER X-RAY : {alea_choice.upper()}")
    
    # Couleur de la bulle selon l'aléa
    color_hex = "#ff4b4b" if raw_risk > 2 else "#00f2ff"
    
    hud_html = f"""
    <div style="position: relative; width: 100%; height: 450px; border: 1px solid #00f2ff; background: #000;">
        <div id="three-container" style="width: 100%; height: 100%;"></div>
        
        <div style="position: absolute; top: 20%; left: 15%; border: 1px solid {color_hex}; padding: 10px; background: rgba(0,0,0,0.8); color: {color_hex}; font-family: monospace; font-size: 11px;">
            <b>{alea_choice.upper()} DETECTED</b><br>Intensity: {round(raw_risk, 1)}<br>Status: Critical
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth/450, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth * 0.5, 450);
        document.getElementById('three-container').appendChild(renderer.domElement);

        const group = new THREE.Group();
        for (let i = 0; i < 12; i++) {{
            const geo = new THREE.CylinderGeometry(6, 6, 8, 32, 1, true);
            const mat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.15 }});
            const seg = new THREE.Mesh(geo, mat);
            seg.rotation.z = Math.PI / 2;
            seg.position.x = (i - 6) * 9;
            group.add(seg);

            const rGeo = new THREE.TorusGeometry(6.2, 0.2, 8, 40);
            const rMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, transparent: true, opacity: 0.5 }});
            const ring = new THREE.Mesh(rGeo, rMat);
            ring.position.x = (i - 6) * 9;
            ring.rotation.y = Math.PI / 2;
            group.add(ring);
        }}
        
        // Plan de risque rouge
        const road = new THREE.Mesh(new THREE.PlaneGeometry(120, 8), new THREE.MeshBasicMaterial({{ color: 0xff4b4b, transparent: true, opacity: {min(raw_risk/6, 0.8)}, side: THREE.DoubleSide }}));
        road.rotation.x = Math.PI/2; road.position.y = -5.8;
        group.add(road);

        scene.add(group);
        camera.position.set(50, 20, 70); camera.lookAt(0,0,0);
        function animate() {{ requestAnimationFrame(animate); group.rotation.y += 0.002; renderer.render(scene, camera); }}
        animate();
    </script>
    """
    components.html(hud_html, height=470)

# 3. ANALYSES DE RISQUES (DROITE)
with col_anal:
    st.markdown("### 📊 ANALYSE")
    
    with st.expander("📉 ÉCONOMIQUE", expanded=True):
        st.write(f"**Court (6m) :** -{round(impact_data['eco']*0.2, 1)} M€")
        st.write(f"**Moyen (2a) :** -{round(impact_data['eco']*1.5, 1)} M€")
        st.write(f"**Long (5a) :** -{round(impact_data['eco']*5, 1)} M€")
        
    with st.expander("🏗️ MATÉRIEL", expanded=True):
        st.write(f"**Dégâts :** {round(impact_data['mat'], 1)} M€")
        st.caption("Focus : Structures portails et systèmes de pompage.")

    with st.expander("🌍 SOCIO-POLITIQUE", expanded=True):
        st.markdown(f"<p style='color:white;'>{impact_data['soc']}</p>", unsafe_allow_html=True)
        st.caption("Risque de tension diplomatique FR-IT accrue.")

# --- 4. ENCART STRATÉGIES (BAS) ---
st.markdown("---")
st.markdown("### 🛡️ STRATÉGIES D'ADAPTATION")

s_col1, s_col2 = st.columns(2)

with s_col1:
    st.markdown(f'<div class="neon-panel" style="border-color: #ff4b4b;">', unsafe_allow_html=True)
    st.write("**RÉPONSE IMMÉDIATE (COURT TERME)**")
    if alea_choice == "Inondations":
        st.write("- Activation pompes haute capacité\n- Pose de batardeaux mobiles")
    elif alea_choice == "Sécheresse":
        st.write("- Limitation vitesse fret\n- Injection azote refroidissement")
    else:
        st.write("- Purge préventive des versants\n- Monitoring LiDAR H24")
    st.markdown('</div>', unsafe_allow_html=True)

with s_col2:
    st.markdown(f'<div class="neon-panel">', unsafe_allow_html=True)
    st.write("**RÉSILIENCE STRUCTURELLE (LONG TERME)**")
    st.write(f"- Investissement estimé : {round(impact_data['mat']*3, 1)} M€")
    st.write("- Création de galeries de dérivation spécifiques")
    st.write("- Refonte totale du pacte de gestion bilatérale")
    st.markdown('</div>', unsafe_allow_html=True)
