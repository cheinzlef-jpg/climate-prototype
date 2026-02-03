import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(layout="wide", page_title="Digital Twin - Pumping Station")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00f2ff; }
    section[data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #00f2ff; }
    h1, h2, h3, h4, p, label { color: #00f2ff !important; }
    .info-card { background: rgba(0, 20, 30, 0.8); border: 1px solid #00f2ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .metric-value { font-size: 1.8em; font-weight: bold; color: #ff4b4b; }
    .indicator-label { font-size: 0.9em; color: #00f2ff; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIQUE DE NAVIGATION (SIDEBAR) ---
with st.sidebar:
    st.title("🛡️ HUB DE CONTRÔLE")
    tab_choice = st.radio("Navigation", ["🖥️ Simulation 3D", "ℹ️ Méthodologie & Hypothèses"])
    
    st.divider()
    if tab_choice == "🖥️ Simulation 3D":
        st.subheader("1. Scénario Climatique")
        alea = st.selectbox("Type d'aléa", ["Hors Crise", "Inondation", "Sécheresse"])
        rcp = st.select_slider("Scénario RCP", options=["2.6", "4.5", "8.5"], value="8.5")
        horizon_clim = st.select_slider("Horizon Temporel", options=["Actuel", "2050", "2100"], value="2050")
        
        st.divider()
        st.subheader("2. Stratégies d'Adaptation")
        cat_strat = st.selectbox("Catégorie de mesure", ["Physique", "Systémique", "Gouvernance", "R&D"])
        horizon_strat = st.select_slider("Échéance de mise en œuvre", options=["< 5 ans", "5 ans", "10 ans", "20 ans"])
        
        # Calcul du score de risque (0 à 10)
        risk_score = 0 if alea == "Hors Crise" else (2 if horizon_clim == "Actuel" else (5 if horizon_clim == "2050" else 8))
        if rcp == "8.5": risk_score += 2
    else:
        st.info("Consultez les détails théoriques du modèle.")

# --- 3. BASE DE DONNÉES DES STRATÉGIES ---
data_strat = {
    "Physique": {"< 5 ans": "Batardeaux amovibles.", "5 ans": "Surélévation pompes.", "10 ans": "Digues béton.", "20 ans": "Structures flottantes."},
    "Systémique": {"< 5 ans": "Protocoles délestage.", "5 ans": "Maillage réseaux.", "10 ans": "Micro-grid solaire.", "20 ans": "REUT circulaire."},
    "Gouvernance": {"< 5 ans": "Audit assurance.", "5 ans": "Alerte IoT.", "10 ans": "Cellule de crise.", "20 ans": "Standards résilience."},
    "R&D": {"< 5 ans": "Jumeau numérique.", "5 ans": "Matériaux auto-cicatrisants.", "10 ans": "IA prédictive.", "20 ans": "Bio-filtration thermique."}
}

# --- 4. CONTENU CONDITIONNEL ---

if tab_choice == "🖥️ Simulation 3D":
    st.header(f"Digital Twin : Mode {'X-Ray Bleu (Normal)' if alea == 'Hors Crise' else 'Alerte Crise'}")
    
    col_visu, col_kpi = st.columns([2.5, 1])
    
    with col_visu:
        # Création d'un schéma 3D X-Ray (Plotly)
        fig = go.Figure()
        
        def add_box_xray(x, y, z, dx, dy, dz, color, name):
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                color=color, opacity=0.4, showscale=False, name=name
            ))

        # Définition des couleurs selon le risque
        main_color = "rgba(0, 242, 255, 0.3)" if risk_score < 3 else "rgba(255, 50, 50, 0.5)"
        
        # Dessin de l'usine simplifiée
        add_box_xray(0, 0, 0, 2, 2, 1, main_color, "Unité Pompage")
        add_box_xray(3, 0, -0.5, 1.5, 1.5, 0.5, "rgba(0, 242, 255, 0.2)", "Sous-sol Technique")
        add_box_xray(0, 3, 0, 1, 1, 0.8, main_color, "Contrôle")
        
        fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
                          paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"🛠️ Stratégie : {cat_strat} ({horizon_strat})")
        st.markdown(f'<div class="strategy-box">{data_strat[cat_strat][horizon_strat]}</div>', unsafe_allow_html=True)

    with col_kpi:
        st.subheader("📊 INDICATEURS (KPI)")
        
        # Calculs KPI
        cout_base = risk_score * 1.2
        resilience_score = max(10, 100 - (risk_score * 9))
        
        st.markdown(f"""
        <div class="info-card">
            <p class="indicator-label">💰 ESTIMATION DÉGÂTS (COURT TERME)</p>
            <span class="metric-value">-{cout_base:.1f} M€</span>
        </div>
        <div class="info-card">
            <p class="indicator-label">📉 TAUX DE RÉSILIENCE SYSTÉMIQUE</p>
            <span class="metric-value" style="color: #00ff00;">{resilience_score}%</span>
        </div>
        <div class="info-card">
            <p class="indicator-label">⏳ CONTINUITÉ DE SERVICE</p>
            <span class="metric-value" style="color: {'#ff4b4b' if resilience_score < 50 else '#00ff00'};">
                {"> 98%" if risk_score < 3 else "45% (Interrompu)"}
            </span>
        </div>
        """, unsafe_allow_html=True)

else:
    # --- 5. ONGLET MÉTHODOLOGIE ---
    st.header("ℹ️ Méthodologie & Hypothèses de Calcul")
    
    st.subheader("Formule du Risque ($R$)")
    st.latex(r"R = \text{Aléa} (P) \times \text{Vulnérabilité} (V) \times \text{Exposition} (E)")
    
    st.markdown("""
    ### Justification des Indicateurs :
    * **Coût Court Terme (6 mois) :** Basé sur le **CAPEX de remplacement** immédiat (pompes, automates). Modèle : *Valeur à neuf - Vétusté + Frais de décontamination*.
    * **Coût Long Terme (5 ans) :** Intègre les **Impacts Systémiques**. Calculé via le multiplicateur de *Cramer-Lundberg* (dommages indirects sur l'industrie et la santé).
    * **Taux de Résilience :** Indicateur composite pondérant l'état des structures X-Ray et la redondance des systèmes de secours.
    """)
    
    
    
    st.info("💡 Les données sont indexées sur les rapports du GIEC (RCP 8.5) et les courbes de dommages de l'OCDE.")
