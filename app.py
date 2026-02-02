import streamlit as st
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Mont-Blanc X-Ray Pro v5")

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
        min-height: 100px;
    }
    .budget-text { font-family: monospace; font-size: 18px; color: #00ff00; }
</style>
""", unsafe_allow_html=True)

# --- HUB CONTROL (GAUCHE) ---
col_ctrl, col_visu, col_anal = st.columns([0.8, 2, 1.2])

with col_ctrl:
    st.markdown("### 🎛️ HUD CONTROLS")
    rcp = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=1)
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea = st.selectbox("ALÉA À SIMULER", ["Inondations", "Glissement de terrain", "Sécheresse"])
    
    # Calcul de l'intensité
    h_idx = {2024: 0.2, 2050: 0.6, 2100: 1.0}[horizon]
    r_idx = {"2.6": 0.3, "4.5": 0.6, "8.5": 1.0}[rcp]
    intensite = h_idx * r_idx
    
    # Facteur de ralentissement du trafic
    vitesse_trafic = max(0.05, 0.6 - (intensite * 0.55))

# --- VISUALISATION 3D (CENTRE) ---
with col_visu:
    st.markdown(f"### 🔬 SIMULATION : {alea.upper()}")
    
    # Logique d'aléa pour Three.js
    js_alea = ""
    if alea == "Inondations":
        js_alea = f"const h={intensite*7.5}; const w=new THREE.Mesh(new THREE.BoxGeometry({intensite*105},h,12), new THREE.MeshBasicMaterial({{color:0x0077ff,transparent:true,opacity:0.6}})); w.position.y=-6+h/2; group.add(w);"
    elif alea == "Glissement de terrain":
        js_alea = f"for(let i=0;i<{int(intensite*60)};i++){{const r=new THREE.Mesh(new THREE.DodecahedronGeometry(1.2), new THREE.MeshBasicMaterial({{color:0x888888,wireframe:true}})); r.position.set(-50+Math.random()*({intensite}*90),-4,Math.random()*8-4); group.add(r);}}"
    elif alea == "Sécheresse":
        js_alea = f"const s=new THREE.Mesh(new THREE.CylinderGeometry({1+intensite*5},{1+intensite*5},105,16), new THREE.MeshBasicMaterial({{color:0xff3300,transparent:true,opacity:{min(intensite,0.7)}}})); s.rotation.z=Math.PI/2; group.add(s);"

    three_js = f"""
    <div id="c3d" style="width: 100%; height: 500px; border: 1px solid #00f2ff; background: #000; position:relative;">
        <div style="position:absolute; top:10px; left:10px; color:#00f2ff; font-family:monospace; font-size:11px; border:1px solid #00f2ff; padding:8px; background:rgba(0,0,0,0.7); z-index:10;">
            SYSTEM_STATUS: ACTIVE<br>SECTION_INTEGRITY: {round(100 - (intensite*80))}%<br>TRAFFIC_FLOW: {round(vitesse_trafic*180)} veh/min
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

        // Construction des 10 tronçons + Galeries
        for(let i=0; i<10; i++) {{
            const x = (i-4.5)*10;
            const t = new THREE.Mesh(new THREE.CylinderGeometry(6,6,9.5,16,1,true), new THREE.MeshBasicMaterial({{color:0x00f2ff,wireframe:true,opacity:0.1,transparent:true}}));
            t.rotation.z=Math.PI/2; t.position.x=x; group.add(t);
            
            const s = new THREE.Mesh(new THREE.CylinderGeometry(2,2,9.5,8,1,true), new THREE.MeshBasicMaterial({{color:0x00f2ff,wireframe:true,opacity:0.05,transparent:true}}));
            s.rotation.z=Math.PI/2; s.position.set(x, -9, -12); group.add(s);
        }}

        // Simulation Trafic (Cubes)
        for(let i=0; i<6; i++) {{
            const c = new THREE.Mesh(new THREE.BoxGeometry(1.2,0.6,0.6), new THREE.MeshBasicMaterial({{color:0xffffff}}));
            c.position.set(Math.random()*100-50, -5.5, Math.random()*4-2);
            cars.push(c); group.add(c);
        }}

        {js_alea}
        scene.add(group);
        camera.position.set(65, 30, 85); camera.lookAt(0,0,0);

        function animate() {{
            requestAnimationFrame(animate);
            group.rotation.y += 0.001;
            cars.forEach(c => {{
                c.position.x += {vitesse_trafic};
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
    st.markdown("### 📊 RISK ASSESSMENT")
    perte = round(intensite * 210, 1)
    st.markdown(f'<div class="neon-panel"><p class="metric-title">Pertes Économiques</p><p class="metric-value">-{perte} M€</p></div>', unsafe_allow_html=True)
    
    st.write("**Impact Socio-Politique :**")
    if intensite > 0.6:
        st.error("Rupture de souveraineté logistique : Détours obligatoires de 300km via Fréjus.")
    else:
        st.info("Ralentissements saisonniers gérables via régulation dynamique.")

st.markdown("---")
st.markdown("### 🛡️ PLANS D'ADAPTATION STRATÉGIQUE")

plans = {
    "Inondations": {
        "6m": "Pompes mobiles & capteurs laser.",
        "2a": "Étanchéification des voussoirs.",
        "5a": "Bassin souterrain 50k m³."
    },
    "Glissement de terrain": {
        "6m": "Radars de paroi & filets.",
        "2a": "Ancrages actifs permafrost.",
        "5a": "Galerie pare-bloc lourde."
    },
    "Sécheresse": {
        "6m": "Monitoring câbles HT.",
        "2a": "Brumisation haute pression.",
        "5a": "Échangeurs géothermiques."
    }
}

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="strat-card"><b>COURT TERME (6m)</b><br>{plans[alea]["6m"]}</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="strat-card"><b>MOYEN TERME (2a)</b><br>{plans[alea]["2a"]}</div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="strat-card"><b>LONG TERME (5a)</b><br>{plans[alea]["5a"]}</div>', unsafe_allow_html=True)
