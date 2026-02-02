import streamlit as st
import numpy as np
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(layout="wide", page_title="Tunnel X-Ray Simulator v4")

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
    .metric-value { font-size: 22px; font-weight: bold; color: #ff4b4b; }
    .metric-title { font-size: 10px; text-transform: uppercase; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# --- HUB CONTROL (GAUCHE) ---
col_ctrl, col_visu, col_anal = st.columns([0.8, 2, 1])

with col_ctrl:
    st.markdown("### 🎛️ HUB CONTROL")
    rcp = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=1)
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea = st.selectbox("ALÉA À SIMULER", ["Inondations", "Glissement de terrain", "Sécheresse"])
    
    # Calcul de l'intensité (0.1 à 1.0)
    h_idx = {2024: 0.2, 2050: 0.6, 2100: 1.0}[horizon]
    r_idx = {"2.6": 0.3, "4.5": 0.6, "8.5": 1.0}[rcp]
    intensite_globale = h_idx * r_idx # Valeur entre 0.06 et 1.0

# --- VISUALISATION 3D (CENTRE) ---
with col_visu:
    st.markdown(f"### 🔬 SCANNER : {alea.upper()} (IMPACT DYNAMIQUE)")
    
    # Logique JS : L'impact visuel dépend de intensite_globale
    js_alea_logic = ""
    
    if alea == "Inondations":
        # La hauteur de l'eau monte ET s'étend sur plus de tronçons
        hauteur = intensite_globale * 7
        largeur = intensite_globale * 100
        js_alea_logic = f"""
            const waterGeo = new THREE.BoxGeometry({largeur}, {hauteur}, 12);
            const waterMat = new THREE.MeshBasicMaterial({{ color: 0x0077ff, transparent: true, opacity: 0.6 }});
            const water = new THREE.Mesh(waterGeo, waterMat);
            water.position.y = -6 + ({hauteur}/2);
            group.add(water);
        """
    elif alea == "Glissement de terrain":
        # Plus d'intensité = plus de rochers sur plus de tronçons
        nb_rochers = int(intensite_globale * 40)
        js_alea_logic = f"""
            for(let i=0; i<{nb_rochers}; i++) {{
                const rockGeo = new THREE.DodecahedronGeometry(Math.random()*1.5 + 0.5);
                const rockMat = new THREE.MeshBasicMaterial({{ color: 0x888888, wireframe: true }});
                const rock = new THREE.Mesh(rockGeo, rockMat);
                // Les rochers s'étalent sur l'axe X selon l'intensité
                rock.position.set(-50 + Math.random()*({intensite_globale}*80), -4 + Math.random()*3, Math.random()*6 - 3);
                group.add(rock);
            }}
        """
    elif alea == "Sécheresse":
        # Le noyau de chaleur devient plus large et plus opaque
        opacite = min(intensite_globale, 0.9)
        rayon = 1 + (intensite_globale * 4)
        js_alea_logic = f"""
            const heatGeo = new THREE.CylinderGeometry({rayon}, {rayon}, 100, 16);
            const heatMat = new THREE.MeshBasicMaterial({{ color: 0xff3300, transparent: true, opacity: {opacite} }});
            const heatCore = new THREE.Mesh(heatGeo, heatMat);
            heatCore.rotation.z = Math.PI / 2;
            group.add(heatCore);
        """

    three_js_code = f"""
    <div id="container-3d" style="width: 100%; height: 450px; border: 1px solid #00f2ff; background: #000;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth/450, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth * 0.6, 450);
        document.getElementById('container-3d').appendChild(renderer.domElement);

        const group = new THREE.Group();
        
        // 10 Tronçons structurels
        for (let i = 0; i < 10; i++) {{
            const segGeo = new THREE.CylinderGeometry(6, 6, 9, 16, 1, true);
            const segMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, wireframe: true, transparent: true, opacity: 0.15 }});
            const seg = new THREE.Mesh(segGeo, segMat);
            seg.rotation.z = Math.PI / 2;
            seg.position.x = (i - 4.5) * 10;
            group.add(seg);

            const ringGeo = new THREE.TorusGeometry(6.1, 0.15, 8, 40);
            const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f2ff, opacity: 0.6, transparent: true }});
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.y = Math.PI / 2;
            ring.position.x = (i - 4.5) * 10;
            group.add(ring);
        }}

        {js_alea_logic}

        scene.add(group);
        camera.position.set(60, 25, 80);
        camera.lookAt(0, 0, 0);

        function animate() {{
            requestAnimationFrame(animate);
            group.rotation.y += 0.002;
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js_code, height=470)

# --- ANALYSE DE RISQUES (DROITE) ---
with col_anal:
    st.markdown("### 📊 ANALYSE")
    impact_eco = round(intensite_globale * 150, 1)
    
    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.markdown("<p class='metric-title'>Dommages Économiques Totaux</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='metric-value'>-{impact_eco} M€</p>", unsafe_allow_html=True)
    st.write(f"**Criticité :** {'HAUTE' if intensite_globale > 0.6 else 'MODÉRÉE'}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="neon-panel">', unsafe_allow_html=True)
    st.markdown("<p class='metric-title'>Impact Social & Politique</p>", unsafe_allow_html=True)
    st.write(f"Risque d'enclavement : {round(intensite_globale * 100)}%")
    st.write("Détour fret via Fréjus requis.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- STRATÉGIES (BAS) ---
st.markdown("---")
st.markdown("### 🛡️ PLAN D'ADAPTATION")
c1, c2, c3 = st.columns(3)
with c1:
    st.info("**Court Terme (6 mois)** : Monitoring fibre optique et capteurs de pression temps réel.")
with c2:
    st.warning("**Moyen Terme (2 ans)** : Renforcement des joints d'étanchéité et système de pompage d'urgence.")
with c3:
    st.error("**Long Terme (5 ans)** : Construction d'un tunnel de secours ou d'une galerie de dérivation.")
