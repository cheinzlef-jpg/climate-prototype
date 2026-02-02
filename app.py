import streamlit as st
import numpy as np
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(layout="wide", page_title="Tunnel Mont-Blanc X-Ray")

# --- STYLE CSS POUR L'EFFET FUTURISTE ---
st.markdown("""
<style>
    body { background-color: #050505; color: #00f2ff; }
    .stApp { background-color: #050505; }
    .reportview-container { background: #050505; }
    h1, h2, h3 { color: #00f2ff; font-family: 'Courier New', Courier, monospace; text-transform: uppercase; letter-spacing: 2px; }
    .metric-card {
        background: rgba(0, 242, 255, 0.05);
        border: 1px solid #00f2ff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (CONTRÔLES) ---
st.sidebar.title("🕹️ DASHBOARD")
rcp = st.sidebar.select_slider("SCÉNARIO RCP", options=["2.6", "4.5", "8.5"], value="4.5")
annee = st.sidebar.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)

# Calcul du facteur de risque
risk_mult = {"2.6": 1, "4.5": 2, "8.5": 4}[rcp] * ((annee - 2020) / 30)

# --- RENDU 3D "RAYON X" (Three.js) ---
# On passe l'intensité du risque au JavaScript pour changer l'opacité du rouge
red_pulse = min(1.0, risk_mult / 4)

three_js_canvas = f"""
<div id="container" style="width: 100%; height: 400px; background: #050505; border: 1px solid #333;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 400, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(window.innerWidth, 400);
    document.getElementById('container').appendChild(renderer.domElement);

    // Tunnel Principal (Wireframe Cyan)
    const geometry = new THREE.CylinderGeometry(5, 5, 100, 32, 10, true);
    const material = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.3 }});
    const tunnel = new THREE.Mesh(geometry, material);
    tunnel.rotation.z = Math.PI / 2;
    scene.add(tunnel);

    // Courbe de Risque Interne (Noyau Rouge)
    const coreGeo = new THREE.CylinderGeometry(2, 2, 100, 20, 10, false);
    const coreMat = new THREE.MeshBasicMaterial({{ color: 0xff0000, wireframe: true, transparent: true, opacity: {red_pulse} }});
    const core = new THREE.Mesh(coreGeo, coreMat);
    core.rotation.z = Math.PI / 2;
    scene.add(core);

    // Anneaux de structure
    for(let i=-50; i<=50; i+=10) {{
        const rGeo = new THREE.TorusGeometry(5.5, 0.1, 8, 50);
        const rMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, transparent: true, opacity: 0.6 }});
        const ring = new THREE.Mesh(rGeo, rMat);
        ring.position.x = i;
        ring.rotation.y = Math.PI / 2;
        scene.add(ring);
    }}

    camera.position.z = 25;
    camera.position.y = 5;
    camera.lookAt(0,0,0);

    function animate() {{
        requestAnimationFrame(animate);
        tunnel.rotation.x += 0.005;
        core.rotation.x -= 0.008;
        renderer.render(scene, camera);
    }}
    animate();
</script>
"""

# --- AFFICHAGE PRINCIPAL ---
col_viz, col_metrics = st.columns([2, 1])

with col_viz:
    st.subheader("Modélisation Structurelle & Aléas")
    components.html(three_js_canvas, height=420)
    
    # Graphique de données (Plotly)
    x = np.linspace(0, 11.6, 100)
    y = np.exp(x/5) * (risk_mult * 0.5) + np.random.normal(0, 0.2, 100)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', line=dict(color='#ff0000', width=2), name="Intensité Aléa"))
    fig.update_layout(
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        height=200,
        xaxis=dict(title="Distance Tunnel (km)", showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_metrics:
    st.subheader("Analyse d'Impact")
    st.markdown(f"""
    <div class="metric-card">
        <p style="color:#ff4b4b; font-weight:bold;">⚠️ RISQUE GLOBAL : {round(risk_mult * 20)}%</p>
        <hr style="border-color:#00f2ff;">
        <p><b>Portail FR :</b> Glissements de terrain (+{round(risk_mult * 10)}%)</p>
        <p><b>Tronçon Central :</b> Stress Thermique (T° roche > 35°C)</p>
        <p><b>Portail IT :</b> Crues torrentielles (Risque Inondation)</p>
    </div>
    <br>
    <div class="metric-card">
        <p style="color:#00f2ff; font-weight:bold;">🛠️ STRATÉGIE ADAPTATION</p>
        <p><b>Coût estimé :</b> {round(risk_mult * 15, 1)} M€</p>
        <p><b>Bénéfice :</b> Maintien du flux transalpin</p>
    </div>
    """, unsafe_allow_html=True)
