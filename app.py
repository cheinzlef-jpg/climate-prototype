import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(page_title="The Climate Standards 3D - Mont Blanc", layout="wide")

st.title("🛰️ Terminal 3D de Résilience : Tunnel du Mont-Blanc")
st.markdown("---")

# --- INTERFACE DE CONTRÔLE ---
st.sidebar.header("🕹️ Simulation Multi-Aléas")
alea = st.sidebar.radio("Sélectionner l'aléa", ["Inondation", "Sécheresse", "Glissement de terrain"])
intensite = st.sidebar.slider("Intensité de l'aléa (Niveau 1-5)", 1, 5, 2)

# --- DONNÉES TECHNIQUES DES SECTIONS ---
data = {
    'Section': ['Portail France', 'Galerie Tech 1', 'Cœur du Massif', 'Galerie Tech 2', 'Portail Italie'],
    'lat': [45.902, 45.885, 45.860, 45.845, 45.832],
    'lon': [6.861, 6.900, 6.940, 6.980, 7.015],
    'altitude': [1274, 1350, 1395, 1360, 1381], # Altitude réelle du tunnel
    'vuln_inondation': [5, 2, 1, 2, 5],
    'vuln_secheresse': [1, 2, 4, 2, 1], # Impact sur permafrost/fissures
    'vuln_glissement': [4, 5, 2, 4, 3]
}
df = pd.DataFrame(data)

# --- LOGIQUE DE RISQUE ---
def calculate_risk(row, alea, intensite):
    if alea == "Inondation": v = row['vuln_inondation']
    elif alea == "Sécheresse": v = row['vuln_secheresse']
    else: v = row['vuln_glissement']
    
    risk_score = v * intensite
    if risk_score > 15: return [255, 0, 0, 200]    # Rouge (Critique)
    if risk_score > 8: return [255, 165, 0, 200]  # Orange (Alerte)
    return [0, 255, 100, 200]                    # Vert (Résilient)

df['color'] = df.apply(lambda r: calculate_risk(r, alea, intensite), axis=1)

# --- VISUALISATION 3D (PYDECK) ---
# Simulation du relief (MNT) via l'inclinaison de la caméra
view_state = pdk.ViewState(
    latitude=45.86, longitude=6.94, zoom=11, pitch=45, bearing=30
)

layer_tunnel = pdk.Layer(
    "ColumnLayer",
    df,
    get_position="[lon, lat]",
    get_elevation="altitude",
    elevation_scale=1,
    radius=150,
    get_fill_color="color",
    pickable=True,
    auto_highlight=True,
)
r = pdk.Deck(
    layers=[layer_tunnel],
    initial_view_state=view_state,
    # On utilise un style vide et on ajoute le fond satellite en fond
    map_provider="carto", 
    map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json", 
    tooltip={"text": "{Section}"}
)

col1, col2 = st.columns([3, 1])

with col1:
    st.pydeck_chart(r)

with col2:
    st.subheader("📋 Analyse d'Impact")
    st.write(f"**Aléa :** {alea}")
    st.write(f"**Intensité :** {intensite}/5")
    
    # Stratégies d'adaptation dynamiques
    st.markdown("### 🛠️ Stratégies")
    if alea == "Inondation":
        st.info("- Batardeaux automatiques\n- Pompes d'exhaure haute capacité")
    elif alea == "Sécheresse":
        st.info("- Monitoring permafrost\n- Injection de coulis dans les fissures")
    else:
        st.info("- Pose de filets haute résistance\n- Capteurs de mouvement (Inclinomètres)")

# --- FOOTER TECHNIQUE ---
st.caption("Données simulées sur MNT IGN 25m - Analyse de Niveau 3 (The Climate Standards)")
