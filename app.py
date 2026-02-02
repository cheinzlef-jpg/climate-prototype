import streamlit as st
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Mont-Blanc X-Ray Pro")

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
    .strat-card {
        border-left: 4px solid #ff4b4b;
        background: rgba(255, 75, 75, 0.05);
        padding: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- HUB CONTROL (GAUCHE) ---
col_ctrl, col_visu, col_anal = st.columns([0.8, 2, 1.2])

with col_ctrl:
    st.markdown("### 🎛️ HUD CONTROLS")
    rcp = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=1)
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea = st.selectbox("ALÉA À SIMULER", ["Inondations", "Glissement de terrain", "Sécheresse"])
    
    h_idx = {2024: 0.2, 2050: 0.6, 2100: 1.0}[horizon]
    r_idx = {"2.6": 0.3, "4.5": 0.6, "8.5": 1.0}[rcp]
    intensite = h_idx * r_idx
    trafic_vitesse = max(0, 0.5 - (intensite * 0.5)) # Le trafic ralentit si le risque monte

# --- VISUALISATION 3D PRO (CENTRE) ---
with col_visu:
    st.markdown(f"### 🔬 SIMULATION : {alea.upper()}")
    
    # Logique d'aléa pour JS
    js_alea = ""
    if alea == "Inondations":
        js_alea = f"const h={intensite*7}; const w=new THREE.Mesh(new THREE.BoxGeometry({intensite*100},h,12), new THREE.MeshBasicMaterial({{color:0x0077ff,transparent:true,opacity:0.6}})); w.position.y=-6+h/2; group.add(w);"
    elif alea == "Glissement de terrain":
        js_alea = f"for(let i=0;i<{int(intensite*50)};i++){{const r=new THREE.Mesh(new THREE.DodecahedronGeometry(1), new THREE.MeshBasicMaterial({{color:0x888888,wireframe:true}})); r.position.set(-50+Math.random()*({intensite}*80),-4,Math.random()*6-3); group.add(r);}}"
    elif alea == "Sécheresse":
        js_alea = f"const s=new THREE.Mesh(new THREE.CylinderGeometry({1+intensite*4},{1+intensite*4},100,16), new THREE.MeshBasicMaterial({{color:0xff3300,transparent:true,opacity:{min(intensite,0.7)}}})); s.rotation.z=Math.PI/2; group.add(s);"

    three_js = f"""
    <div id="c3d" style="width: 100%; height: 500px; border: 1px solid #00f2ff; background: #000; position:relative;">
        <div style="position:absolute; top:10px; left:10px; color:#00f2ff; font-family:monospace; font-size:10px; border:1px solid #00f2ff; padding:5px; background:rgba(0,0,0,0.5);">
            OBJECT: TUNNEL_MB_CORE<br>SECTIONS: 10/10 ACTIVE<br>TRAFFIC_FLOW: {round(trafic_vitesse*200)}%
        </div>
        <div id="render"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth/500, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
        renderer.setSize(window.innerWidth*0.6, 500);
        document.getElementById('render').appendChild(renderer.domElement);

        const group = new THREE.Group();
        const cars = [];

        // 10 Tronçons + Tunnel de service
        for(let i=0; i<10; i++) {{
            const x = (i-4.5)*10;
            // Tunnel Principal
            const t = new THREE.Mesh(new THREE.CylinderGeometry(6,6,9,16,1,true), new THREE.MeshBasicMaterial({{color:0x00f2ff,wireframe:true,opacity:0.1,transparent:true}}));
            t.rotation.z=Math.PI/2; t.position.x=x; group.add(t);
            // Tunnel Service
            const s = new THREE.Mesh(new THREE.CylinderGeometry(2,2,9,8,1,true), new THREE.MeshBasicMaterial({{color:0x00f2ff,wireframe:true,opacity:0.05,transparent:true}}));
            s.rotation.z=Math.PI/2; s.position.set(x, -8, -10); group.add(s);
        }}

        // Trafic
        for(let i=0; i<5; i++) {{
            const c = new THREE.Mesh(new THREE.BoxGeometry(1,0.5,0.5), new THREE.MeshBasicMaterial({{color:0xffffff}}));
            c.position.x = Math.random()*100 - 50;
            c.position.y = -5.5;
            cars.push(c); group.add(c);
        }}

        {js_alea}
        scene.add(group);
        camera.position.set(60, 25, 80); camera.lookAt(0,0,0);

        function animate() {{
            requestAnimationFrame(animate);
            group.rotation.y += 0.001;
            // Simulation trafic
            cars.forEach(c => {{
                c.position.x += {trafic_vitesse};
                if(c.position.x > 50) c.position.x = -50;
            }});
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js, height=520)

# --- ANALYSE & STRATÉGIES (DROITE / BAS) ---
with col_anal:
    st.markdown("### 📊 RISK REPORT")
    st.markdown(f'<div class="neon-panel"><p class="metric-value">-{round(intensite*180,1)} M€</p><caption style="color:#00f2ff">Pertes cumulées (5 ans)</caption></div>', unsafe_allow_html=True)
    
    st.write("**Impact Politique :**")
    st.caption("Forte pression sur les accords de transit bilatéraux et report modal forcé.")

st.markdown("---")
st.markdown("### 🛡️ PLANS D'ADAPTATION PAR TEMPORALITÉ")

# Logique de plans dynamiques
plans = {
    "Inondations": {
        "6 mois": "Déploiement de pompes mobiles et capteurs de niveau d'eau laser.",
        "2 ans": "Redimensionnement des collecteurs et étanchéification des joints de voussoirs.",
        "5 ans": "Création d'un bassin de rétention souterrain de 50,000 m³."
    },
    "Glissement de terrain": {
        "6 mois": "Installation de radars de mouvement de paroi et filets dynamiques.",
        "2 ans": "Ancrages actifs de 30m dans le permafrost et barrières pare-blocs.",
        "5 ans": "Construction d'une galerie de protection lourde (pare-avalanche/bloc)."
    },
    "Sécheresse": {
        "6 mois": "Ajustement des seuils d'alerte thermique et monitoring des câbles HT.",
        "2 ans": "Installation d'un système de nébulisation haute pression pour refroidissement.",
        "5 ans": "Refonte totale de la centrale de ventilation avec échangeurs géothermiques."
    }
}

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="strat-card"><b>COURT TERME (6m)</b><br><small>{plans[alea]["6 mois"]}</small></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="strat-card"><b>MOYEN TERME (2a)</b><br><small>{plans[alea]["2 ans"]}</small></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="strat-card"><b>LONG TERME (5a)</b><br><sma
