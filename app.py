"""
Séparateur d'individus — Acoustique chiroptères
================================================
Application Streamlit pour estimer le nombre d'individus à partir de
données acoustiques de suivi de chauves-souris (méthode du séparateur,
Seebens-Hoyer et al., 2026) avec test de bimodalité de Hartigan's Dip.

Lancer : streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import timedelta
import io

# ── Dépendance optionnelle : diptest ──────────────────────────────────────────
try:
    import diptest as _diptest
    HAS_DIPTEST = True
except ImportError:
    HAS_DIPTEST = False

# ─────────────────────────────────────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Séparateur d'individus — Chiroptères",
    page_icon="🦇",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 2rem; }
.block-container { padding-top: 1.5rem; }
.stTabs [data-baseweb="tab"] { font-size: 14px; }
div.stAlert > div { font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ─────────────────────────────────────────────────────────────────────────────

def acoustic_night(dt):
    """Date de la nuit acoustique : soir = date du jour si h≥12, sinon date J-1."""
    if pd.isna(dt):
        return None
    if dt.hour < 12:
        return (dt - timedelta(days=1)).date()
    return dt.date()


def compute_gaps(times_sorted):
    """Calcule les intervalles (minutes) entre contacts consécutifs."""
    if len(times_sorted) < 2:
        return np.array([])
    deltas = [(times_sorted[i] - times_sorted[i - 1]).total_seconds() / 60
              for i in range(1, len(times_sorted))]
    return np.array(deltas)


def assign_individuals(times_sorted, separator_min):
    """
    Attribue un numéro d'individu à chaque contact.
    Retourne un array d'entiers de même longueur que times_sorted.
    """
    if len(times_sorted) == 0:
        return np.array([], dtype=int)
    individus = np.ones(len(times_sorted), dtype=int)
    current = 1
    for i in range(1, len(times_sorted)):
        delta = (times_sorted[i] - times_sorted[i - 1]).total_seconds() / 60
        if delta > separator_min:
            current += 1
        individus[i] = current
    return individus


def hartigan_dip(gaps):
    """
    Teste la bimodalité via Hartigan's Dip.
    Retourne (D, p, warning_msg).

    Pré-requis pour un test fiable :
    - Au moins 30 intervalles (effectif minimum)
    - Au moins 5 % d'intervalles > 10 min (mode long présent)
    Sans ces conditions, D≈0 / p≈1 est un artefact numérique, pas un résultat.
    """
    if not HAS_DIPTEST:
        return None, None, "Package diptest non installé (`pip install diptest`)."
    arr = np.asarray(gaps, dtype=float)
    n = len(arr)
    if n < 30:
        return None, None, (
            f"Effectif insuffisant ({n} intervalles disponibles, minimum 30 requis). "
            "Augmentez le nombre de nuits analysées ou vérifiez le filtre espèce/période."
        )
    pct_long = float(np.mean(arr > 10) * 100)
    if pct_long < 5:
        return None, None, (
            f"Mode long absent : seulement {pct_long:.1f} % des intervalles dépassent 10 min. "
            "La distribution est quasi-unimodale (pic unique de courts intervalles intra-individus). "
            "Cela signifie que les nuits analysées contiennent rarement plusieurs individus distincts "
            "séparés de >10 min — le test ne peut pas distinguer les deux modes. "
            "Vérifiez que la période inclut des nuits à forte activité migratoire."
        )
    d, p = _diptest.diptest(arr)
    return float(d), float(p), None


def build_summary(df, separator_min):
    """Calcule le nombre d'individus estimés par nuit × espèce."""
    rows = []
    for (night, sp), grp in df.groupby(["nuit_acoustique", "espece"], sort=True):
        times = sorted(grp["datetime"])
        individus = assign_individuals(times, separator_min)
        n_ind = int(individus.max()) if len(individus) else 0
        rows.append({
            "Nuit acoustique": night,
            "Espèce": sp,
            "Contacts": len(grp),
            "Individus estimés": n_ind,
        })
    return pd.DataFrame(rows)


def build_gap_df(df, separator_min):
    """Calcule tous les intervalles intra-nuit avec métadonnées (espèce, nuit, statut)."""
    rows = []
    for (night, sp), grp in df.groupby(["nuit_acoustique", "espece"], sort=True):
        times = sorted(grp["datetime"])
        for i in range(1, len(times)):
            delta = (times[i] - times[i - 1]).total_seconds() / 60
            rows.append({
                "nuit_acoustique": night,
                "espece": sp,
                "intervalle_min": delta,
                "nouveau_individu": delta > separator_min,
                "t_debut": times[i - 1],
                "t_fin": times[i],
            })
    return pd.DataFrame(rows)


