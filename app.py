import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Tunnel Mont-Blanc X-Ray v2")

# --- DESIGN CSS : INTERFACE HUD NOIRE & CYAN ---
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
    h1, h2, h3, p { color: #00f2ff !important; font-family: 'Courier New', monospace; }
    .data-label { color: #ff4b4b !important; font-weight: bold; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🎛️ PARAMÈTRES")
    rcp = st.select_slider("SCÉNARIO RCP", options=["2.6", "4.5", "8.5"], value="4.5")
    annee = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)

# --- LOGIQUE DE RISQUE ---
risk_val = {"2.6": 1, "4.5": 2.5, "8.5": 5}[rcp] * ((annee-2020)/40)

# --- MISE EN PAGE ---
col_main, col_stats = st.columns([2.5, 1])

with col_main:
    # --- LE TUNNEL 3D (ASPECT RÉALISTE & SEGMENTÉ) ---
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.markdown("### 🔬 SCANNER STRUCTUREL X-RAY (TEMPS RÉEL)")
    
    three_js_code = f"""
    <div id="tunnel-3d" style="width: 100%; height: 400px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 400, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth * 0.65, 400);
        document.getElementById('tunnel-3d').appendChild(renderer.domElement);

        // Groupe pour tout le tunnel
        const tunnelGroup = new THREE.Group();

        // Création des segments massifs du tunnel
        const segCount = 12;
        const segLength = 10;
        
        for (let i = 0; i < segCount; i++) {{
            // Cylindre principal (paroi)
            const geo = new THREE.CylinderGeometry(8, 8, segLength, 16, 2, true);
            const mat = new THREE.MeshBasicMaterial({{ 
                color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.2 
            }});
            const segment = new THREE.Mesh(geo, mat);
            segment.rotation.z = Math.PI / 2;
            segment.position.x = (i - segCount/2) * segLength;
            tunnelGroup.add(segment);

            // Anneaux de renfort (les "joints" visibles sur l'image)
            const ringGeo = new THREE.TorusGeometry(8.2, 0.3, 8, 32);
            const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, transparent: true, opacity: 0.6 }});
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.position.x = (i - segCount/2) * segLength;
            ring.rotation.y = Math.PI / 2;
            tunnelGroup.add(ring);
        }}
        
        // Courbe de risque rouge au sol
        const roadGeo = new THREE.PlaneGeometry(segCount * segLength, 6);
        const roadMat = new THREE.MeshBasicMaterial({{ 
            color: 0xff4b4b, transparent: true, opacity: Math.min({risk_val}/6, 0.8), side: THREE.DoubleSide 
        }});
        const road = new THREE.Mesh(roadGeo, roadMat);
        road.rotation.x = Math.PI / 2;
        road.position.y = -7.5;
        tunnelGroup.add(road);

        // --- ICONES D'ALERTE CLIGNOTANTES ---
        const alertGeo = new THREE.SphereGeometry(1.5, 16, 16);
        const alertMat = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});
        const alert = new THREE.Mesh(alertGeo, alertMat);
        alert.position.set(-20, 0, 0); // Positionner sur un tronçon
        if ({risk_val} > 2.5) tunnelGroup.add(alert);

        scene.add(tunnelGroup);
        camera.position.set(40, 15, 50);
        camera.lookAt(0, 0, 0);

        function animate() {{
            requestAnimationFrame(animate);
            // Animation de pulsation de l'alerte
            if (alert) {{
                const s = 1 + Math.sin(Date.now() * 0.01) * 0.3;
                alert.scale.set(s, s, s);
                alert.material.opacity = 0.5 + Math.sin(Date.now() * 0.01) * 0.5;
            }}
            tunnelGroup.rotation.y += 0.002; // Rotation lente pour la perspective
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js_code, height=420)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- GRAPHIQUE DE RISQUE (PLOTLY) ---
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    x = np.linspace(0, 11.6, 100)
    y = (np.exp(x/5) * risk_val / 5) + np.abs(np.sin(x)*2)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', line=dict(color='#ff4b4b', width=3)))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=200, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(showgrid=False, title="DISTANCE (KM)"), yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_stats:
    # --- PANNEAU DE DONNÉES ---
    st.markdown('<div class="neon-panel" style="height: 680px;">', unsafe_allow_html=True)
    st.markdown(f"### STATUS : {annee}")
    st.markdown(f"**SCÉNARIO :** RCP {rcp}")
    st.write("---")
    
    st.markdown(f"""
    <p class="data-label">🌡️ THERMIQUE : {round(risk_val * 12, 1)}°C</p>
    <p class="data-label">🏔️ GLISSEMENT : {"CRITIQUE" if risk_val > 4 else "SURVEILLANCE"}</p>
    <p class="data-label">🌊 INONDATION : {round(risk_val * 15)}% PROB.</p>
    <br><br>
    <h4>🛡️ ADAPTATION</h4>
    <p>- Injection résine tronçon 4<br>- Monitoring LiDAR actif<br>- Ventilation forcée niveau 3</p>
    <br>
    <button style="width:100%; border:1px solid #00f2ff; background:none; color:#00f2ff; padding:10px;">
        EXPORT DATA
    </button>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
