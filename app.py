import streamlit as st
import numpy as np
import streamlit.components.v1 as components

# Configuration Dashboard
st.set_page_config(layout="wide", page_title="Mont-Blanc X-Ray V3")

# --- STYLE CSS : INTERFACE HUD & BULLES ---
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    
    /* Panneau Principal */
    .hud-container {
        border: 2px solid #00f2ff;
        border-radius: 10px;
        background: rgba(0, 242, 255, 0.02);
        position: relative;
        padding: 10px;
        margin-bottom: 20px;
    }

    /* Étiquettes / Bulles d'info */
    .info-bubble {
        position: absolute;
        border: 1px solid #00f2ff;
        background: rgba(0, 0, 0, 0.8);
        color: #00f2ff;
        padding: 5px 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.8em;
        border-radius: 4px;
        pointer-events: none;
        white-space: nowrap;
    }

    /* Ligne de liaison */
    .connector {
        position: absolute;
        background: #00f2ff;
        height: 1px;
        transform-origin: left center;
    }

    h3 { color: #00f2ff !important; font-family: 'Courier New', monospace; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIQUE DE RISQUE (Via Sidebar) ---
with st.sidebar:
    st.title("📟 PARAMÈTRES")
    rcp = st.select_slider("SCÉNARIO RCP", options=["2.6", "4.5", "8.5"], value="8.5")
    annee = st.select_slider("ANNÉE", options=[2024, 2050, 2100], value=2050)

# Intensité pour le code JS
risk_score = {"2.6": 1.2, "4.5": 2.8, "8.5": 5.0}[rcp] * ((annee-2020)/30)

# --- INTERFACE PRINCIPALE ---
st.markdown("### HBB SCANNER STRUCTURAL X-RAY (TEMPS RÉEL)")

# Le conteneur HTML/JS qui dessine le tunnel ET les bulles
hud_html = f"""
<div style="position: relative; width: 100%; height: 500px; border: 2px solid #00f2ff; border-radius: 10px; overflow: hidden; background: #050505;">
    
    <div id="three-container" style="width: 100%; height: 100%;"></div>

    <div id="labels-overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
        <div class="info-bubble" style="top: 20%; left: 15%; border-color: #ff4b4b; color: #ff4b4b;">
            Glissement de terrain (Risk {round(risk_score * 0.8, 1)})
        </div>
        <div class="info-bubble" style="top: 60%; left: 55%;">
            Stress Thermique (Critique)
        </div>
        <div class="info-bubble" style="top: 40%; left: 75%;">
            Infiltration H2O (Zone 8)
        </div>
    </div>

    <style>
        .info-bubble {{
            position: absolute;
            border: 1px solid #00f2ff;
            background: rgba(0, 0, 0, 0.7);
            color: #00f2ff;
            padding: 4px 8px;
            font-family: monospace;
            font-size: 12px;
            box-shadow: 0 0 10px rgba(0,242,255,0.3);
        }}
    </style>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / 500, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(window.innerWidth, 500);
    document.getElementById('three-container').appendChild(renderer.domElement);

    // Construction du Tunnel Segmenté
    const tunnelGroup = new THREE.Group();
    const segments = 15;
    for (let i = 0; i < segments; i++) {{
        const geometry = new THREE.CylinderGeometry(6, 6, 8, 32, 1, true);
        const material = new THREE.MeshBasicMaterial({{ 
            color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.15 
        }});
        const segment = new THREE.Mesh(geometry, material);
        segment.rotation.z = Math.PI / 2;
        segment.position.x = (i - segments/2) * 8.5;
        tunnelGroup.add(segment);

        // Anneaux Structurels
        const ringGeo = new THREE.TorusGeometry(6.1, 0.1, 8, 40);
        const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, transparent: true, opacity: 0.4 }});
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.position.x = (i - segments/2) * 8.5;
        ring.rotation.y = Math.PI / 2;
        tunnelGroup.add(ring);
    }}

    // Sol de risque (Lame rouge)
    const roadGeo = new THREE.PlaneGeometry(130, 8);
    const roadMat = new THREE.MeshBasicMaterial({{ 
        color: 0xff4b4b, transparent: true, opacity: Math.min({risk_score}/10, 0.7), side: THREE.DoubleSide 
    }});
    const road = new THREE.Mesh(roadGeo, roadMat);
    road.rotation.x = Math.PI / 2;
    road.position.y = -5.8;
    tunnelGroup.add(road);

    // Points d'alerte (Sphères pulsantes)
    const alertGeo = new THREE.SphereGeometry(1.2, 16, 16);
    const alertMat = new THREE.MeshBasicMaterial({{ color: 0xff4b4b }});
    const p1 = new THREE.Mesh(alertGeo, alertMat);
    p1.position.set(-35, -2, 0);
    tunnelGroup.add(p1);

    const p2 = new THREE.Mesh(alertGeo, alertMat);
    p2.position.set(10, 0, 0);
    tunnelGroup.add(p2);

    scene.add(tunnelGroup);
    camera.position.set(60, 20, 80);
    camera.lookAt(0, 0, 0);

    function animate() {{
        requestAnimationFrame(animate);
        tunnelGroup.rotation.y += 0.001; // Rotation très lente
        
        // Effet de pulsation sur les points d'alerte
        const s = 1 + Math.sin(Date.now() * 0.005) * 0.2;
        p1.scale.set(s,s,s);
        p2.scale.set(s,s,s);
        
        renderer.render(scene, camera);
    }}
    animate();
</script>
"""

components.html(hud_html, height=520)

# --- ANALYSE TECHNIQUE (TEXTE DU BAS) ---
st.markdown("### Analyse de structure (linéaire)")
st.code(f"""
// LOG_SYSTEM: SCAN_COMPLETE
// SECTEUR_FR: RISQUE GLISSEMENT [MODE:{'CRITIQUE' if risk_score > 3 else 'STABLE'}]
// SECTEUR_IT: PRESSION HYDROSTATIQUE [VAL:{round(risk_score * 12, 2)} bar]
// MAINTENANCE: PRÉVENTION NIVEAU {'4' if rcp == '8.5' else '2'} ACTIVÉE
""", language="javascript")