def get_gaps_for_species(gap_df, sp, max_gap_min=480):
    """
    Extrait les intervalles intra-nuit pour une espèce depuis gap_df.
    Utilise gap_df comme unique source de vérité (pas de duplication de logique).
    Filtre les valeurs aberrantes > max_gap_min (artefacts).
    """
    if gap_df.empty or sp not in gap_df["espece"].values:
        return np.array([])
    arr = gap_df[gap_df["espece"] == sp]["intervalle_min"].values.astype(float)
    return arr[arr <= max_gap_min]


def parse_file(uploaded):
    """Charge CSV ou Excel en DataFrame brut."""
    name = uploaded.name.lower()
    if name.endswith(".csv"):
        # Détection du séparateur
        sample = uploaded.read(4096).decode("utf-8", errors="replace")
        uploaded.seek(0)
        sep = ";" if sample.count(";") > sample.count(",") else ","
        df = pd.read_csv(uploaded, sep=sep, dtype=str)
    else:
        df = pd.read_excel(uploaded, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def try_parse_datetime(df, col_dt=None, col_date=None, col_time=None):
    """
    Essaie de construire une colonne datetime à partir d'une ou deux colonnes.
    Retourne (Series datetime, message d'erreur ou None).
    """
    try:
        if col_dt:
            series = pd.to_datetime(df[col_dt], dayfirst=True, infer_datetime_format=True)
        else:
            combined = df[col_date].astype(str) + " " + df[col_time].astype(str)
            series = pd.to_datetime(combined, dayfirst=True, infer_datetime_format=True)
        if series.isna().all():
            return None, "Aucune date valide reconnue."
        return series, None
    except Exception as e:
        return None, str(e)


# Couleurs espèces (cycle)
SPECIES_COLORS = px.colors.qualitative.Safe + px.colors.qualitative.Vivid


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🦇 Paramètres")

    # ── Import fichier ──────────────────────────────────────────────────────
    st.subheader("1 · Import des données")
    uploaded = st.file_uploader(
        "Tableur (CSV ou Excel)",
        type=["csv", "xlsx", "xls"],
        help="Le fichier doit contenir au minimum une colonne date/heure et une colonne espèce.",
    )

    if not uploaded:
        st.info("Importez un fichier pour commencer.")
        st.markdown("""
**Format attendu :**
| Date | Heure | Espèce |
|------|-------|--------|
| 15/08/2023 | 22:14 | Pipistrellus nathusii |
| 15/08/2023 | 22:31 | Nyctalus noctula |
| … | … | … |

Les colonnes Date et Heure peuvent être fusionnées ou séparées.
        """)
        st.stop()

    raw_df = parse_file(uploaded)

    # ── Mapping des colonnes ────────────────────────────────────────────────
    st.subheader("2 · Mapping des colonnes")
    cols = list(raw_df.columns)

    dt_mode = st.radio(
        "Format date/heure",
        ["Colonne unique (date + heure)", "Deux colonnes séparées"],
        horizontal=True,
    )

    if dt_mode == "Colonne unique (date + heure)":
        col_datetime = st.selectbox("Colonne date-heure", cols,
                                    index=next((i for i, c in enumerate(cols)
                                                if any(k in c.lower() for k in
                                                       ["datetime", "date", "time", "heure"])), 0))
        col_date_sep = col_time_sep = None
    else:
        col_date_sep = st.selectbox("Colonne date", cols,
                                    index=next((i for i, c in enumerate(cols)
                                                if "date" in c.lower()), 0))
        col_time_sep = st.selectbox("Colonne heure", cols,
                                    index=next((i for i, c in enumerate(cols)
                                                if any(k in c.lower() for k in
                                                       ["heure", "time"])), min(1, len(cols) - 1)))
        col_datetime = None

    col_species = st.selectbox(
        "Colonne espèce",
        cols,
        index=next((i for i, c in enumerate(cols)
                    if any(k in c.lower() for k in
                           ["espece", "espèce", "species", "sp", "taxon", "label"])), 0),
    )

    # ── Séparateur ──────────────────────────────────────────────────────────
    st.subheader("3 · Séparateur d'individus")
    sep_min = st.slider(
        "Intervalle sans activité (minutes)",
        min_value=5, max_value=60, value=20, step=1,
        help="Deux contacts séparés de plus de N minutes sont attribués à des individus distincts.",
    )

    # ── Filtres optionnels ──────────────────────────────────────────────────
    st.subheader("4 · Filtres (optionnel)")
    apply_period = st.checkbox("Filtrer par période migratoire")
    date_range = None
    if apply_period:
        date_range = st.date_input(
            "Période à analyser",
            value=[], help="Laisser vide = toutes les dates."
        )

    min_contacts = st.number_input(
        "Contacts minimum par nuit × espèce", min_value=1, value=1, step=1,
        help="Exclure les nuits avec trop peu de contacts pour une espèce donnée.",
    )

    if not HAS_DIPTEST:
        st.warning("⚠️ Package `diptest` non installé — test de Hartigan désactivé.\n\n`pip install diptest`")


# ─────────────────────────────────────────────────────────────────────────────
# Préparation des données
# ─────────────────────────────────────────────────────────────────────────────
if col_datetime:
    dt_series, err = try_parse_datetime(raw_df, col_dt=col_datetime)
else:
    dt_series, err = try_parse_datetime(raw_df, col_date=col_date_sep, col_time=col_time_sep)

if err or dt_series is None:
    st.error(f"Impossible de lire les dates/heures : {err}")
    st.stop()

df_work = pd.DataFrame({
    "datetime": dt_series,
    "espece": raw_df[col_species].astype(str).str.strip(),
})
df_work.dropna(subset=["datetime", "espece"], inplace=True)
df_work = df_work[df_work["espece"] != ""]
df_work["nuit_acoustique"] = df_work["datetime"].apply(acoustic_night)

# Filtre période
if apply_period and date_range and len(date_range) == 2:
    d0, d1 = date_range
    df_work = df_work[
        (df_work["nuit_acoustique"] >= d0) &
        (df_work["nuit_acoustique"] <= d1)
    ]

# Filtre contacts minimum
if min_contacts > 1:
    counts = df_work.groupby(["nuit_acoustique", "espece"]).size().reset_index(name="n")
    valid = counts[counts["n"] >= min_contacts][["nuit_acoustique", "espece"]]
    df_work = df_work.merge(valid, on=["nuit_acoustique", "espece"])

if df_work.empty:
    st.warning("Aucune donnée après filtrage. Vérifiez les paramètres.")
    st.stop()

# Espèces disponibles (pour filtres interactifs)
all_species = sorted(df_work["espece"].unique())
species_color = {sp: SPECIES_COLORS[i % len(SPECIES_COLORS)]
                 for i, sp in enumerate(all_species)}

# ─────────────────────────────────────────────────────────────────────────────
# Calculs principaux
# ─────────────────────────────────────────────────────────────────────────────
summary_df = build_summary(df_work, sep_min)
gap_df = build_gap_df(df_work, sep_min)
# gaps calculés via get_gaps_for_species(gap_df, sp) — source unique : gap_df

n_nights = df_work["nuit_acoustique"].nunique()
total_contacts = len(df_work)
total_individus = summary_df["Individus estimés"].sum()
n_species = len(all_species)

# ─────────────────────────────────────────────────────────────────────────────
# En-tête
# ─────────────────────────────────────────────────────────────────────────────
st.title("🦇 Séparateur d'individus — Acoustique chiroptères")
st.caption(
    f"Fichier : **{uploaded.name}** · "
    f"Séparateur : **{sep_min} min** · "
    f"Méthode : Seebens-Hoyer et al. (2026)"
)

# Métriques résumé
c1, c2, c3, c4 = st.columns(4)
c1.metric("Nuits analysées", f"{n_nights:,}")
c2.metric("Contacts totaux", f"{total_contacts:,}")
c3.metric("Individus estimés", f"{total_individus:,}")
c4.metric("Espèces", f"{n_species}")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Onglets
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Données",
    "📊 Distribution des intervalles",
    "🦇 Estimation par nuit",
    "🗓️ Vue phénologique",
    "💾 Export",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Aperçu des données
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Aperçu des données importées")
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.dataframe(
            df_work.rename(columns={
                "datetime": "Date-heure",
                "espece": "Espèce",
                "nuit_acoustique": "Nuit acoustique",
            }).sort_values("Date-heure").head(500),
            use_container_width=True,
            height=380,
        )
        if len(df_work) > 500:
            st.caption(f"Affichage limité aux 500 premières lignes sur {len(df_work):,}.")

    with col_r:
        st.markdown("**Contacts par espèce**")
        sp_counts = (
            df_work.groupby("espece")
            .agg(contacts=("datetime", "count"),
                 nuits=("nuit_acoustique", "nunique"))
            .reset_index()
            .rename(columns={"espece": "Espèce", "contacts": "Contacts", "nuits": "Nuits"})
            .sort_values("Contacts", ascending=False)
        )
        st.dataframe(sp_counts, use_container_width=True, hide_index=True)

        st.markdown("**Plage temporelle**")
        d0 = df_work["nuit_acoustique"].min()
        d1 = df_work["nuit_acoustique"].max()
        st.info(f"{d0} → {d1}\n\n{n_nights} nuits acoustiques")

    # Distribution des contacts par nuit
    st.markdown("---")
    st.subheader("Contacts par nuit et par espèce")
    nightly = (
        df_work.groupby(["nuit_acoustique", "espece"])
        .size()
        .reset_index(name="contacts")
    )
    nightly["nuit_acoustique"] = nightly["nuit_acoustique"].astype(str)

    sp_filter1 = st.multiselect(
        "Espèces à afficher", all_species, default=all_species[:min(5, len(all_species))],
        key="sp_filter1"
    )
    nightly_f = nightly[nightly["espece"].isin(sp_filter1)] if sp_filter1 else nightly

    fig_nightly = px.bar(
        nightly_f, x="nuit_acoustique", y="contacts", color="espece",
        color_discrete_map=species_color,
        labels={"nuit_acoustique": "Nuit acoustique", "contacts": "Contacts", "espece": "Espèce"},
        height=320,
    )
    fig_nightly.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=10, b=40),
        xaxis=dict(tickangle=-45),
    )
    st.plotly_chart(fig_nightly, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Distribution des intervalles + test de Hartigan
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Distribution des intervalles entre contacts consécutifs")

    col_sp, col_range = st.columns([2, 2])
    with col_sp:
        sp_selected = st.selectbox("Espèce", all_species, key="sp_dip")
    with col_range:
        max_gap_display = st.slider(
            "Intervalle max affiché (min)", 10, 120, 60, 5,
            help="Pour zoomer sur la zone du séparateur."
        )

    # Intervalles intra-nuit poolés pour cette espèce (source pour Hartigan)
    gaps_sp_hartigan = get_gaps_for_species(gap_df, sp_selected)
    # Intervalles avec métadonnées (pour l'histogramme et le tableau)
    if gap_df.empty or sp_selected not in gap_df["espece"].values:
        gaps_sp = np.array([])
    else:
        gaps_sp = gap_df[gap_df["espece"] == sp_selected]["intervalle_min"].values

    gaps_filtered = gaps_sp[gaps_sp <= max_gap_display] if len(gaps_sp) else np.array([])

    # ── Diagnostics de la distribution ──
    n_total = len(gaps_sp_hartigan)
    n_short = int(np.sum(gaps_sp_hartigan <= sep_min)) if n_total else 0
    n_long  = int(np.sum(gaps_sp_hartigan >  sep_min)) if n_total else 0
    pct_long = (n_long / n_total * 100) if n_total else 0

    col_dip1, col_dip2, col_dip3, col_dip4 = st.columns(4)
    col_dip1.metric("Intervalles analysés", f"{n_total:,}")
    col_dip2.metric(f"Courts (≤ {sep_min} min)", f"{n_short:,}",
                    help="Intervalles intra-individu (même individu probable)")
    col_dip3.metric(f"Longs (> {sep_min} min)", f"{n_long:,}",
                    help="Intervalles inter-individus (nouvel individu probable)")
    col_dip4.metric("% longs", f"{pct_long:.1f} %",
                    delta="✓ > 5 %" if pct_long >= 5 else "✗ < 5 %",
                    delta_color="normal" if pct_long >= 5 else "inverse")

    # ── Test de Hartigan ──
    dip_stat, dip_pval, dip_warn = hartigan_dip(gaps_sp_hartigan)

    if dip_warn:
        st.warning(f"⚠️ **Test non applicable** : {dip_warn}")
    elif dip_stat is not None:
        col_h1, col_h2 = st.columns(2)
        col_h1.metric("Hartigan's D", f"{dip_stat:.4f}")
        col_h2.metric("p-value", f"{dip_pval:.4f}",
                      delta="bimodal ✓" if dip_pval < 0.05 else "unimodal ✗",
                      delta_color="normal" if dip_pval < 0.05 else "inverse")
        if dip_pval < 0.05:
            st.success(
                f"✅ **Bimodalité confirmée** (D = {dip_stat:.4f}, p = {dip_pval:.4f} < 0.05) — "
                f"le séparateur de **{sep_min} min** est validé pour *{sp_selected}*."
            )
        else:
            st.warning(
                f"⚠️ **Bimodalité non confirmée** (D = {dip_stat:.4f}, p = {dip_pval:.4f} ≥ 0.05) — "
                f"le séparateur de **{sep_min} min** est à interpréter avec précaution. "
                "Préférer l'activité brute pour cette espèce / période."
            )
    else:
        st.info("Installez `diptest` (`pip install diptest`) pour activer le test de Hartigan.")

    # ── Histogramme ──
    if len(gaps_filtered) == 0:
        st.info("Pas d'intervalles à afficher pour cette espèce.")
    else:
        fig_gap = go.Figure()
        gaps_same = gaps_filtered[gaps_filtered <= sep_min]
        gaps_new  = gaps_filtered[gaps_filtered >  sep_min]

        if len(gaps_same) > 0:
            fig_gap.add_trace(go.Histogram(
                x=gaps_same,
                name=f"≤ {sep_min} min (même individu)",
                marker_color="#1D9E75", opacity=0.85,
                xbins=dict(size=1),
            ))
        if len(gaps_new) > 0:
            fig_gap.add_trace(go.Histogram(
                x=gaps_new,
                name=f"> {sep_min} min (nouvel individu)",
                marker_color="#E24B4A", opacity=0.85,
                xbins=dict(size=1),
            ))

        fig_gap.add_vline(
            x=sep_min, line_dash="dash", line_color="#888",
            annotation_text=f"Seuil = {sep_min} min",
            annotation_position="top right",
        )
        fig_gap.update_layout(
            barmode="overlay",
            xaxis_title="Intervalle (minutes)",
            yaxis_title="Nombre d'intervalles",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            height=380, margin=dict(t=20, b=40),
        )
        st.plotly_chart(fig_gap, use_container_width=True)
        st.caption(
            f"Intervalles > {max_gap_display} min exclus de l'affichage "
            f"({max(0, len(gaps_sp) - len(gaps_filtered))} intervalles masqués). "
            "Le test de Hartigan porte sur la distribution complète (sans coupure)."
        )

    # ── Tableau récapitulatif toutes espèces ──
    st.markdown("---")
    st.subheader("Résultats du test de Hartigan par espèce")
    if not HAS_DIPTEST:
        st.info("Package `diptest` non disponible (`pip install diptest`).")
    else:
        dip_rows = []
        for sp in all_species:
            g = get_gaps_for_species(gap_df, sp)
            d, p, w = hartigan_dip(g)
            n_sp   = len(g)
            nl_sp  = int(np.sum(g > sep_min)) if n_sp else 0
            pct_sp = (nl_sp / n_sp * 100) if n_sp else 0
            dip_rows.append({
                "Espèce": sp,
                "N intervalles": n_sp,
                "% longs": f"{pct_sp:.1f} %",
                "Hartigan D": f"{d:.4f}" if d is not None else "—",
                "p-value":    f"{p:.4f}" if p is not None else "—",
                "Bimodalité": (
                    "✅ confirmée"     if (p is not None and p < 0.05)
                    else "⚠️ non confirmée" if (p is not None)
                    else f"⛔ {w[:50]}…" if w else "—"
                ),
                "Séparateur valide": (
                    "Oui" if (p is not None and p < 0.05)
                    else "Non" if p is not None
                    else "N/A"
                ),
            })
        dip_table = pd.DataFrame(dip_rows)
        st.dataframe(dip_table, use_container_width=True, hide_index=True)
        st.caption(
            "Le test de Hartigan requiert ≥ 30 intervalles et ≥ 5 % d'intervalles longs "
            "(> 10 min) pour être interprétable. En dessous de ces seuils, "
            "D ≈ 0 et p ≈ 1 sont des artefacts numériques sans signification."
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Estimation des individus par nuit
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Individus estimés par nuit et par espèce")

    col_l3, col_r3 = st.columns([3, 2])

    with col_l3:
        sp_filter3 = st.multiselect(
            "Espèces", all_species,
            default=all_species[:min(5, len(all_species))],
            key="sp_filter3"
        )

    summary_f = summary_df[summary_df["Espèce"].isin(sp_filter3)] if sp_filter3 else summary_df
    summary_f = summary_f.copy()
    summary_f["Nuit acoustique"] = summary_f["Nuit acoustique"].astype(str)

    # Graphique individus estimés par nuit
    fig_ind = px.bar(
        summary_f,
        x="Nuit acoustique", y="Individus estimés", color="Espèce",
        color_discrete_map=species_color,
        labels={"Nuit acoustique": "Nuit acoustique"},
        height=340,
    )
    fig_ind.update_layout(
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=10, b=40),
        xaxis=dict(tickangle=-45),
    )
    st.plotly_chart(fig_ind, use_container_width=True)

    # Ratio individus / contacts
    st.markdown("---")
    st.subheader("Ratio individus / contacts")
    ratio_df = summary_f.copy()
    ratio_df["Ratio ind./contacts"] = (
        ratio_df["Individus estimés"] / ratio_df["Contacts"]
    ).round(2)

    fig_ratio = px.scatter(
        ratio_df,
        x="Contacts", y="Individus estimés", color="Espèce",
        color_discrete_map=species_color,
        hover_data=["Nuit acoustique", "Ratio ind./contacts"],
        height=320,
    )
    # Droite de régression manuelle (numpy, sans statsmodels)
    x_all = ratio_df["Contacts"].values.astype(float)
    y_all = ratio_df["Individus estimés"].values.astype(float)
    if len(x_all) >= 2:
        coeffs = np.polyfit(x_all, y_all, 1)
        x_line = np.linspace(x_all.min(), x_all.max(), 100)
        y_line = np.polyval(coeffs, x_line)
        fig_ratio.add_trace(go.Scatter(
            x=x_line, y=y_line,
            mode="lines",
            line=dict(color="#888", width=1.5, dash="dash"),
            name=f"Régression (pente={coeffs[0]:.2f})",
            showlegend=True,
        ))
    fig_ratio.update_layout(margin=dict(t=10, b=40))
    st.plotly_chart(fig_ratio, use_container_width=True)

    # Tableau de synthèse
    st.markdown("---")
    st.subheader("Tableau de synthèse")
    st.dataframe(
        summary_f.sort_values(["Nuit acoustique", "Espèce"]),
        use_container_width=True,
        hide_index=True,
        height=320,
    )

    # Totaux par espèce
    totaux = (
        summary_df.groupby("Espèce")
        .agg(
            Contacts_total=("Contacts", "sum"),
            Individus_total=("Individus estimés", "sum"),
            Nuits=("Nuit acoustique", "nunique"),
        )
        .reset_index()
        .rename(columns={
            "Contacts_total": "Contacts (total)",
            "Individus_total": "Individus estimés (total)",
        })
    )
    totaux["Moy. ind./nuit"] = (totaux["Individus estimés (total)"] / totaux["Nuits"]).round(1)
    st.markdown("**Totaux par espèce (toutes nuits)**")
    st.dataframe(totaux, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Vue phénologique (détail d'une nuit)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Vue phénologique — détail d'une nuit")

    col_n, col_s = st.columns(2)
    with col_n:
        night_list = sorted(df_work["nuit_acoustique"].unique(), reverse=True)
        selected_night = st.selectbox(
            "Nuit acoustique", night_list,
            format_func=str, key="night_select"
        )
    with col_s:
        sp_night = st.selectbox(
            "Espèce", all_species, key="sp_night"
        )

    df_night_sp = df_work[
        (df_work["nuit_acoustique"] == selected_night) &
        (df_work["espece"] == sp_night)
    ].copy()

    if df_night_sp.empty:
        st.info(f"Aucun contact pour *{sp_night}* la nuit du {selected_night}.")
    else:
        times_sorted = sorted(df_night_sp["datetime"])
        individus = assign_individuals(times_sorted, sep_min)
        df_night_sp = df_night_sp.sort_values("datetime").copy()
        df_night_sp["individu"] = individus

        n_ind_night = int(individus.max())
        n_cont_night = len(df_night_sp)
        gaps_night = compute_gaps(times_sorted)

        c1n, c2n, c3n = st.columns(3)
        c1n.metric("Contacts", n_cont_night)
        c2n.metric("Individus estimés", n_ind_night)
        c3n.metric("Intervalle médian", f"{np.median(gaps_night):.0f} min" if len(gaps_night) else "—")

        # Graphique timeline
        max_ind = max(individus)
        colors_ind = [SPECIES_COLORS[i % len(SPECIES_COLORS)] for i in range(max_ind)]

        fig_tl = go.Figure()

        # Barres de contacts colorées par individu
        for idx, (t, ind) in enumerate(zip(times_sorted, individus)):
            col = colors_ind[(ind - 1) % len(colors_ind)]
            fig_tl.add_trace(go.Scatter(
                x=[t, t],
                y=[0, 1],
                mode="lines",
                line=dict(color=col, width=6),
                name=f"Individu {ind}",
                legendgroup=f"ind{ind}",
                showlegend=(idx == list(individus).index(ind)),
                hovertemplate=f"<b>Individu {ind}</b><br>%{{x|%H:%M}}<extra></extra>",
            ))

        # Zones d'appartenance (fond coloré léger)
        grp_starts = {}
        grp_ends = {}
        for t, ind in zip(times_sorted, individus):
            if ind not in grp_starts:
                grp_starts[ind] = t
            grp_ends[ind] = t

        for ind in range(1, max_ind + 1):
            col = colors_ind[(ind - 1) % len(colors_ind)]
            fig_tl.add_vrect(
                x0=grp_starts[ind], x1=grp_ends[ind],
                fillcolor=col, opacity=0.08, line_width=0,
                layer="below",
            )

        # Lignes de séparation (gaps > seuil)
        if len(gaps_night) > 0:
            for i, g in enumerate(gaps_night):
                if g > sep_min:
                    t_mid = times_sorted[i] + timedelta(minutes=g / 2)
                    fig_tl.add_vline(
                        x=times_sorted[i + 1],
                        line_dash="dash", line_color="#E24B4A", line_width=1,
                        annotation_text=f"+{g:.0f}′",
                        annotation_font_size=10,
                        annotation_position="top",
                    )

        fig_tl.update_layout(
            xaxis_title="Heure",
            yaxis=dict(visible=False, range=[-0.2, 1.5]),
            height=220,
            legend=dict(orientation="h", yanchor="bottom", y=1.05, font_size=11),
            margin=dict(t=40, b=40, l=20, r=20),
            hovermode="x unified",
        )
        st.plotly_chart(fig_tl, use_container_width=True)
        st.caption(
            f"Chaque barre verticale = 1 contact. Couleur = individu estimé. "
            f"Ligne rouge pointillée = intervalle > {sep_min} min → séparation d'individus."
        )

        # Tableau des intervalles pour cette nuit
        if len(gaps_night) > 0:
            with st.expander("Détail des intervalles de cette nuit"):
                rows_night = []
                for i, g in enumerate(gaps_night):
                    rows_night.append({
                        "De": times_sorted[i].strftime("%H:%M"),
                        "À": times_sorted[i + 1].strftime("%H:%M"),
                        "Intervalle (min)": round(g, 1),
                        "Statut": f"{'🔴 Nouvel individu' if g > sep_min else '🟢 Même individu'}",
                    })
                st.dataframe(pd.DataFrame(rows_night), use_container_width=True,
                             hide_index=True)

    # Phénologie saisonnière
    st.markdown("---")
    st.subheader("Phénologie saisonnière — individus estimés")
    sp_pheno = st.multiselect(
        "Espèces", all_species,
        default=all_species[:min(4, len(all_species))],
        key="sp_pheno"
    )
    summary_pheno = summary_df[summary_df["Espèce"].isin(sp_pheno)].copy() if sp_pheno else summary_df.copy()
    summary_pheno["Nuit acoustique"] = summary_pheno["Nuit acoustique"].astype(str)

    fig_pheno = px.line(
        summary_pheno,
        x="Nuit acoustique", y="Individus estimés",
        color="Espèce", color_discrete_map=species_color,
        markers=True, height=340,
        labels={"Nuit acoustique": "Nuit acoustique"},
    )
    fig_pheno.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=10, b=40),
        xaxis=dict(tickangle=-45),
    )
    st.plotly_chart(fig_pheno, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Export
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Export des résultats")

    # ── Tableau complet nuit × espèce ──
    st.markdown("**1 · Tableau individus estimés (nuit × espèce)**")
    st.dataframe(summary_df, use_container_width=True, hide_index=True, height=280)

    buf1 = io.BytesIO()
    with pd.ExcelWriter(buf1, engine="openpyxl") as w:
        summary_df.to_excel(w, sheet_name="Individus_nuit_espece", index=False)
    st.download_button(
        "⬇️ Télécharger (Excel)",
        buf1.getvalue(),
        file_name="individus_nuit_espece.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_summary"
    )

    # ── Tableau des intervalles ──
    st.markdown("---")
    st.markdown("**2 · Tableau des intervalles (tous contacts)**")
    gap_export = gap_df.copy()
    gap_export["nuit_acoustique"] = gap_export["nuit_acoustique"].astype(str)
    gap_export["t_debut"] = gap_export["t_debut"].dt.strftime("%Y-%m-%d %H:%M")
    gap_export["t_fin"] = gap_export["t_fin"].dt.strftime("%Y-%m-%d %H:%M")
    gap_export["intervalle_min"] = gap_export["intervalle_min"].round(1)
    gap_export = gap_export.rename(columns={
        "nuit_acoustique": "Nuit acoustique",
        "espece": "Espèce",
        "intervalle_min": "Intervalle (min)",
        "nouveau_individu": "Nouvel individu",
        "t_debut": "Contact précédent",
        "t_fin": "Contact suivant",
    })
    st.dataframe(gap_export, use_container_width=True, hide_index=True, height=280)

    buf2 = io.BytesIO()
    with pd.ExcelWriter(buf2, engine="openpyxl") as w:
        gap_export.to_excel(w, sheet_name="Intervalles", index=False)
    st.download_button(
        "⬇️ Télécharger (Excel)",
        buf2.getvalue(),
        file_name="intervalles_contacts.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_gaps"
    )

    # ── Test de Hartigan ──
    if HAS_DIPTEST:
        st.markdown("---")
        st.markdown("**3 · Résultats test de Hartigan's Dip**")
        dip_rows = []
        for sp in all_species:
            g = get_gaps_for_species(gap_df, sp)
            d, p, w = hartigan_dip(g)
            n_sp  = len(g)
            nl_sp = int(np.sum(g > sep_min)) if n_sp else 0
            dip_rows.append({
                "Espèce": sp,
                "N intervalles": n_sp,
                "N longs (> seuil)": nl_sp,
                "% longs": f"{(nl_sp/n_sp*100):.1f} %" if n_sp else "—",
                "Hartigan D": round(d, 6) if d is not None else None,
                "p-value": round(p, 6) if p is not None else None,
                "Bimodalité confirmée (p<0.05)": (p < 0.05) if p is not None else None,
                "Séparateur valide": (
                    "Oui" if (p is not None and p < 0.05)
                    else "Non" if p is not None
                    else f"N/A — {w[:80]}" if w else "N/A"
                ),
            })
        dip_tbl = pd.DataFrame(dip_rows)
        st.dataframe(dip_tbl, use_container_width=True, hide_index=True)

        buf3 = io.BytesIO()
        with pd.ExcelWriter(buf3, engine="openpyxl") as w:
            dip_tbl.to_excel(w, sheet_name="Hartigan_Dip", index=False)
        st.download_button(
            "⬇️ Télécharger (Excel)",
            buf3.getvalue(),
            file_name="hartigan_dip.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_dip"
        )

    # ── Export complet multi-feuilles ──
    st.markdown("---")
    st.markdown("**4 · Export complet (toutes tables, un seul fichier)**")
    buf4 = io.BytesIO()
    with pd.ExcelWriter(buf4, engine="openpyxl") as w:
        summary_df.to_excel(w, sheet_name="Individus_nuit_espece", index=False)
        gap_export.to_excel(w, sheet_name="Intervalles", index=False)
        if HAS_DIPTEST:
            dip_tbl.to_excel(w, sheet_name="Hartigan_Dip", index=False)
        totaux.to_excel(w, sheet_name="Totaux_par_espece", index=False)

    st.download_button(
        "⬇️ Télécharger le rapport complet (Excel)",
        buf4.getvalue(),
        file_name=f"rapport_separateur_{uploaded.name.split('.')[0]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_full"
    )

    # ── Paramètres de l'analyse (traçabilité) ──
    st.markdown("---")
    st.markdown("**5 · Paramètres de l'analyse (traçabilité)**")
    params = {
        "Fichier source": uploaded.name,
        "Séparateur (min)": sep_min,
        "Colonne date-heure": col_datetime or f"{col_date_sep} + {col_time_sep}",
        "Colonne espèce": col_species,
        "Nuits analysées": n_nights,
        "Espèces": ", ".join(all_species),
        "Total contacts": total_contacts,
        "Total individus estimés": int(total_individus),
        "diptest disponible": str(HAS_DIPTEST),
        "Référence méthode": "Seebens-Hoyer et al. (2026), Biological Conservation 316, 111741",
    }
    st.json(params)
