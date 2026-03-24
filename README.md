# 🦇 Eol chiros trafic : convertisseur d'activité en estimations d'individus

Application Streamlit pour estimer le nombre d'individus à partir de données
acoustiques de suivi de chauves-souris, basée sur la méthode du séparateur
(Seebens-Hoyer et al., 2026) avec test de bimodalité de Hartigan's Dip.

---

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

---

## Format du fichier d'entrée

Le fichier CSV ou Excel doit contenir **au minimum** :
- une colonne date-heure (fusionnée ou en deux colonnes séparées)
- une colonne espèce / label

### Exemples de formats acceptés

**Option A — colonne unique date-heure :**

| DateTime            | Espece                  |
|---------------------|-------------------------|
| 15/08/2023 22:14:05 | Pipistrellus nathusii   |
| 15/08/2023 22:31:18 | Nyctalus noctula        |
| 16/08/2023 00:05:42 | Pipistrellus nathusii   |

**Option B — colonnes séparées :**

| Date       | Heure    | Espece                  |
|------------|----------|-------------------------|
| 15/08/2023 | 22:14:05 | Pipistrellus nathusii   |
| 15/08/2023 | 22:31:18 | Nyctalus noctula        |

**Formats de date acceptés :** `DD/MM/YYYY`, `YYYY-MM-DD`, `DD-MM-YYYY`, etc.
**Séparateurs CSV acceptés :** `,` ou `;` (détection automatique)

---

## Fonctionnalités

### Onglets

| Onglet | Contenu |
|--------|---------|
| 📋 Données | Aperçu du fichier importé, distribution des contacts par nuit |
| 📊 Distribution des intervalles | Histogramme des intervalles, test de Hartigan's Dip par espèce |
| 🦇 Estimation par nuit | Individus estimés par nuit × espèce, ratios, tableau de synthèse |
| 🗓️ Vue phénologique | Détail contact par contact d'une nuit, phénologie saisonnière |
| 💾 Export | Téléchargement Excel de toutes les tables (individus, intervalles, Hartigan) |

### Paramètres (sidebar)

- **Séparateur** : intervalle sans activité en minutes (5–60 min, défaut 20 min)
- **Mapping des colonnes** : flexible, colonne unique ou date + heure séparées
- **Filtre période** : analyse d'une période migratoire spécifique
- **Contacts minimum** : exclure les nuits avec trop peu de contacts

---

## Méthode

### Séparateur d'individus

Deux contacts de la même espèce séparés de plus de N minutes sans activité
sont attribués à deux individus distincts. La valeur de 20 min est recommandée
comme estimation conservative (Seebens-Hoyer et al., 2026).

**Règle :**
```
gap > N min  →  nouvel individu
gap ≤ N min  →  même individu
```

### Test de bimodalité (Hartigan's Dip)

Le test de Hartigan's Dip (1985) teste l'hypothèse nulle d'unimodalité.

- **p < 0.05** : bimodalité confirmée → séparateur valide
- **p ≥ 0.05** : distribution unimodale → utiliser l'activité brute

### Nuit acoustique

Une "nuit acoustique" correspond à la soirée d'un jour donné :
- Contacts avant 12h00 → rattachés à la nuit précédente (J-1)
- Contacts après 12h00 → rattachés à la nuit du jour J

---

## Référence

> Seebens-Hoyer, A., Bach, L., Pommeranz, H., Voigt, C.C., et al. (2026).
> Estimating the traffic rates of bats migrating across the North and Baltic Seas
> to develop efficient mitigation measures at offshore wind energy facilities.
> *Biological Conservation*, 316, 111741.
> https://doi.org/10.1016/j.biocon.2026.111741

---

## Déploiement Streamlit Cloud

1. Créer un dépôt GitHub avec `app.py` et `requirements.txt`
2. Se connecter sur [share.streamlit.io](https://share.streamlit.io)
3. Pointer vers le dépôt → déploiement automatique

---

## Dépendances

| Package | Rôle |
|---------|------|
| `streamlit` | Interface web |
| `pandas` | Manipulation des données |
| `numpy` | Calculs numériques |
| `plotly` | Visualisations interactives |
| `openpyxl` | Lecture/écriture Excel |
| `diptest` | Test de Hartigan's Dip (bimodalité) |
