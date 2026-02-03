Python
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Mont-Blanc X-Ray | Composite View")

# --- BACKGROUND IMAGE & GLOBAL CSS ---
st.markdown("""
<style>
    .stApp {
        background-image: url("https://lh3.googleusercontent.com/rd-gg-dl/AOI_d_9O978yByu5l-x_JTtl2NCMx9oW-XJuEBex1VB7vpzEmJ-QEoDOlipTGqbhoydCr2Wr3m97j5Bm4XTT7mhMud0qacD1W2yDl4dtcJh6uyegXSuE7-MUPJJGc87mUXXorjGSOo-DRCw9XsXozACdFjV1vLWqPcp3Quf_Dtwow6raRuYc-fcHtgJXVEBacmaJj4TY94Mx56mSjsNlDriqO5MdV07yui35VxGxuOS3Px7aqu6VKeGiZEJi3a911akwL_-upyQ0lfg66i5Ip8L6oUK6lRBxmwxqErKMRk9EMh2FNbz-ShgMfFf65aq6hB6Cn9ShK0GDl4F0WLn2w4KpunJqle6uBOQ6LaacBFO3Y-ryuIP0pxVHdo0EDixWntCmNVoyj5HK3-TPsaAmmhXxV6Fjihrv_WKDUf-rMdQiluvJBJ1qTkPICJm4LgTosfwVNvacfdJDzMOa_FiFzsrVlMSt-GAGqnxhFamb0SySqZvClFQnSdKvGOGTMe_JKF0CxE4CHI4EXknwEkoEPdeKE3fakSRFfQxXxQXTeD5FTr0a5OYvfn0MqEYahrdsu6VeGteOYUUdKhnrRDs01oPTdDFJ2MdnSwDG41lvfacd52GoMfu1-QAafTTMdDoS_7CPYhEBYzVrRFLoJXPnWjX2jqUjsoKr3h-GnANiWcwdtZPUthC746JOcFLuDid4B_wW4bOIj1VZ3zREE9qSQLVfUttyL-NedmLttjHfj0Lr2JpsgA0KHuHWJf9PM_bJoxCKXPb0L4fhcG4tu1v95BIUMLX0Tjl9YC7TBYkidNL7yF07WVevB2akUPU6CuVKHX_dFIYro15UJYDRxhU29XPhzEkV1dEryIfbczQsEtF1SbpEIyu2GHduMNAur5d3DA2W1NzwHy2Ec0SEVkb3EZoFr8mGzVuT-7iCXo7uItDxz6Lb5H6Y9B6ZyciqItHTBfMKS9g0wOwms8qW2AutuLMO1JD2NwCdIO8_l90zEzzVVrJ2SDjRiTt6gISGsi9urLIjUpaqhKoPxgQWdj87l91lSGp2VnMBV5rC6weUraSOPBMJd3gqetW0ScbFTmu1shhOluHRz9jbRji2XMpeXPW3jvZMP6YrAZ4uVMhJMSwLFhktPR42Oqzs0nlOEPxYI4v_gJd4wSoYowcqMzSM5uFz9Lfoj_E_xBeNa8Sp7akwl3dM9mhIe9RfPTZxGZ6PY5XGnEKdF4Z2sIMzJPVBCuno3ZlQ4jX7BQ=s1024-rj?authuser=1"); /* REMPLACEZ PAR L'URL DE VOTRE IMAGE DE MONTAGNE */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #e0f7fa; /* Couleur de texte claire pour le contraste */
    }
    /* Style pour les panneaux HUD */
    .neon-panel, .strat-panel {
        background: rgba(0, 0, 0, 0.7); /* Fond semi-transparent foncé */
        border: 1px solid #00f2ff;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 0 8px #00f2ff; /* Effet néon */
        font-family: 'Consolas', monospace;
        color: #00f2ff;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #ff4b4b; /* Rouge pour les valeurs critiques */
    }
    .stRadio > label, .stSelectbox > label, .stSlider > label {
        color: #00f2ff;
    }
</style>
""", unsafe_allow_html=True)

