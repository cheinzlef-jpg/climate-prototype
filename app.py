import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="The Climate Standards - Mont Blanc", layout="wide")

st.title("🛡️ Resilience Terminal: Tunnel du Mont-Blanc")
st.markdown("---")

# --- SIDEBAR : CONTRÔLE DU RISQUE ---
st.sidebar.header("🕹️ Simulation de Crue")
flood_level = st.sidebar.slider("Niveau de crue torrentielle (m)", 0.0, 4.0, 0.5)
scenario_year = st.sidebar.selectbox("Horizon", ["Actuel", "2050 (RCP 8.5)", "2100"])

# --- DONNÉES DES SECTIONS DU TUNNEL ---
# Simulation de 5 sections critiques
sections = {
    'Section': ['Portail France', 'Section Géotechnique 1', 'Zone Centrale', 'Section Géotechnique 2', 'Portail Italie'],
    'Lat': [45.902, 45.885, 45.860, 45.845, 45.832],
    'Lon': [6.861, 6.900, 6.940, 6.980, 7.015],
    'Seuil_Inondation_m': [1.5, 3.5, 4.0, 3.2, 1.2], # Niveau d'eau avant arrêt SCADA
    'Importance': [1.0, 0.8, 0.9, 0.8, 1.0]
}
df = pd.DataFrame(sections)

# Logique de statut
df['Statut'] = df['Seuil_Inondation_m'].apply(lambda x: "✅ OPÉRATIONNEL" if x > flood_level else "🚨 RUPTURE SCADA")

# --- INTERFACE PRINCIPALE ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📍 Carte de Vulnérabilité - {scenario_year}")
    # Vue centrée sur le tunnel
    m = folium.Map(location=[45.86, 6.94], zoom_start=12, tiles='CartoDB dark_matter')
    
    # Dessiner le tracé du tunnel (Ligne bleue)
    folium.PolyLine(df[['Lat', 'Lon']].values, color="white", weight=5, opacity=0.5).add_to(m)

    for _, row in df.iterrows():
        color = "green" if "✅" in row['Statut'] else "red"
        folium.Marker(
            location=[row['Lat'], row['Lon']],
            icon=folium.Icon(color=color, icon='info-sign'),
            popup=f"{row['Section']} - Seuil: {row['Seuil_Inondation_m']}m"
        ).add_to(m)
    
    st_folium(m, width=800, height=500)

with col2:
    st.subheader("📊 État par Section")
    st.dataframe(df[['Section', 'Statut']], hide_index=True)
    
    # Calcul score global
    score = 100 - (len(df[df['Statut'] == "🚨 RUPTURE SCADA"]) / len(df) * 100)
    st.metric("Indice de Résilience Global", f"{int(score)}%")

st.markdown("---")

# --- SECTION STRATÉGIES D'ADAPTATION ---
st.header("🛠️ Stratégies d'Adaptation (Préconisations)")

if score < 100:
    st.warning("Des vulnérabilités critiques ont été détectées. Voici les mesures correctives :")
    
    tab1, tab2, tab3 = st.tabs(["🏗️ Infrastructure", "🔌 SCADA / Élec", "🌊 Gestion des Eaux"])
    
    with tab1:
        st.write("**Élévation des Portails :** Installer des barrières anti-crue amovibles aux entrées France et Italie (Seuils détectés < 2m).")
        st.write("**Renforcement Géotechnique :** Injection de résine dans les zones de failles pour prévenir les infiltrations liées à la fonte du permafrost.")
        
    with tab2:
        st.write("**Mise hors d'eau :** Surélever les armoires électriques et capteurs SCADA de 1.5m par rapport au niveau du sol actuel.")
        st.write("**Redondance :** Déploiement de capteurs de pression IP68 (étanches) pour maintenir le monitoring en cas d'immersion partielle.")
        
    with tab3:
        st.write("**Bassins de rétention :** Augmenter la capacité des pompes d'exhaure (évacuation des eaux) de 30% pour absorber les crues éclairs.")
else:
    st.success("L'infrastructure est résiliente pour ce niveau de crue. Monitoring standard activé.")
