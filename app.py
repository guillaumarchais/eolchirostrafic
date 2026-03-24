"""
Eol chiros trafic : convertisseur d'activité en estimations d'individus
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


# Plafond biologique pour le test de Hartigan :
# Au-delà de 4 × séparateur, tous les gaps signifient "individu différent".
# Les inclure trop longs dilue le 2e mode en une queue plate et empêche le
# Dip test de détecter deux pics concentrés même quand la bimodalité est réelle.
_HARTIGAN_CAP_DEFAULT = 90  # minutes


def bimodality_coefficient(arr_log):
    """
    Bimodality Coefficient (BC) sur distribution log-transformée.
    BC = (γ² + 1) / (κ_corr)  où γ = skewness, κ = kurtosis corrigé.
    BC > 5/9 ≈ 0.555 suggère une distribution bimodale.
    Référence : SAS Institute (1990), repris par Pfister et al. (2013).
    Avantage vs Dip test : robuste aux distributions très déséquilibrées
    (ratio courts/longs élevé), ce qui est typique en acoustique chiroptères.
    """
    n = len(arr_log)
    if n < 4:
        return None
    s = float(pd.Series(arr_log).skew())
    k = float(pd.Series(arr_log).kurtosis())  # excess kurtosis
    # Correction de taille d'échantillon
    k_corr = k + 3 * (n - 1)**2 / ((n - 2) * (n + 1))
    if k_corr == 0:
        return None
    return (s**2 + 1) / k_corr


def test_bimodalite(gaps, sep_min=20):
    """
    Teste la bimodalité des intervalles inter-contacts.
    Retourne un dict avec :
      - bc      : Bimodality Coefficient (log1p, cap=max(4×sep,90))
      - bc_ok   : BC > 0.555
      - dip_d   : statistique D du Dip test (si diptest installé)
      - dip_p   : p-value du Dip test
      - dip_ok  : p < 0.05
      - n_test  : n utilisé pour le test (après cap + log)
      - warn    : message si test non applicable (str ou None)
    """
    cap = max(4 * sep_min, 90)
    arr = np.asarray(gaps, dtype=float)
    arr = arr[(arr >= 0) & (arr <= cap)]
    n = len(arr)

    if n < 30:
        return {"bc": None, "bc_ok": None, "dip_d": None, "dip_p": None,
                "dip_ok": None, "n_test": n, "cap": cap,
                "warn": (f"Effectif insuffisant ({n} intervalles ≤ {cap} min, "
                         "minimum 30 requis).")}

    pct_long = float(np.mean(arr > sep_min) * 100)
    if pct_long < 5:
        return {"bc": None, "bc_ok": None, "dip_d": None, "dip_p": None,
                "dip_ok": None, "n_test": n, "cap": cap,
                "warn": (f"Mode long absent : seulement {pct_long:.1f} % des intervalles "
                         f"dépassent {sep_min} min (seuil : 5 %). "
                         "Préférer l'activité brute pour cette espèce.")}

    arr_log = np.log1p(arr)

    bc = bimodality_coefficient(arr_log)
    bc_ok = (bc > 0.555) if bc is not None else None

    dip_d = dip_p = dip_ok = None
    if HAS_DIPTEST:
        dip_d, dip_p = _diptest.diptest(arr_log)
        dip_d, dip_p = float(dip_d), float(dip_p)
        dip_ok = dip_p < 0.05

    return {"bc": bc, "bc_ok": bc_ok, "dip_d": dip_d, "dip_p": dip_p,
            "dip_ok": dip_ok, "n_test": n, "cap": cap, "warn": None}


def verdict_bimodalite(res):
    """
    Interprétation synthétique du résultat des tests.
    Retourne (label_court, emoji, detail).
    """
    if res["warn"]:
        return "N/A", "⛔", res["warn"]
    bc_ok  = res["bc_ok"]
    dip_ok = res["dip_ok"]
    if dip_ok is None:
        # Seulement BC disponible
        if bc_ok:
            return "confirmée (BC)", "✅", f"BC = {res['bc']:.3f} > 0.555"
        else:
            return "non confirmée", "⚠️", f"BC = {res['bc']:.3f} ≤ 0.555"
    # Les deux tests disponibles
    if bc_ok and dip_ok:
        return "confirmée", "✅", f"BC={res['bc']:.3f}  D={res['dip_d']:.4f}  p={res['dip_p']:.4f}"
    elif bc_ok and not dip_ok:
        return "probable (BC✓ Dip✗)", "🟡", f"BC={res['bc']:.3f}  D={res['dip_d']:.4f}  p={res['dip_p']:.4f}"
    elif not bc_ok and dip_ok:
        return "probable (Dip✓ BC✗)", "🟡", f"BC={res['bc']:.3f}  D={res['dip_d']:.4f}  p={res['dip_p']:.4f}"
    else:
        return "non confirmée", "⚠️", f"BC={res['bc']:.3f}  D={res['dip_d']:.4f}  p={res['dip_p']:.4f}"



def get_gaps_for_species(gap_df, sp, max_gap_min=480):
    """
    Extrait les intervalles intra-nuit pour une espèce depuis gap_df.
    max_gap_min=480 filtre les artefacts > 8h (pour l'histogramme).
    Le plafonnement pour les tests de bimodalité est géré dans test_bimodalite().
    """
    if gap_df.empty or sp not in gap_df["espece"].values:
        return np.array([])
    arr = gap_df[gap_df["espece"] == sp]["intervalle_min"].values.astype(float)
    return arr[arr <= max_gap_min]


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

    # Détection automatique : si une colonne contient "heure" ou "time" ET
    # une autre contient "date", on a probablement deux colonnes séparées.
    _has_time_col = any(any(k in c.lower() for k in ["heure", "time"]) for c in cols)
    _has_date_col = any("date" in c.lower() for c in cols)
    _has_datetime_col = any(
        any(k in c.lower() for k in ["datetime", "date_heure", "dateheure", "timestamp"])
        for c in cols
    )
    _auto_mode = (
        "Deux colonnes séparées"
        if (_has_time_col and _has_date_col and not _has_datetime_col)
        else "Colonne unique (date + heure)"
    )

    dt_mode = st.radio(
        "Format date/heure",
        ["Colonne unique (date + heure)", "Deux colonnes séparées"],
        index=["Colonne unique (date + heure)", "Deux colonnes séparées"].index(_auto_mode),
        horizontal=True,
        help="Détection automatique — modifiez si nécessaire.",
    )

    if dt_mode == "Colonne unique (date + heure)":
        col_datetime = st.selectbox("Colonne date-heure", cols,
                                    index=next((i for i, c in enumerate(cols)
                                                if any(k in c.lower() for k in
                                                       ["datetime", "date", "time", "heure"])), 0))
        col_date_sep = col_time_sep = None
        # Vérification : la colonne doit contenir une heure réelle
        _test_dt = pd.to_datetime(raw_df[col_datetime].dropna().iloc[:10],
                                  dayfirst=True, errors="coerce")
        if (_test_dt.dt.hour == 0).all():
            st.warning(
                f"⚠️ La colonne **{col_datetime}** ne semble contenir que des dates sans heure. "
                "Si vos données ont une colonne heure séparée, passez en mode "
                "**Deux colonnes séparées** ci-dessus."
            )
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
st.title("🦇 Eol chiros trafic : convertisseur d'activité en estimations d'individus")
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

    # ── Tests de bimodalité ──
    res = test_bimodalite(gaps_sp_hartigan, sep_min=sep_min)
    label, emoji, detail = verdict_bimodalite(res)

    if res["warn"]:
        st.warning(f"⛔ **Test non applicable** : {res['warn']}")
    else:
        col_h1, col_h2, col_h3 = st.columns(3)
        col_h1.metric("BC (log)",
                      f"{res['bc']:.3f}" if res["bc"] is not None else "—",
                      delta="✓ > 0.555" if res["bc_ok"] else "✗ ≤ 0.555",
                      delta_color="normal" if res["bc_ok"] else "inverse",
                      help="Bimodality Coefficient sur log(intervalles). BC > 0.555 → bimodale.")
        if res["dip_d"] is not None:
            col_h2.metric("Dip D (log)", f"{res['dip_d']:.4f}")
            col_h3.metric("p-value Dip", f"{res['dip_p']:.4f}",
                          delta="✓ < 0.05" if res["dip_ok"] else "✗ ≥ 0.05",
                          delta_color="normal" if res["dip_ok"] else "inverse")
        else:
            col_h2.metric("Dip D", "—", help="Installez `diptest` pour activer.")
            col_h3.metric("p-value", "—")

        if label.startswith("confirmée"):
            st.success(f"{emoji} **Bimodalité {label}** — {detail} — "
                       f"séparateur de **{sep_min} min** validé pour *{sp_selected}*.")
        elif label.startswith("probable"):
            st.info(f"{emoji} **Bimodalité {label}** — {detail} — "
                    f"résultats des deux tests divergents, interpréter avec prudence.")
        else:
            st.warning(f"{emoji} **Bimodalité {label}** — {detail} — "
                       f"préférer l'activité brute pour cette espèce / période.")
        st.caption(
            f"Tests calculés sur log₁₊ₓ(intervalles) plafonnés à {res['cap']} min "
            f"(n={res['n_test']}). La transformation log compresse le pic court "
            "et rend les deux modes comparables — recommandée pour les distributions "
            "de temps inter-événements."
        )

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
    st.subheader("Résultats des tests de bimodalité par espèce")
    bm_rows = []
    for sp in all_species:
        g   = get_gaps_for_species(gap_df, sp)
        res = test_bimodalite(g, sep_min=sep_min)
        lbl, emj, det = verdict_bimodalite(res)
        n_sp  = len(g)
        nl_sp = int(np.sum(g > sep_min)) if n_sp else 0
        bm_rows.append({
            "Espèce":           sp,
            "N gaps (brut)":   n_sp,
            "N gaps (test)":   res["n_test"],
            "% longs":         f"{(nl_sp/n_sp*100):.1f} %" if n_sp else "—",
            "BC (log)":        f"{res['bc']:.3f}" if res["bc"] is not None else "—",
            "Dip D":           f"{res['dip_d']:.4f}" if res["dip_d"] is not None else "—",
            "p-value":         f"{res['dip_p']:.4f}" if res["dip_p"] is not None else "—",
            "Bimodalité":      f"{emj} {lbl}",
            "Séparateur valide": ("Oui" if "confirmée" in lbl else
                                  "Probable" if "probable" in lbl else
                                  "Non" if "non confirmée" in lbl else "N/A"),
        })
    bm_table = pd.DataFrame(bm_rows)
    st.dataframe(bm_table, use_container_width=True, hide_index=True)
    st.caption(
        "BC = Bimodality Coefficient sur log₁₊ₓ(intervalles plafonnés). "
        "BC > 0.555 → bimodale. Dip test calculé sur la même distribution log. "
        "Plafond = max(4 × séparateur, 90 min)."
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

    # ── Tests de bimodalité (export) ──
    st.markdown("---")
    st.markdown("**3 · Résultats tests de bimodalité (BC + Dip)**")
    bm_rows_exp = []
    for sp in all_species:
        g   = get_gaps_for_species(gap_df, sp)
        res = test_bimodalite(g, sep_min=sep_min)
        lbl, emj, det = verdict_bimodalite(res)
        n_sp  = len(g)
        nl_sp = int(np.sum(g > sep_min)) if n_sp else 0
        bm_rows_exp.append({
            "Espèce":             sp,
            "N gaps brut":        n_sp,
            "N gaps (test)":      res["n_test"],
            "Plafond (min)":      res["cap"],
            "% longs":            round(nl_sp/n_sp*100, 1) if n_sp else None,
            "BC (log)":           round(res["bc"], 4) if res["bc"] is not None else None,
            "BC > 0.555":         res["bc_ok"],
            "Dip D":              round(res["dip_d"], 6) if res["dip_d"] is not None else None,
            "p-value Dip":        round(res["dip_p"], 6) if res["dip_p"] is not None else None,
            "Bimodalité":         f"{emj} {lbl}",
            "Séparateur valide":  ("Oui" if "confirmée" in lbl else
                                   "Probable" if "probable" in lbl else
                                   "Non" if "non confirmée" in lbl else "N/A"),
        })
    dip_tbl = pd.DataFrame(bm_rows_exp)
    st.dataframe(dip_tbl, use_container_width=True, hide_index=True)

    buf3 = io.BytesIO()
    with pd.ExcelWriter(buf3, engine="openpyxl") as w:
        dip_tbl.to_excel(w, sheet_name="Tests_bimodalite", index=False)
    st.download_button(
        "⬇️ Télécharger (Excel)",
        buf3.getvalue(),
        file_name="tests_bimodalite.xlsx",
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
            dip_tbl.to_excel(w, sheet_name="Tests_bimodalite", index=False)
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