# --- HUB CONTROL (LEFT) ---
col_ctrl, col_spacer, col_anal = st.columns([0.8, 1.2, 1])

with col_ctrl:
    st.markdown("### 🎛️ SYSTEM CONTROLS", unsafe_allow_html=True)
    rcp = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=1, key="rcp_control")
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050, key="horizon_control")
    alea = st.selectbox("ALÉA À SIMULER", ["Aucun", "Inondations", "Glissement de terrain", "Sécheresse"], key="alea_control")
    
    intensite = {"2.6": 0.3, "4.5": 0.6, "8.5": 1.0}[rcp] * ((horizon - 2020) / 80) # Normalize for horizon
    
    # Traffic simulation based on intensity
    traffic_speed = max(0.05, 0.3 - (intensite * 0.25)) # Slower if higher intensity
    num_cars = int(5 + (intensite * 10)) # More cars (congestion) if higher intensity

# --- 3D VISUALIZATION (CENTER - transparent overlay) ---
# This part is a placeholder for the 3D scene that will be absolutely positioned over the background
with col_spacer: # Use col_spacer to fill the center area where 3D will be
    st.markdown("<h3></h3>", unsafe_allow_html=True) # Just a small spacer to align
    
    js_alea_code = ""
    if alea == "Inondations":
        js_alea_code = f"""
            const waterHeight = {intensite * 8};
            const water = new THREE.Mesh(
                new THREE.BoxGeometry(100, waterHeight, 30), // Width, Height, Depth
                new THREE.MeshBasicMaterial({{color: 0x0077ff, transparent: true, opacity: 0.5}})
            );
            water.position.set(0, -5 + (waterHeight / 2), 0); // Adjust Y for water level
            scene.add(water);
        """
    elif alea == "Glissement de terrain":
        js_alea_code = f"""
            for(let i=0; i<{int(intensite * 80)}; i++) {{
                const rock = new THREE.Mesh(
                    new THREE.DodecahedronGeometry(Math.random() * 1.5 + 0.5),
                    new THREE.MeshBasicMaterial({{color: 0x888888, wireframe: true}})
                );
                // Position rocks over the tunnel entrance area
                rock.position.set(Math.random()*40 - 20, 10 + Math.random()*20, Math.random()*15 - 7.5);
                scene.add(rock);
            }}
        """
    elif alea == "Sécheresse":
        js_alea_code = f"""
            const heatRadius = 5 + ({intensite * 8});
            const heatOpacity = Math.min({intensite * 0.8}, 0.7);
            const heat = new THREE.Mesh(
                new THREE.CylinderGeometry(heatRadius, heatRadius, 100, 32),
                new THREE.MeshBasicMaterial({{color: 0xff3300, transparent: true, opacity: heatOpacity}})
            );
            heat.rotation.z = Math.PI / 2;
            heat.position.set(0, 0, 0); // Centered
            scene.add(heat);
        """

    three_js_code = f"""
    <div id="threejs-container" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('threejs-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 700, 0.1, 1000); // Adjusted for side-profile
        const renderer = new THREE.WebGLRenderer({{antialias: true, alpha: true}});
        renderer.setSize(window.innerWidth * 0.7, 600); // Adjust size for better fit
        container.appendChild(renderer.domElement);

        // Tunnel sections (wireframe tubes for X-ray effect)
        const tunnelGroup = new THREE.Group();
        for(let i=0; i<10; i++) {{
            const x = (i-4.5) * 12; // Spread sections along X-axis for length
            
            // Main tunnel (larger)
            const mainTunnelGeo = new THREE.CylinderGeometry(6, 6, 11, 32, 1, true);
            const mainTunnelMat = new THREE.MeshBasicMaterial({{color: 0x00f2ff, wireframe: true, opacity: 0.2, transparent: true}});
            const mainTunnel = new THREE.Mesh(mainTunnelGeo, mainTunnelMat);
            mainTunnel.rotation.z = Math.PI / 2; // Rotate to be horizontal
            mainTunnel.position.set(x, 0, 0); // Position along the tunnel's length
            tunnelGroup.add(mainTunnel);

            // Secondary tunnel/service gallery (smaller, below)
            const secondaryTunnelGeo = new THREE.CylinderGeometry(2, 2, 11, 16, 1, true);
            const secondaryTunnelMat = new THREE.MeshBasicMaterial({{color: 0x00f2ff, wireframe: true, opacity: 0.1, transparent: true}});
            const secondaryTunnel = new THREE.Mesh(secondaryTunnelGeo, secondaryTunnelMat);
            secondaryTunnel.rotation.z = Math.PI / 2;
            secondaryTunnel.position.set(x, -8, 0); // Position below main tunnel
            tunnelGroup.add(secondaryTunnel);
        }}
        scene.add(tunnelGroup);

        // Traffic simulation (simple boxes)
        const cars = [];
        for(let i=0; i<{num_cars}; i++) {{
            const car = new THREE.Mesh(new THREE.BoxGeometry(2, 1, 1), new THREE.MeshBasicMaterial({{color: 0xffffff}}));
            car.position.set(Math.random()*120 - 60, -5, Math.random()*5 - 2.5); // Spread cars
            cars.push(car);
            scene.add(car);
        }}

        {js_alea_code} // Inject aléa logic here

        // Camera position for a side/profile view
        camera.position.set(0, 5, 80); // Looking at the center of the tunnel from a distance
        camera.lookAt(0, 0, 0);

        function animate() {{
            requestAnimationFrame(animate);
            tunnelGroup.rotation.y += 0.0005; // Gentle rotation for 3D feel
            cars.forEach(c => {{
                c.position.x += {traffic_speed};
                if(c.position.x > 60) c.position.x = -60;
            }});
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js_code, height=600) # Height for the 3D canvas

# --- RISK ASSESSMENT (RIGHT) ---
with col_anal:
    st.markdown("### 📊 RISK ASSESSMENT", unsafe_allow_html=True)
    perte_eco = round(intensite * 250, 1) # Example calculation
    prob_fermeture = round(intensite * 60) # Example percentage
    traffic_fluidity = round(100 - (intensite * 70)) # Example percentage
    
    st.markdown(f"""
    <div class="neon-panel">
        <p class="metric-value">IMPACT ÉCONOMIQUE: -{perte_eco} M€</p>
        <p>PROBABILITÉ FERMETURE: {prob_fermeture}%</p>
        <p>TRAFIC FLUIDITÉ: {traffic_fluidity}%</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ INTERNAL CONDITIONS", expanded=True):
        temp_ext = 5 + (intensite * 15) # Example temp
        temp_int = 15 + (intensite * 10) # Example temp
        st.markdown(f"""
        <p style="color:#00f2ff;">TEMPÉRATURE EXT: {round(temp_ext)}°C</p>
        <p style="color:#00f2ff;">TEMPÉRATURE INT: {round(temp_int)}°C</p>
        <p style="color:#00f2ff;">QUALITÉ AIR: {'CRITIQUE' if intensite > 0.7 else 'MODÉRÉE'}</p>
        """, unsafe_allow_html=True)

# --- ADAPTATION STRATEGIES (BOTTOM) ---
st.markdown("---")
st.markdown("### 🛡️ STRATÉGIES D'ADAPTATION", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="strat-panel"><b>COURT TERME (6 MOIS)</b><br>Activation Géophones & Filets Dynamiques</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="strat-panel"><b>MOYEN TERME (2 ANS)</b><br>Construction Digue Défense</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="strat-panel"><b>LONG TERME (5 ANS)</b><br>Tunnel de Service Élargi</div>', unsafe_allow_html=True)
