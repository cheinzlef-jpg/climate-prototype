import matplotlib.pyplot as plt
import numpy as np

# Critères issus de votre barème
labels = ['Diagnostic', 'Gestion Flux', 'Communication', 'Interdisciplinarité', 'Réactivité']
# Exemple de score pour l'équipe gagnante (Pégomas)
scores = [17, 18, 16, 17, 19] 

angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
scores += scores[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, scores, color='teal', alpha=0.25)
ax.plot(angles, scores, color='teal', linewidth=2)
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
plt.title("Référentiel d'Évaluation : Profil de Performance (Exemple Pégomas)", y=1.1)
plt.show()
