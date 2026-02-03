import streamlit as st

# 1. Configuration (Plein écran)
st.set_page_config(layout="wide", page_title="Simulateur Infra")

# 2. Choix de l'infrastructure
# Tu peux ajouter tes propres URLs d'images ici
infra_images = {
    "Tunnel": "https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop",
    "Pont": "https://images.unsplash.com/photo-1445023083233-0669f6888636?q=80&w=2070&auto=format&fit=crop",
    "Station de Pompage": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?q=80&w=2070&auto=format&fit=crop"
}

with st.sidebar:
    st.header("⚙️ PARAMÈTRES")
    site = st.selectbox("CHOISIR SITE", list(infra_images.keys()))
    horizon = st.slider("HORIZON", 2024, 2100, 2050)
    intensite = st.slider("SÉVÉRITÉ ALÉA (%)", 0, 100, 40) / 100

# 3. CSS pour l'affichage HUD (On code le design ici)
st.markdown(f"""
<style>
    .stApp {{
        background-image: url("{infra_images[site]}");
        background-size: cover;
        background-position: center;
    }}
    .hud-card {{
        background: rgba(0, 20, 30, 0.85);
        border: 2px solid #00f2ff;
        border-radius: 10px;
        padding: 20px;
        color: #00f2ff;
        font-family: 'monospace';
        box-shadow: 0 0 15px #00f2ff;
    }}
    .danger {{ color: #ff4b4b; font-weight: bold; font-size: 1.5em; }}
</style>
""", unsafe_allow_html=True)

# 4. Le contenu (Code des calculs et affichage)
st.title(f"🔍 MONITORING : {site.upper()}")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    impact = round(intensite * 250 * ((horizon-2024)/76 + 1), 1)
    st.markdown(f"""
    <div class="hud-card">
        <h3>📊 IMPACT ÉCO</h3>
        <p class="danger">-{impact} M€</p>
        <p>Probabilité arrêt : {int(intensite * 90)}%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # On simule des métriques selon le site
    m1 = "Débit" if site == "Station de Pompage" else "Trafic"
    val = int(100 - (intensite * 80))
    st.markdown(f"""
    <div class="hud-card">
        <h3>🚀 OPÉRATIONS</h3>
        <p>Efficacité {m1} : {val}%</p>
        <p>Alerte structure : {'OUI' if intensite > 0.7 else 'NON'}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="hud-card">
        <h3>🛡️ STRATÉGIE</h3>
        <p><b>{horizon}</b> : {
            "Renforcement béton" if site == "Pont" else 
            "Digue anti-crue" if site == "Station de Pompage" else 
            "Ventilation forcée"
        }</p>
    </div>
    """, unsafe_allow_html=True)
