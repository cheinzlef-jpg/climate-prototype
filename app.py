import streamlit as st
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Tunnel Mont-Blanc Decision Support")

# --- DESIGN HUD ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    .neon-panel {
        border: 1px solid #00f2ff;
        border-radius: 5px;
        background: rgba(0, 242, 255, 0.05);
        padding: 15px;
        margin-bottom: 10px;
    }
    .hypothese { font-size: 0.85em; color: #aaaaaa; font-style: italic; }
    .metric-value { font-size: 24px; font-weight: bold; color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# --- HUB CONTROL (GAUCHE) ---
col_ctrl, col_visu, col_anal = st.columns([0.8, 2, 1.2])

with col_ctrl:
    st.markdown("### 🎛️ CONTROLE DES FLUX")
    rcp = st.radio("SCÉNARIO RCP", ["2.6", "4.5", "8.5"], index=1)
    horizon = st.select_slider("HORIZON", options=[2024, 2050, 2100], value=2050)
    alea = st.selectbox("ALÉA À SIMULER", ["Inondations", "Glissement de terrain", "Sécheresse"])
    
    h_idx = {2024: 0.2, 2050: 0.6, 2100: 1.0}[horizon]
    r_idx = {"2.6": 0.3, "4.5": 0.6, "8.5": 1.0}[rcp]
    intensite = h_idx * r_idx
    
    # Trafic réaliste : il ne s'arrête pas, il ralentit et s'accumule (congestion)
    vitesse_trafic = max(0.1, 0.5 - (intensite * 0.4))
    densite_trafic = int(5 + (intensite * 15)) # Plus de véhicules bloqués si intensité haute

# --- VISUALISATION 3D (CENTRE) ---
with col_visu:
    st.markdown(f"### 🔬 SIMULATION DE FLUX DÉGRADÉ : {alea.upper()}")
    
    js_alea = ""
    if alea == "Inondations":
        js_alea = f"const h={intensite*5}; const w=new THREE.Mesh(new THREE.BoxGeometry(100,h,12), new THREE.MeshBasicMaterial({{color:0x0077ff,transparent:true,opacity:0.4}})); w.position.y=-6+h/2; group.add(w);"
    elif alea == "Glissement de terrain":
        js_alea = f"for(let i=0;i<{int(intensite*40)};i++){{const r=new THREE.Mesh(new THREE.DodecahedronGeometry(1.2), new THREE.MeshBasicMaterial({{color:0x888888,wireframe:true}})); r.position.set(-50+Math.random()*20,-4.5,Math.random()*8-4); group.add(r);}}"
    elif alea == "Sécheresse":
        js_alea = f"const s=new THREE.Mesh(new THREE.CylinderGeometry({1+intensite*3},{1+intensite*3},100,16), new THREE.MeshBasicMaterial({{color:0xff3300,transparent:true,opacity:{min(intensite,0.5)}}})); s.rotation.z=Math.PI/2; group.add(s);"

    three_js = f"""
    <div id="c3d" style="width: 100%; height: 480px; border: 1px solid #00f2ff; background: #000; position:relative;">
        <div id="render"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth/480, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
        renderer.setSize(window.innerWidth*0.6, 480);
        document.getElementById('render').appendChild(renderer.domElement);

        const group = new THREE.Group();
        const cars = [];

        for(let i=0; i<10; i++) {{
            const x = (i-4.5)*10;
            const t = new THREE.Mesh(new THREE.CylinderGeometry(6,6,9.5,16,1,true), new THREE.MeshBasicMaterial({{color:0x00f2ff,wireframe:true,opacity:0.1,transparent:true}}));
            t.rotation.z=Math.PI/2; t.position.x=x; group.add(t);
        }}

        // Génération du trafic dégradé
        for(let i=0; i<{densite_trafic}; i++) {{
            const c = new THREE.Mesh(new THREE.BoxGeometry(1.5,0.7,0.7), new THREE.MeshBasicMaterial({{color:0xffffff}}));
            c.position.set(Math.random()*100-50, -5.3, Math.random()*4-2);
            cars.push(c); group.add(c);
        }}

        {js_alea}
        scene.add(group);
        camera.position.set(65, 30, 85); camera.lookAt(0,0,0);

        function animate() {{
            requestAnimationFrame(animate);
            group.rotation.y += 0.0005;
            cars.forEach(c => {{
                c.position.x += {vitesse_trafic};
                if(c.position.x > 50) c.position.x = -50;
            }});
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js, height=500)

# --- ANALYSE ÉCONOMIQUE (DROITE) ---
with col_anal:
    st.markdown("### 📈 ANALYSE ÉCONOMIQUE")
    
    # Paramètres de calcul basés sur les données réelles du Tunnel du Mont-Blanc
    flux_journalier = 5000  # Véhicules/jour (Poids lourds + Légers)
    cout_retard_moyen = 120 # €/heure (Coût d'exploitation moyen transporteur)
    perte_peage_jour = 0.8  # M€ (Recettes moyennes journalières)
    
    # Calculs dynamiques basés sur l'intensité de l'aléa
    jours_impact = int(intensite * 45)
    retard_moyen = intensite * 2.5 # Heures de retard générées par la congestion
    
    # Formule : Pertes = (Jours * Perte Péage * %Fermeture) + (Jours * Flux * Retard * Coût/h)
    perte_directe = jours_impact * perte_peage_jour * (0.2 * intensite)
    cout_friction = (jours_impact * flux_journalier * retard_moyen * cout_retard_moyen) / 1000000
    total_impact = perte_directe + cout_friction

    st.markdown(f"""
    <div class="neon-panel">
        <p class="metric-title">Coût Annuel Estimé</p>
        <p class="metric-value">{round(total_impact, 1)} M€/an</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- ENCART D'INFORMATION CLIQUABLE (LES HYPOTHÈSES) ---
    with st.expander("ℹ️ MÉTHODOLOGIE & HYPOTHÈSES"):
        st.markdown(f"""
        <div style="font-size: 0.85em; color: #aaaaaa; border-left: 2px solid #00f2ff; padding-left: 10px;">
        
        **1. Pertes Directes ($C_d$) :**<br>
        Basées sur une perte de $20\%$ du CA journalier durant les {jours_impact} jours de criticité.
        $$C_d = J_i \\times P_j \\times (0.2 \\times I)$$
        
        **2. Coût de Friction Logistique ($C_f$) :**<br>
        Impact du ralentissement sur le fret transalpin. On estime que chaque unité de risque génère {round(retard_moyen, 1)}h de retard.
        $$C_f = \\frac{J_i \\times Flux \\times R_m \\times C_h}{10^6}$$
        
        **3. Paramètres fixes :**
        - Flux : {flux_journalier} véh/j.
        - Coût horaire transport : {cout_retard_moyen} €/h.
        - Valeur temps : Indexée sur le coût d'opportunité logistique.
        </div>
        """, unsafe_allow_html=True)
        
    st.write("**Répartition du risque :**")
    st.progress(min(intensite, 1.0))
    st.caption(f"Probabilité d'incident majeur : {round(intensite * 15, 1)}%")
# --- STRATÉGIES (BAS) ---
st.markdown("---")
st.markdown("### 🛡️ RÉPONSES D'ADAPTATION")

# Logique de plans croisés aléa/horizon
def get_strat(a, h):
    strats = {
        "Inondations": {2024: "Curage accéléré des collecteurs.", 2050: "Pompes automatiques SCADA.", 2100: "Galerie de décharge."},
        "Glissement de terrain": {2024: "Surveillance visuelle.", 2050: "Radars LiDAR infrarouges.", 2100: "Tunnel pare-blocs armé."},
        "Sécheresse": {2024: "Régulation de vitesse thermique.", 2050: "Nébulisation d'eau recyclée.", 2100: "Climatisation géothermique."}
    }
    return strats[a][h]

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="neon-panel"><b>IMMÉDIAT (6m)</b><br>{get_strat(alea, 2024)}</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="neon-panel"><b>STRUCTUREL (2a)</b><br>{get_strat(alea, 2050)}</div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="neon-panel"><b>STRATÉGIQUE (5a)</b><br>{get_strat(alea, 2100)}</div>', unsafe_allow_html=True)
