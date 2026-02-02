import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components

# Configuration pour un affichage plein écran "Dashboard"
st.set_page_config(layout="wide", page_title="Tunnel Mont-Blanc X-Ray")

# --- DESIGN CSS : INTERFACE FUTURISTE ---
st.markdown("""
<style>
    /* Fond noir profond */
    .stApp {
        background-color: #050505;
    }
    
    /* Cadre néon pour les sections */
    .neon-panel {
        border: 2px solid #00f2ff;
        border-radius: 15px;
        padding: 20px;
        background: rgba(0, 242, 255, 0.02);
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.1);
        margin-bottom: 20px;
    }

    /* Texte futuriste */
    h1, h2, h3, p {
        color: #00f2ff !important;
        font-family: 'Orbitron', sans-serif; /* Style tech si dispo */
    }

    .data-label {
        color: #ff4b4b !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR STYLE HUD ---
with st.sidebar:
    st.markdown("### CONFIGURATION HUD")
    rcp = st.select_slider("SCÉNARIO RCP", options=["2.6", "4.5", "8.5"], value="4.5")
    annee = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    
# --- LOGIQUE DE CALCUL ---
risk_level = {"2.6": 1.5, "4.5": 3.0, "8.5": 6.5}[rcp] * ((annee-2020)/50)

# --- MISE EN PAGE PRINCIPALE ---
col_left, col_right = st.columns([2.5, 1])

with col_left:
    # --- PANNEAU DU TUNNEL 3D ---
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.markdown("### 🌀 VISUALISATION STRUCTURELLE X-RAY")
    
    # Intégration du tunnel 3D en fil de fer (Three.js)
    three_js = f"""
    <div id="3d-tunnel" style="width: 100%; height: 350px; background: transparent;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/350, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth * 0.6, 350);
        document.getElementById('3d-tunnel').appendChild(renderer.domElement);

        const geo = new THREE.CylinderGeometry(5, 5, 100, 32, 10, true);
        const mat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.3 }});
        const tunnel = new THREE.Mesh(geo, mat);
        tunnel.rotation.z = Math.PI / 2;
        scene.add(tunnel);

        // Courbe de risque rouge interne
        const coreGeo = new THREE.TorusGeometry(3, 0.05, 16, 100);
        const coreMat = new THREE.MeshBasicMaterial({{ color: 0xff4b4b }});
        
        camera.position.set(40, 15, 30);
        camera.lookAt(0, 0, 0);

        function animate() {{
            requestAnimationFrame(animate);
            tunnel.rotation.x += 0.002;
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js, height=360)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- PANNEAU DU GRAPHIQUE ---
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.markdown("### 📈 PROFIL DES ALÉAS (MULTI-TEMP.)")
    
    x = np.linspace(0, 11.6, 100)
    y = np.sin(x) + (risk_level)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', line=dict(color='#ff4b4b', width=3), name="VULNÉRABILITÉ"))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0,r=0,t=0,b=0), height=250,
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # --- PANNEAU INFOS & STRATÉGIE ---
    st.markdown('<div class="neon-panel" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown(f"## HORIZON : {annee}")
    st.markdown(f"### SCÉNARIO : RCP {rcp}")
    st.write("---")
    
    st.markdown(f"""
    <p class="data-label">RISQUE THERMIQUE : {"ÉLEVÉ" if risk_level > 4 else "MODÉRÉ"}</p>
    <p class="data-label">RISQUE GLISSEMENT : {"ÉLEVÉ" if risk_level > 5 else "STABLE"}</p>
    <p class="data-label">RISQUE INONDATION : {"CRITIQUE" if annee == 2100 else "SURVEILLANCE"}</p>
    
    <br><br>
    <h4>🛡️ STRATÉGIES D'ADAPTATION</h4>
    <p style="color: white !important; font-size: 0.9em;">
    - Renforcement des voûtes (Tronçon 4-7)<br>
    - Monitoring fibre optique temps réel<br>
    - Ventilation cryogénique active
    </p>
    """, unsafe_allow_html=True)
    
    st.button("GÉNÉRER RAPPORT ÉCONOMIQUE (C/A)")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ANALYSE ---
st.markdown('<div class="neon-panel" style="text-align: center;">', unsafe_allow_html=True)
st.write("ANALYSE SYNTHÉTIQUE : La dégradation du permafrost en zone d'entrée FR nécessite une intervention immédiate dès 2045.")
st.markdown('</div>', unsafe_allow_html=True)
