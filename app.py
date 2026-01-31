import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(page_title="The Climate Standards - Prototype V1", layout="wide")

st.title("🛡️ The Climate Standards | Terminal de Résilience")
st.subheader("Analyse de Niveau 3 : Stress-Test Climatique & SCADA")

# --- SIDEBAR : PARAMÈTRES DU SCÉNARIO ---
st.sidebar.header("Paramètres du Scénario")
annee = st.sidebar.selectbox("Horizon Temporel", [2026, 2050, 2100])
temp_max = st.sidebar.slider("Température Extrême (°C)", 30, 55, 40)
secteur = st.sidebar.selectbox("Secteur", ["Eau", "Énergie", "Logistique"])

# --- DONNÉES FICTIVES (Mélange SIG + SCADA) ---
data = {
    'Asset': ['Station Pompage A', 'Poste Électrique Nord', 'Unité de Traitement'],
    'Lat': [48.8566, 48.8600, 48.8500],
    'Lon': [2.3522, 2.3600, 2.3400],
    'Seuil_SCADA_Temp': [42, 48, 45], # Limite physique de l'automate
    'Importance': [0.9, 1.0, 0.7]
}
df = pd.DataFrame(data)

# --- LOGIQUE DE CALCUL DU SCORE ---
df['Etat'] = df['Seuil_SCADA_Temp'].apply(lambda x: "OK" if x > temp_max else "CRITIQUE")
score_resilience = 100 - (df[df['Etat'] == "CRITIQUE"]['Importance'].sum() * 50)
score_resilience = max(0, min(100, score_resilience))

# --- AFFICHAGE DU DASHBOARD ---
col1, col2 = st.columns([2, 1])

with col1:
    st.write(f"### Carte de Vulnérabilité - Horizon {annee}")
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=14)
    
    for _, row in df.iterrows():
        color = "green" if row['Etat'] == "OK" else "red"
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=10,
            color=color,
            fill=True,
            popup=f"{row['Asset']} (Seuil: {row['Seuil_SCADA_Temp']}°C)"
        ).add_to(m)
    
    st_folium(m, width=700, height=400)

with col2:
    st.metric(label="Score de Résilience Global", value=f"{int(score_resilience)} / 100")
    st.write("### État des Actifs (SCADA)")
    st.table(df[['Asset', 'Seuil_SCADA_Temp', 'Etat']])

# --- EXPLICATION TECHNIQUE POUR LE CLIENT ---
st.info(f"""
**Analyse de Niveau 3 :** À {temp_max}°C, le système détecte que 
{len(df[df['Etat'] == 'CRITIQUE'])} actif(s) dépasse(nt) les seuils de sécurité SCADA. 
Le risque de rupture systémique est de {100 - score_resilience}%.
""")
