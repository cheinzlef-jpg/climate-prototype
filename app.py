import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(layout="wide", page_title="Industrial Resilience Command Center")

st.markdown("""
<style>
    .stApp { background-color: #010203; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #05080a; border-right: 1px solid #00f2ff; }
    .info-card { background: rgba(0, 20, 35, 0.9); border: 1px solid #00f2ff; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    .metric-value { font-size: 2.2em; font-weight: bold; text-shadow: 0 0 10px #00f2ff; }
    .status-ok { color: #00ff64; }
    .status-warn { color: #ffc800; text-shadow: 0 0 10px #ffc800; }
    .status-critical { color: #ff3232; font-weight: bold; text-shadow: 0 0 15px #ff3232; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

# --- 2. HUB DE CONTRÔLE (SIDEBAR) ---
with st.sidebar:
    st.title("🛡️ HUB RESILIENCE")
    tab = st.radio("SÉLECTION VUE", ["🖥️ Simulation 3D", "ℹ️ Méthodologie"])
    st.divider()
    
    if tab == "🖥️ Simulation 3D":
        st.subheader("📡 Scénario Climatique")
        alea = st.selectbox("Type d'Aléa", ["Hors Crise", "Inondation Majeure", "Sécheresse Critique"])
        rcp = st.select_slider("Trajectoire RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon = st.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"], value="2050")
        
        st.divider()
        st.subheader("🛠️ Stratégies d'Adaptation")
        cat_strat = st.selectbox("Catégorie", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horiz_strat = st.select_slider("Échéance", options=["Court Terme", "Moyen Terme", "Long Terme"])
        
        mode_cine = st.checkbox("🎬 Rotation Cinématique")

        # Logique de calcul du risque (0-10)
        risk_val = 0 if alea == "Hors Crise" else (3 if horizon == "Actuel" else (6 if horizon == "2050" else 9))
        if rcp == "8.5" and alea != "Hors Crise": risk_val += 1
    else:
        risk_val = 0

# --- 3. DONNÉES MÉTIER ---
strategies = {
    "Physique": {"Court Terme": "Batardeaux amovibles.", "Moyen Terme": "Surélévation pompes.", "Long Terme": "Digue béton périmétrale."},
    "Systémique": {"Court Terme": "Protocoles délestage.", "Moyen Terme": "Micro-grid solaire.", "Long Terme": "Cycle REUT intégral."},
    "Gouvernance": {"Court Terme": "Audit assurance.", "Moyen Terme": "Alerte IoT IA.", "Long Terme": "Délocalisation stratégique."},
    "R&D": {"Court Terme": "Jumeau Numérique.", "Moyen Terme": "Matériaux auto-cicatrisants.", "Long Terme": "Bio-filtration thermique."}
}

# --- 4. MOTEUR DE RENDU 3D ---
import streamlit as st
import plotly.graph_objects as go
import numpy as np

def create_complex_view(risk_score, angle=1.0):
    fig = go.Figure()

    # --- 1. LOGIQUE DE STYLE (COULEURS DYNAMIQUES) ---
    def get_style(vulnerabilite):
        if alea == "Hors Crise": 
            return "#00f2ff", "rgba(0, 242, 255, 0.2)" # Bleu Cyan
        impact = vulnerabilite + risk_score
        if impact < 7:   return "#00ff64", "rgba(0, 255, 100, 0.3)" # Vert
        elif impact < 11: return "#ffc800", "rgba(255, 200, 0, 0.4)" # Orange
        else:             return "#ff3232", "rgba(255, 50, 50, 0.5)" # Rouge

    # --- 2. GÉNÉRATEUR DE FORMES (PLEINES + TRANSPARENTES) ---
    def add_asset(x, y, z, dx, dy, dz, r, shape_type, vulne, name):
        c_line, c_fill = get_style(vulne)
        
        if shape_type == "tank": # Cylindre large (Décanteurs / Clarificateurs)
            theta = np.linspace(0, 2*np.pi, 32)
            fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), 
                                     y=np.outer(y+r*np.sin(theta), np.ones(2)),
                                     z=np.outer(np.ones(32), [z, z+dz]), 
                                     colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.6, name=name))
            fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(32, z+dz), 
                                       mode='lines', line=dict(color=c_line, width=4), showlegend=False))

        elif shape_type == "tower": # Cylindre haut (Digesteur / Silo)
            theta = np.linspace(0, 2*np.pi, 20)
            fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), 
                                     y=np.outer(y+r*np.sin(theta), np.ones(2)),
                                     z=np.outer(np.ones(20), [z, z+dz]), 
                                     colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.7, name=name))
            fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(20, z+dz), 
                                       mode='lines', line=dict(color=c_line, width=3), showlegend=False))

        elif shape_type == "block": # Rectangles (Bassins / HUB)
            fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x]*2, y=[y, y, y+dy, y+dy]*2, z=[z]*4+[z+dz]*4,
                                    i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                    color=c_fill, opacity=0.6, name=name))
            # Wireframe pour le contour
            edges = [[0,1,2,3,0], [4,5,6,7,4], [0,4], [1,5], [2,6], [3,7]]
            for s in edges:
                fig.add_trace(go.Scatter3d(x=[[x,x+dx,x+dx,x,x,x+dx,x+dx,x][i] for i in s],
                                           y=[[y,y,y+dy,y+dy,y,y,y+dy,y+dy][i] for i in s],
                                           z=[[z,z,z,z,z+dz,z+dz,z+dz,z+dz][i] for i in s],
                                           mode='lines', line=dict(color=c_line, width=2), showlegend=False))

    # --- 3. DESSIN DES ROUTES (CONNEXIONS) ---
    route_style = dict(color="rgba(150, 150, 150, 0.4)", width=15)
    # Route principale
    fig.add_trace(go.Scatter3d(x=[-8, 12], y=[0, 0], z=[-0.05, -0.05], mode='lines', line=route_style, showlegend=False))
    # Accès secondaires
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[-8, 8], z=[-0.05, -0.05], mode='lines', line=route_style, showlegend=False))

    # --- 4. IMPLANTATION STEP (1 structure par typologie) ---
    # PRÉTRAITEMENT
    add_asset(-6, -4, 0, 3, 2, 1.5, 0, "block", 5, "Dégrillage & Dessablage")
    
    # PRIMAIRE
    add_asset(-5, 4, 0, 0, 0, 1.2, 2.5, "tank", 2, "Décanteur Primaire")
    
    # SECONDAIRE (Bassin Aération)
    add_asset(2, 4, 0, 6, 3, 1.5, 0, "block", 3, "Bassins Boues Activées")
    
    # CLARIFICATION
    add_asset(8, -4, 0, 0, 0, 1.2, 3.0, "tank", 2, "Clarificateur Final")
    
    # TRAITEMENT DES BOUES
    add_asset(-1, -6, 0, 0, 0, 5, 1.8, "tower", 4, "Digesteur (Méthaniseur)")
    add_asset(4, -6, 0, 2, 2, 4, 0.8, "tower", 6, "Silo Stockage Boues")
    
    # UNITÉ TECHNIQUE & HUB (CRITIQUE)
    add_asset(0, 0.5, -1.2, 2.5, 2.5, 2, 0, "block", 9, "Poste Électrique & SCADA")
    add_asset(4, 0.5, 0, 2, 2, 1.5, 0, "block", 7, "Atelier Déshydratation")

    # --- 5. EFFET INONDATION ---
    if alea == "Inondation Majeure" and risk_score > 0:
        water_level = -0.8 + (risk_score * 0.15)
        fig.add_trace(go.Mesh3d(x=[-10, 15, 15, -10], y=[-10, -10, 10, 10], z=[water_level]*4, 
                               color="rgba(0, 120, 255, 0.3)", opacity=0.5))

    # --- 6. MISE EN PAGE ---
    fig.update_layout(
        scene=dict(
            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=1.8*np.cos(angle), y=1.8*np.sin(angle), z=1.2)),
            aspectratio=dict(x=1.5, y=1, z=0.5)
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), height=800
    )
    return fig

    # --- GÉNÉRATEUR DE FORMES AVANCÉES ---
    def add_asset(x, y, z, dx, dy, dz, r, shape_type, vulne, name):
        c_line, c_fill = get_style(vulne)
        
        if shape_type == "tower":  # Tour de process (Cylindre haut)
            theta = np.linspace(0, 2*np.pi, 20)
            fig.add_trace(go.Surface(x=np.outer(x+r*np.cos(theta), np.ones(2)), 
                                     y=np.outer(y+r*np.sin(theta), np.ones(2)),
                                     z=np.outer(np.ones(20), [z, z+dz]), 
                                     colorscale=[[0, c_fill], [1, c_fill]], showscale=False, opacity=0.5))
            fig.add_trace(go.Scatter3d(x=x+r*np.cos(theta), y=y+r*np.sin(theta), z=np.full(20, z+dz), 
                                       mode='lines', line=dict(color=c_line, width=4), name=name))

        elif shape_type == "hangar": # Entrepôt avec toit en pente
            # Base
            fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                                    y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                                    z=[z, z, z, z, z+dz*0.6, z+dz*0.6, z+dz*0.6, z+dz*0.6],
                                    color=c_fill, opacity=0.5, i=[7,0,0,0], j=[3,4,1,2], k=[0,7,2,3]))
            # Toit
            fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x, x+dx/2], 
                                    y=[y, y, y+dy, y+dy, y+dy/2], 
                                    z=[z+dz*0.6, z+dz*0.6, z+dz*0.6, z+dz*0.6, z+dz],
                                    color=c_line, opacity=0.7))

        elif shape_type == "block": # Bloc technique standard
            fig.add_trace(go.Mesh3d(x=[x, x+dx, x+dx, x]*2, y=[y, y, y+dy, y+dy]*2, z=[z]*4+[z+dz]*4,
                                    color=c_fill, opacity=0.5, name=name))
            fig.add_trace(go.Scatter3d(x=[x, x+dx, x+dx, x, x], y=[y, y, y+dy, y+dy, y], z=[z+dz]*5, 
                                       mode='lines', line=dict(color=c_line, width=3), showlegend=False))

    # --- DESSIN DU SITE (7 Assets avec vulnérabilités différentes) ---
    # Ordre : x, y, z, dx, dy, dz, r, type, vulne, nom
    add_asset(-3, -3, 0, 0, 0, 4, 1.2, "tower", 3, "Unité de Craquage")
    add_asset(3, -3, 0, 2.5, 2.5, 1.5, 0, "hangar", 4, "Entrepôt Logistique")
    add_asset(-3, 2, 0, 0, 0, 2, 1.8, "tower", 2, "Réservoir Eau")
    add_asset(2, 2, -1.0, 1.5, 1.5, 1.2, 0, "block", 9, "Data Center (Sous-sol)") # TRÈS VULNÉRABLE
    add_asset(6, -2, 0, 1.2, 4, 1.0, 0, "block", 5, "Bureaux Administratifs")
    add_asset(0, 0, 0, 0, 0, 5, 0.6, "tower", 6, "Cheminée d'Évent")
    add_asset(5, 4, 0, 2, 2, 3, 0, "hangar", 7, "Maintenance")

    # --- SOL & GRILLE ---
    gx, gy = np.meshgrid(np.linspace(-6, 10, 10), np.linspace(-6, 8, 10))
    fig.add_trace(go.Scatter3d(x=gx.flatten(), y=gy.flatten(), z=np.full(100, -0.1), 
                               mode='markers', marker=dict(size=2, color="rgba(0, 242, 255, 0.3)"), showlegend=False))

    # --- EFFET VISUEL D'INONDATION ---
    if alea == "Inondation Majeure" and risk_score > 0:
        z_water = -0.5 + (risk_score * 0.12)
        fig.add_trace(go.Mesh3d(x=[-6, 10, 10, -6], y=[-6, -6, 8, 8], z=[z_water]*4, 
                               color="rgba(0, 100, 255, 0.3)", opacity=0.4, name="Niveau d'eau"))

    # --- CONFIGURATION CAMÉRA ---
    fig.update_layout(
        scene=dict(
            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=1.8*np.cos(angle), y=1.8*np.sin(angle), z=1.3)),
            aspectratio=dict(x=1.2, y=1, z=0.4)
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), height=700
    )
    return fig

    # --- ÉLÉMENTS DÉCORATIFS (GRILLE AU SOL) ---
    grid_range = np.linspace(-5, 10, 15)
    for g in grid_range:
        fig.add_trace(go.Scatter3d(x=[g, g], y=[-5, 10], z=[-1, -1], mode='lines', line=dict(color="rgba(0, 242, 255, 0.1)", width=1), showlegend=False))
        fig.add_trace(go.Scatter3d(x=[-5, 10], y=[g, g], z=[-1, -1], mode='lines', line=dict(color="rgba(0, 242, 255, 0.1)", width=1), showlegend=False))

    # --- INFRASTRUCTURE ---
    add_advanced_asset(-2, -2, -0.5, 0, 0, 2, 1.8, "tank", 2, "Stockage Brut")
    add_advanced_asset(3, -1, -0.5, 0, 0, 1.5, 1.5, "tank", 3, "Filtration")
    add_advanced_asset(0, 4, -0.5, 4, 3, 2, 0, "factory", 6, "Unité de Commande")
    add_advanced_asset(6, 0, -1.2, 2, 2, 1, 0, "factory", 9, "Poste Électrique HT") # TRÈS BAS ET VULNÉRABLE

    # --- RÉSEAU DE FLUX (ANIMÉ VISUELLEMENT) ---
    pipe_x = [-2, 0, 0, 3, 6]
    pipe_y = [-2, -2, 4, 4, 4]
    pipe_z = [0.5, 0.5, 0.5, 0.5, 0.5]
    fig.add_trace(go.Scatter3d(x=pipe_x, y=pipe_y, z=pipe_z, mode='lines', 
                               line=dict(color="#00f2ff", width=8, dash='solid'), name="Flux Principal"))

    # --- EFFET D'INONDATION (LUMINESCENT) ---
    if alea == "Inondation Majeure" and risk_score > 0:
        water_z = -1 + (risk_score * 0.15)
        fig.add_trace(go.Mesh3d(x=[-5, 10, 10, -5], y=[-5, -5, 10, 10], z=[water_z]*4, 
                               color="rgba(0, 150, 255, 0.3)", opacity=0.5, name="Niveau d'eau"))

    fig.update_layout(
        scene=dict(
            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=1.8*np.cos(angle), y=1.8*np.sin(angle), z=1.3)),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5) # On aplatit un peu pour l'effet grand angle
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, b=0, t=0),
        height=750
    )
    return fig
    # Architecture site industriel
    add_cyl(0, 0, 0, 1.5, 1.2, 2, "Bassin Traitement 1")
    add_cyl(4, 0, 0, 1.5, 1.2, 2, "Bassin Traitement 2")
    add_cube(1, 3, 0, 3, 2, 2, 5, "Unité de Pompage")
    add_cube(5, 4, -1, 2, 2, 0.8, 8, "Local Électrique")
    
    # Réseau tuyauterie
    fig.add_trace(go.Scatter3d(x=[0, 0, 2.5, 5], y=[0, 3, 3, 4], z=[0.6, 0.6, 0.6, 0.6], mode='lines', line=dict(color="#00f2ff", width=5), showlegend=False))

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
        camera=dict(eye=dict(x=1.7*np.cos(angle), y=1.7*np.sin(angle), z=1.2))),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=650)
    return fig

# --- 5. LOGIQUE D'AFFICHAGE ---
if tab == "🖥️ Simulation 3D":
    col_v, col_k = st.columns([2.5, 1])
    
    with col_v:
        st.header(f"Digital Twin : Impact {alea}")
        if mode_cine:
            ph = st.empty()
            for i in range(120):
                ph.plotly_chart(create_complex_view(risk_val, angle=i*0.05), use_container_width=True, key=f"v_{i}")
                time.sleep(0.04)
        else:
            st.plotly_chart(create_complex_view(risk_val), use_container_width=True)
        st.info(f"**Stratégie {cat_strat} ({horiz_strat}) :** {strategies[cat_strat][horiz_strat]}")
        
# --- AJOUT DE LA LÉGENDE DANS L'INTERFACE ---
st.markdown("### 🗺️ Légende des Infrastructures")
leg_col1, leg_col2, leg_col3 = st.columns(3)

with leg_col1:
    st.markdown("""
    **💠 Prétraitement & Primaire**
    * **Dégrillage (Bloc) :** Filtrage des gros déchets.
    * **Décanteur (Cylindre Bas) :** Sédimentation physique.
    """)

with leg_col2:
    st.markdown("""
    **🧪 Traitement Biologique**
    * **Bassin d'Aération (Bloc Long) :** Épuration par bactéries.
    * **Clarificateur (Cylindre Large) :** Séparation eau/boues.
    """)

with leg_col3:
    st.markdown("""
    **⚡ Énergie & Résidus**
    * **Digesteur (Tour) :** Production de biogaz.
    * **HUB SCADA (Bloc Enterré) :** Pilotage électrique (Critique).
    """)
    with col_k:
        st.subheader("📊 Diagnostic")
        paralysie = (risk_val * 20) if alea != "Hors Crise" else 0
        coût = risk_val * 3.5
        
        style = "status-ok" if paralysie == 0 else ("status-warn" if paralysie < 60 else "status-critical")
        statut = "OPTIMAL" if paralysie == 0 else ("DÉGRADÉ" if paralysie < 60 else "CRITIQUE")

        st.markdown(f"""
        <div class="info-card">
            <p style="opacity:0.7">ÉTAT DU SYSTÈME</p>
            <h2 class="{style}">{statut}</h2>
        </div>
        <div class="info-card">
            <p style="opacity:0.7">PARALYSIE ESTIMÉE</p>
            <span class="metric-value">{paralysie} Jours</span>
        </div>
        <div class="info-card">
            <p style="opacity:0.7">PERTES FINANCIÈRES</p>
            <span class="metric-value" style="color:#ff3232;">-{coût:.1f} M€</span>
        </div>
        """, unsafe_allow_html=True)

else:
    st.header("ℹ️ Méthodologie et Calculs")
    st.markdown("La résilience est calculée selon l'équation de risque de l'UNDRR :")
    st.latex(r"Risque = \frac{Aléa \times Vulnérabilité}{Capacité\ d'Adaptation}")
    
    st.subheader("Modèle de Coûts et Délais")
    st.markdown("""
    - **Dommages :** Basés sur les courbes de fragilité JRC.
    - **Paralysie :** Temps cumulé de décontamination, séchage et mise en conformité électrique.
    """)
    
    st.table({
        "Niveau d'Aléa": ["Faible", "Modéré", "Sévère", "Extrême"],
        "Paralysie (j)": ["5-15", "15-45", "45-90", "90-180"],
        "Coût Moyen (M€)": ["0.5", "4.2", "12.5", "28.0"]
    })
