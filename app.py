import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(layout="wide", page_title="Mont-Blanc X-Ray v3 - Analyse Aléas")

# --- 1. DESIGN CSS (HUD & INTERFACE) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    .neon-panel {
        border: 2px solid #00f2ff;
        border-radius: 10px;
        padding: 20px;
        background: rgba(0, 242, 255, 0.03);
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.1);
        margin-bottom: 20px;
    }
    h1, h2, h3, h4 { color: #00f2ff !important; font-family: 'Courier New', monospace; }
    .data-label { color: #ff4b4b !important; font-weight: bold; font-size: 1.1em; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #00f2ff; }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR (LOGIQUE DE CALCUL) ---
with st.sidebar:
    st.markdown("### 🎛️ HUD CONTROLS")
    rcp = st.select_slider("SCÉNARIO RCP", options=["2.6", "4.5", "8.5"], value="8.5")
    annee = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)

# Calcul des intensités par aléa
time_factor = (annee - 2024) / 76
risk_secheresse = (3 if rcp == "8.5" else 1.5) * time_factor * 2.5
risk_glissement = (4 if rcp == "8.5" else 2) * time_factor * 3.0
risk_inondation = (3.5 if rcp == "8.5" else 1.8) * time_factor * 4.0
risk_global = (risk_secheresse + risk_glissement + risk_inondation) / 3

# --- 3. SECTION VISUELLE (3D SCANNER) ---
st.markdown("### 🔬 HBB SCANNER STRUCTURAL (MULTI-ALÉA)")
col_main, col_stats = st.columns([2.5, 1])

with col_main:
    # Intégration du code Three.js (Simplifié pour l'exemple)
    three_js_code = f"""
    <div id="tunnel-3d" style="width: 100%; height: 350px; border:1px solid #00f2ff; border-radius:10px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 350, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth * 0.65, 350);
        document.getElementById('tunnel-3d').appendChild(renderer.domElement);

        const geo = new THREE.CylinderGeometry(5, 5, 100, 32, 1, true);
        const mat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.2 }});
        const tunnel = new THREE.Mesh(geo, mat);
        tunnel.rotation.z = Math.PI / 2;
        scene.add(tunnel);
        
        camera.position.z = 40;
        function animate() {{ requestAnimationFrame(animate); tunnel.rotation.y += 0.005; renderer.render(scene, camera); }}
        animate();
    </script>
    """
    components.html(three_js_code, height=360)

with col_stats:
    st.markdown(f'<div class="neon-panel" style="height: 360px;">', unsafe_allow_html=True)
    st.write(f"**DATA LOG - {annee}**")
    st.markdown(f"<p class='data-label'>🌵 SÉCHERESSE : {round(risk_secheresse,1)}/10</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='data-label'>⛰️ GLISSEMENT : {round(risk_glissement,1)}/10</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='data-label'>🌊 INONDATION : {round(risk_inondation,1)}/10</p>", unsafe_allow_html=True)
    st.write("---")
    st.write(f"PROBABILITÉ FERMETURE : {round(risk_global * 10)}%")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. SECTION ANALYSE DES RISQUES (NUANCÉE) ---
st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
st.subheader("📊 ANALYSE D'IMPACT MULTI-CRITÈRES")
tab1, tab2, tab3 = st.tabs(["📉 Économique", "🏗️ Matériel", "🌍 Socio-Politique"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Court Terme (6 mois)", f"-{round(risk_global * 5, 1)}M€", "Fermetures")
    col2.metric("Moyen Terme (2 ans)", f"-{round(risk_global * 22, 1)}M€", "Baisse Fret")
    col3.metric("Long Terme (5 ans)", f"-{round(risk_global * 85, 1)}M€", "Rupture de flux")

with tab2:
    materiel_data = {
        "Aléa": ["Sécheresse", "Glissement", "Inondation"],
        "Dégâts Matériels": ["Surchauffe ventilation / Câbles", "Structure portail / Filets", "Systèmes électriques / Drainage"],
        "Coût Réparation": [f"{round(risk_secheresse*2)}M€", f"{round(risk_glissement*3)}M€", f"{round(risk_inondation*2.5)}M€"]
    }
    st.table(pd.DataFrame(materiel_data))

with tab3:
    st.warning("**Social :** Enclavement des vallées locales et hausse des prix de consommation.")
    st.info("**Politique :** Nécessité d'un nouvel accord inter-gouvernemental pour le financement de la résilience.")
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. ENCART STRATÉGIES D'ADAPTATION ---
st.markdown('<div class="neon-panel" style="border-color: #ff4b4b;">', unsafe_allow_html=True)
st.subheader("🛡️ STRATÉGIES D'ADAPTATION")
col_strat1, col_strat2, col_strat3 = st.columns(3)

with col_strat1:
    st.write("**POUR LA SÉCHERESSE**")
    st.caption("Refroidissement actif par géo-échanges (Utilisation de l'eau froide des glaciers).")
    st.write(f"Ratio C/A : 1:{round(3.5/risk_global, 1)}")

with col_strat2:
    st.write("**POUR LE GLISSEMENT**")
    st.caption("Puits de drainage du permafrost et capteurs LiDAR de mouvements millimétrés.")
    st.write(f"Ratio C/A : 1:{round(4.2/risk_global, 1)}")

with col_strat3:
    st.write("**POUR L'INONDATION**")
    st.caption("Redimensionnement des collecteurs et bassins d'orage aux portails.")
    st.write(f"Ratio C/A : 1:{round(2.8/risk_global, 1)}")
st.markdown('</div>', unsafe_allow_html=True)
