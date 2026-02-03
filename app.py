import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Mont-Blanc X-Ray : Side View")

# --- STYLE CSS HUD ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    .neon-panel {
        border: 1px solid #00f2ff;
        background: rgba(0, 242, 255, 0.05);
        padding: 15px;
        margin-bottom: 10px;
        font-family: 'Courier New', monospace;
    }
    .metric-value { font-size: 22px; font-weight: bold; color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# --- HUB CONTROL (GAUCHE) ---
col_ctrl, col_visu, col_anal = st.columns([0.8, 2, 1])

with col_ctrl:
    st.markdown("### 🎛️ HUB CONTROL")
    rcp = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=1)
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea = st.selectbox("ALÉA PRIORITAIRE", ["Aucun", "Inondations", "Glissement de terrain", "Sécheresse"])
    
    intensite = {"2.6": 0.3, "4.5": 0.6, "8.5": 1.0}[rcp] * ((horizon-2020)/80)

# --- VISUALISATION 3D : VUE DE PROFIL (CENTRE) ---
with col_visu:
    st.markdown(f"### 🏔️ COUPE GÉOLOGIQUE - {alea.upper()}")
    
    # Logique d'affichage conditionnelle des aléas
    js_alea = ""
    if alea == "Inondations":
        js_alea = f"""
            const water = new THREE.Mesh(
                new THREE.BoxGeometry(120, {intensite * 8}, 15),
                new THREE.MeshBasicMaterial({{color: 0x0077ff, transparent: true, opacity: 0.5}})
            );
            water.position.y = -8 + ({intensite * 4});
            scene.add(water);
        """
    elif alea == "Glissement de terrain":
        js_alea = f"""
            for(let i=0; i<{int(intensite * 100)}; i++) {{
                const rock = new THREE.Mesh(
                    new THREE.DodecahedronGeometry(Math.random() + 0.5),
                    new THREE.MeshBasicMaterial({{color: 0x888888, wireframe: true}})
                );
                rock.position.set(Math.random()*40 - 20, 10 + Math.random()*20, Math.random()*10 - 5);
                scene.add(rock);
            }}
        """
    elif alea == "Sécheresse":
        js_alea = f"""
            const heat = new THREE.Mesh(
                new THREE.CylinderGeometry(8, 8, 120, 32),
                new THREE.MeshBasicMaterial({{color: 0xff3300, transparent: true, opacity: {min(intensite, 0.6)}}})
            );
            heat.rotation.z = Math.PI / 2;
            scene.add(heat);
        """

    three_js_code = f"""
    <div id="side-view" style="width: 100%; height: 500px; border: 1px solid #00f2ff; background: #0b0d12;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth/500, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{antialias: true, alpha: true}});
        renderer.setSize(window.innerWidth * 0.6, 500);
        document.getElementById('side-view').appendChild(renderer.domElement);

        // 1. SOL & MONTAGNE (COUPE)
        const mountainGeo = new THREE.PlaneGeometry(200, 100);
        const mountainMat = new THREE.MeshBasicMaterial({{color: 0x1a1c23, side: THREE.DoubleSide, transparent: true, opacity: 0.8}});
        const mountain = new THREE.Mesh(mountainGeo, mountainMat);
        mountain.position.z = -10;
        scene.add(mountain);

        // 2. TUNNELS (TRONÇONS DE PROFIL)
        const tunnelGroup = new THREE.Group();
        for(let i=0; i<10; i++) {{
            const x = (i-4.5) * 12;
            // Tube principal
            const seg = new THREE.Mesh(
                new THREE.CylinderGeometry(5, 5, 11, 32, 1, true),
                new THREE.MeshBasicMaterial({{color: 0x00f2ff, wireframe: true, opacity: 0.2, transparent: true}})
            );
            seg.rotation.z = Math.PI / 2;
            seg.position.x = x;
            tunnelGroup.add(seg);
            
            // Anneaux de renfort
            const ring = new THREE.Mesh(
                new THREE.TorusGeometry(5.1, 0.1, 16, 100),
                new THREE.MeshBasicMaterial({{color: 0x00f2ff, opacity: 0.6, transparent: true}})
            );
            ring.rotation.y = Math.PI / 2;
            ring.position.x = x;
            tunnelGroup.add(ring);
        }}
        scene.add(tunnelGroup);

        // 3. TRAFIC (PROFIL)
        const cars = [];
        for(let i=0; i<8; i++) {{
            const car = new THREE.Mesh(new THREE.BoxGeometry(2, 0.8, 0.8), new THREE.MeshBasicMaterial({{color: 0xffffff}}));
            car.position.set(Math.random()*100 - 50, -4.2, 0);
            cars.push(car);
            scene.add(car);
        }}

        // 4. INJECTION ALÉA CONDITIONNEL
        {js_alea}

        camera.position.set(0, 5, 80); // VUE DE PROFIL STRICTE
        camera.lookAt(0, 0, 0);

        function animate() {{
            requestAnimationFrame(animate);
            cars.forEach(c => {{
                c.position.x += 0.2;
                if(c.position.x > 60) c.position.x = -60;
            }});
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js_code, height=520)

# --- ANALYSE ÉCONOMIQUE (DROITE) ---
with col_anal:
    st.markdown("### 📊 ANALYSE")
    with st.expander("ℹ️ HYPOTHÈSES DE CALCUL", expanded=True):
        st.write("**Méthode :** Coût de friction logistique.")
        st.latex(r"C = J_{impact} \times (P_{peage} + C_{retard})")
        st.caption("Péage: 0.8M€/j | Retard: 120€/h/véhicule")

    perte = round(intensite * 240, 1)
    st.markdown(f'<div class="neon-panel"><p class="metric-value">-{perte} M€</p><caption>Pertes estimées</caption></div>', unsafe_allow_html=True)

# --- STRATÉGIES (BAS) ---
st.markdown("---")
st.markdown("### 🛡️ RÉPONSE STRATÉGIQUE")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="neon-panel"><b>6 MOIS</b><br>Installation de capteurs piézométriques.</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="neon-panel"><b>2 ANS</b><br>Blindage des voussoirs critiques.</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="neon-panel"><b>5 ANS</b><br>Nouvel émissaire de drainage.</div>', unsafe_allow_html=True)
