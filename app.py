import streamlit as st
import streamlit.components.v1 as components

# 1. Configuration de la page
st.set_page_config(layout="wide", page_title="Mont-Blanc X-Ray Dashboard")

# 2. URL de l'image de fond (Montagne réaliste)
IMG_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1920&q=80"

# 3. Style CSS pour forcer le HUD par-dessus l'image
st.markdown(f"""
<style>
    /* Supprimer les marges Streamlit pour le plein écran */
    .main .block-container {{
        padding: 0;
        max-width: 100%;
    }}
    
    /* Fond de montagne fixe */
    .stApp {{
        background-image: url("{IMG_URL}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Panneaux HUD stylisés */
    .hud-overlay {{
        background: rgba(0, 15, 25, 0.85);
        border: 1px solid #00f2ff;
        border-radius: 4px;
        padding: 20px;
        color: #00f2ff;
        font-family: 'Courier New', monospace;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);
    }}
    
    .metric-value {{ font-size: 28px; font-weight: bold; color: #ff4b4b; text-shadow: 0 0 10px #ff4b4b; }}
</style>
""", unsafe_allow_html=True)

# --- STRUCTURE DES COLONNES ---
col_left, col_mid, col_right = st.columns([1, 1.5, 1])

with col_left:
    st.markdown('<div class="hud-overlay">', unsafe_allow_html=True)
    st.markdown("### 🎛️ SYSTEM CONTROLS")
    rcp = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=1)
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea = st.selectbox("ALÉA À SIMULER", ["Aucun", "Inondations", "Glissement de terrain", "Sécheresse"])
    st.markdown('</div>', unsafe_allow_html=True)

    # Calcul intensité pour le moteur 3D
    intensite = {"2.6": 0.3, "4.5": 0.6, "8.5": 1.0}[rcp] * ((horizon-2020)/80)

with col_right:
    st.markdown('<div class="hud-overlay">', unsafe_allow_html=True)
    st.markdown("### 📊 RISK ASSESSMENT")
    perte = round(intensite * 150, 1)
    st.markdown(f'<p class="metric-value">-{perte} M€</p>', unsafe_allow_html=True)
    st.write(f"PROBABILITÉ FERMETURE : {round(intensite*80)}%")
    st.write(f"FLUIDITÉ TRAFIC : {round(100 - intensite*60)}%")
    
    st.markdown("---")
    st.write("**INTERNAL CONDITIONS**")
    st.write(f"TEMP. INT : {int(15 + intensite*20)}°C")
    st.write(f"AIR QUALITY : {'CRITIQUE' if intensite > 0.7 else 'NORMAL'}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MOTEUR 3D (CENTRE) ---
with col_mid:
    # On prépare les objets en fonction de l'aléa
    js_alea = ""
    if alea == "Inondations":
        js_alea = f"const h={intensite*5}; const w=new THREE.Mesh(new THREE.BoxGeometry(120,h,10), new THREE.MeshBasicMaterial({{color:0x0077ff,transparent:true,opacity:0.4}})); w.position.y=-6+h/2; scene.add(w);"
    elif alea == "Glissement de terrain":
        js_alea = f"for(let i=0;i<{int(intensite*100)};i++){{ const r=new THREE.Mesh(new THREE.DodecahedronGeometry(0.8), new THREE.MeshBasicMaterial({{color:0x888888,wireframe:true}})); r.position.set(Math.random()*40-20,10+Math.random()*15,Math.random()*6-3); scene.add(r); }}"
    elif alea == "Sécheresse":
        js_alea = f"const s=new THREE.Mesh(new THREE.CylinderGeometry(8,8,120,32), new THREE.MeshBasicMaterial({{color:0xff3300,transparent:true,opacity:{min(intensite, 0.5)}}})); s.rotation.z=Math.PI/2; scene.add(s);"

    three_js = f"""
    <div id="three-container" style="width: 100%; height: 600px; margin-top: 50px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth/600, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{antialias: true, alpha: true}});
        renderer.setSize(window.innerWidth * 0.45, 600);
        document.getElementById('three-container').appendChild(renderer.domElement);

        // Tunnel Principal (Vue en coupe de profil)
        const group = new THREE.Group();
        for(let i=0; i<15; i++) {{
            const x = (i-7)*10;
            const tube = new THREE.Mesh(new THREE.CylinderGeometry(4.5,4.5,9.8,32,1,true), new THREE.MeshBasicMaterial({{color:0x00f2ff,wireframe:true,transparent:true,opacity:0.2}}));
            tube.rotation.z=Math.PI/2; tube.position.x=x;
            group.add(tube);
            const ring = new THREE.Mesh(new THREE.TorusGeometry(4.6,0.1,16,100), new THREE.MeshBasicMaterial({{color:0x00f2ff,opacity:0.6,transparent:true}}));
            ring.rotation.y=Math.PI/2; ring.position.x=x;
            group.add(ring);
        }}
        
        // Trafic
        const cars = [];
        for(let i=0; i<8; i++) {{
            const c = new THREE.Mesh(new THREE.BoxGeometry(2,0.8,0.8), new THREE.MeshBasicMaterial({{color:0xffffff}}));
            c.position.set(Math.random()*120-60, -4.2, 0);
            cars.push(c); scene.add(c);
        }}

        scene.add(group);
        {js_alea}
        
        camera.position.set(0, 5, 80);
        camera.lookAt(0, 0, 0);

        function animate() {{
            requestAnimationFrame(animate);
            cars.forEach(c => {{ 
                c.position.x += {0.15 + (1-intensite)*0.2}; 
                if(c.position.x > 60) c.position.x = -60; 
            }});
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js, height=650)

# --- STRATÉGIES (BAS) ---
st.markdown("---")
st.markdown("### 🛡️ ADAPTATION STRATEGY")
c1, c2, c3 = st.columns(3)
with c1: st.info("**6 MOIS** : Monitoring LiDAR actif")
with c2: st.warning("**2 ANS** : Digues de protection")
with c3: st.error("**5 ANS** : Nouveau tunnel de service")
