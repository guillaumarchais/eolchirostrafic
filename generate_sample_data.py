"""
Générateur de données de test pour l'application Séparateur d'individus.
Crée un fichier CSV réaliste simulant 220 nuits de suivi acoustique.

Usage : python generate_sample_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

SPECIES = [
    "Pipistrellus nathusii",
    "Nyctalus noctula",
    "Pipistrellus pipistrellus",
    "Pipistrellus pygmaeus",
    "Vespertilio murinus",
]

# Phénologie (probabilité de présence par jour julien)
def presence_probability(doy, species):
    """Simule une phénologie bimodale printemps/automne."""
    if species == "Pipistrellus nathusii":
        spring = 0.9 * np.exp(-0.5 * ((doy - 110) / 15) ** 2)
        autumn = 1.0 * np.exp(-0.5 * ((doy - 245) / 20) ** 2)
    elif species == "Nyctalus noctula":
        spring = 0.5 * np.exp(-0.5 * ((doy - 100) / 20) ** 2)
        autumn = 0.8 * np.exp(-0.5 * ((doy - 240) / 25) ** 2)
    elif species == "Pipistrellus pipistrellus":
        spring = 0.4 * np.exp(-0.5 * ((doy - 120) / 20) ** 2)
        autumn = 0.7 * np.exp(-0.5 * ((doy - 250) / 20) ** 2)
    elif species == "Pipistrellus pygmaeus":
        spring = 0.3 * np.exp(-0.5 * ((doy - 115) / 18) ** 2)
        autumn = 0.5 * np.exp(-0.5 * ((doy - 255) / 18) ** 2)
    else:  # Vespertilio murinus
        spring = 0.2 * np.exp(-0.5 * ((doy - 105) / 15) ** 2)
        autumn = 0.4 * np.exp(-0.5 * ((doy - 248) / 15) ** 2)
    return spring + autumn


def generate_night(date, species, n_individuals, sunset_h=21, sunrise_h=6):
    """Génère des contacts pour une nuit donnée."""
    contacts = []
    night_start = datetime(date.year, date.month, date.day, sunset_h, 0)
    night_end = datetime(date.year, date.month, date.day + 1, sunrise_h, 0)
    total_minutes = int((night_end - night_start).total_seconds() / 60)

    for ind in range(n_individuals):
        # Heure de passage de l'individu (uniforme sur la nuit)
        pass_minute = random.randint(0, total_minutes - 1)
        t_center = night_start + timedelta(minutes=pass_minute)

        # Nombre de contacts pour cet individu (1-8 contacts rapprochés)
        n_contacts = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8],
                                      p=[0.3, 0.25, 0.2, 0.1, 0.07, 0.04, 0.03, 0.01])

        # Contacts en rafale (intervalles courts, 0-3 min)
        for c in range(n_contacts):
            offset = sum(np.random.randint(0, 4) for _ in range(c))
            t = t_center + timedelta(minutes=offset)
            if night_start <= t <= night_end:
                contacts.append({
                    "Date": t.strftime("%d/%m/%Y"),
                    "Heure": t.strftime("%H:%M:%S"),
                    "Espece": species,
                })

    return contacts


# Générer 220 nuits (avril à novembre 2023)
start_date = datetime(2023, 3, 15).date()
all_records = []

for day_offset in range(220):
    date = start_date + timedelta(days=day_offset)
    doy = date.timetuple().tm_yday

    for sp in SPECIES:
        p = presence_probability(doy, sp)
        # Décider si l'espèce est présente cette nuit
        if random.random() < p:
            n_ind = max(1, int(np.random.poisson(p * 4)))
            records = generate_night(date, sp, n_ind)
            all_records.extend(records)

df = pd.DataFrame(all_records)
df = df.sort_values(["Date", "Heure"]).reset_index(drop=True)

# Mélanger légèrement l'ordre pour simuler un vrai export logiciel
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

df.to_csv("sample_data.csv", index=False, sep=";")

print(f"✅ Fichier 'sample_data.csv' généré :")
print(f"   {len(df):,} contacts")
print(f"   {df['Espece'].nunique()} espèces")
print(f"   Période : {df['Date'].min()} → {df['Date'].max()}")
print(f"\nDistribution par espèce :")
print(df['Espece'].value_counts().to_string())
