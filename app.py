import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Dashboard Adaptation Mont-Blanc")

# --- DATA SIMULATION (Logique RCP) ---
def get_hazard_levels(rcp, horizon):
    # Facteur multiplicateur selon le RCP et l'année
    factor = {"2.6": 1.1, "4.5": 1.5, "8.5": 2.2}
    time_mult = (horizon - 2024) / 76
    base_impact = factor[rcp] * time_mult
    
    return {
        "Glissement de terrain": 20 * base_impact,
        "Inondation/Crues": 15 * base_impact,
        "Stress Thermique": 30 * base_impact
    }

# --- SIDEBAR ---
st.sidebar.header("🕹️ Contrôle du Scénario")
selected_rcp = st.sidebar.select_slider("Trajectoire RCP", options=["2.6", "4.5", "8.5"])
selected_year = st.sidebar.select_slider("Horizon Temporel", options=[2024, 2050, 2100])

hazards = get_hazard_levels(selected_rcp, selected_year)

# --- VISUALISATION "RAYON X" DYNAMIQUE ---
st.subheader(f"🔍 Analyse 'Rayon X' du Tunnel - Horizon {selected_year} (RCP {selected_rcp})")

# Création du tunnel par tronçons
segments = ["Portail FR", "Tronçon Central 1", "Tronçon Central 2", "Portail IT"]
hazard_values = [hazards["Glissement de terrain"], hazards["Stress Thermique"], 
                 hazards["Stress Thermique"]*1.2, hazards["Inondation/Crues"]]

fig = go.Figure(data=[go.Bar(
    x=segments, y=hazard_values,
    marker_color=['#FFA500', '#FF4B4B', '#FF4B4B', '#00F2FF'],
    text=[f"{v:.1f}% Risque" for v in hazard_values],
    textposition='auto',
)])

fig.update_layout(title="Indice de vulnérabilité par tronçon", template="plotly_dark", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- ANALYSE DES CONSÉQUENCES (Multi-Critères) ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Analyse des Impacts")
    impact_data = {
        "Domaine": ["Économique", "Social", "Environnemental", "Technique"],
        "Conséquence": [
            "Perte de péage + surcoût maintenance",
            "Rupture chaîne logistique (Fréjus saturé)",
            "Pollution liée aux détours kilométriques",
            "Obsolescence du système de refroidissement"
        ],
        "Score de Gravité (/10)": [min(10, hazards["Stress Thermique"]/3), 5, 4, 7]
    }
    st.table(pd.DataFrame(impact_data))

with col2:
    st.markdown("### 🛡️ Stratégies d'Adaptation (Coût-Avantage)")
    # Logique de décision simplifiée
    if hazards["Stress Thermique"] > 15:
        st.warning("👉 **Action Recommandée :** Modernisation de la ventilation cryogénique.")
        st.caption("Ratio C/A : 1.8 (Investissement lourd mais évite 6 mois de fermeture cumulée)")
    if hazards["Glissement de terrain"] > 10:
        st.info("👉 **Action Recommandée :** Filets dynamiques et monitoring fibre optique.")
        st.caption("Ratio C/A : 4.2 (Coût faible, haute protection des entrées)")
