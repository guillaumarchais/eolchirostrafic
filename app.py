import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import timedelta
import io
import base64

# ── IMPORTATION DES TRADUCTIONS ──────────────────────────────────────────────
try:
    from translations import LANGUAGES
except ImportError:
    st.error("Le fichier 'translations.py' est manquant.")
    st.stop()

# ── CONFIGURATION DE LA PAGE ─────────────────────────────────────────────────
st.set_page_config(page_title="Seebens-Hoyer Tool", layout="wide")

# ── SÉLECTION DE LA LANGUE (SIDEBAR) ──────────────────────────────────────────
# Placé en haut pour que 't' soit disponible pour tout le script
selected_lang = st.sidebar.selectbox("🌐 Langue / Language", ["Français", "Scientific English"])
L = "FR" if selected_lang == "Français" else "EN"
t = LANGUAGES[L]

# ── DÉPENDANCE OPTIONNELLE : DIPTEST ──────────────────────────────────────────
try:
    import diptest as _diptest
    HAS_DIPTEST = True
except ImportError:
    HAS_DIPTEST = False

# ── DONNÉES DE DÉMONSTRATION ──────────────────────────────────────────────────
_DEMO_CSV_B64 = (
    "RGF0ZTtIZXVyZTtFc3BlY2UNCjAyLzAzLzIwMjM7MDI6MDQ6MDA7TnljdGFsdXMNCjAyLzAzLzIwMjM7MDI6MDQ6NTM7TnljdGFsdXMNCjAyLzAzLzIwMjM7MDI6MDU6Mzc7TnljdGFsdXMNCjAyLzAzLzIwMjM7MDI6MDY6MDM7TnljdGFsdXMNCjA1LzAzLzIwMjM7MjM6NTM6Mjg7UGlwaXN0cmVsbHVzIG5hdGh1c2lpDQowNS8wMy8yMDIzOzIzOjU0OjExO1BpcGlzdHJlbGx1cyBuYXRodXNpaQ0KMDUvMDMvMjAyMzs0OjAwOjAwO1BpcGlzdHJlbGx1cyBuYXRodXNpaQ0KMDUvMDMvMjAyMzs0OjA1OjAwO1BpcGlzdHJlbGx1cyBuYXRodXNpaQ=="
)

def try_parse_datetime(df, col_dt=None, col_date=None, col_time=None):
    try:
        if col_dt:
            # Correction : suppression de infer_datetime_format (obsolète)
            return pd.to_datetime(df[col_dt], dayfirst=True)
        else:
            combined = df[col_date].astype(str) + " " + df[col_time].astype(str)
            return pd.to_datetime(combined, dayfirst=True)
    except Exception as e:
        st.error(f"{t['err_date']} {e}")
        return None

# ── INTERFACE UTILISATEUR ─────────────────────────────────────────────────────
st.title(t["app_title"])

# 1 · Import des données
st.sidebar.header(t["sidebar_params"])
st.sidebar.subheader(t["step_1"])

df_input = None
if st.sidebar.button(t["load_demo"]):
    csv_text = base64.b64decode(_DEMO_CSV_B64).decode("utf-8")
    df_input = pd.read_csv(io.StringIO(csv_text), sep=";")
    st.sidebar.success(t["demo_loaded"])

uploaded_file = st.sidebar.file_uploader(t["upload_label"], type=["csv", "xlsx", "xls"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df_input = pd.read_csv(uploaded_file, sep=None, engine="python")
    else:
        df_input = pd.read_excel(uploaded_file)

if df_input is not None:
    cols = df_input.columns.tolist()
    
    # 2 · Mapping des colonnes
    st.sidebar.subheader(t["step_2"])
    mode_dt = st.sidebar.radio(t["format_dt"], [t["single_col"], t["two_cols"]])
    
    col_dt, col_date, col_time = None, None, None
    if mode_dt == t["single_col"]:
        col_dt = st.sidebar.selectbox(t["col_dt"], cols)
    else:
        col_date = st.sidebar.selectbox(t["col_date"], cols)
        col_time = st.sidebar.selectbox(t["col_time"], cols)
    
    col_sp = st.sidebar.selectbox(t["col_sp"], cols, index=min(2, len(cols)-1))

    # 3 · Séparateur d'individus
    st.sidebar.subheader(t["step_3"])
    gap_minutes = st.sidebar.slider(t["interval_label"], 1, 60, 5)

    # 4 · Filtres
    st.sidebar.subheader(t["step_4"])
    min_contacts_night = st.sidebar.number_input(t["min_contacts"], 1, 1000, 5)

    # ── ANALYSE ───────────────────────────────────────────────────────────────
    if st.sidebar.button(t["run_btn"]):
        df_input["_dt"] = try_parse_datetime(df_input, col_dt, col_date, col_time)
        
        if df_input["_dt"] is not None:
            st.header(t["results_header"])
            
            # Paramètres globaux
            species_list = sorted(df_input[col_sp].unique())
            all_dates = df_input["_dt"].dt.date.unique()
            n_nuits_total = len(all_dates)
            per_start, per_end = min(all_dates), max(all_dates)

            for sp in species_list:
                with st.expander(f"🦇 {sp}", expanded=True):
                    df_sp = df_input[df_input[col_sp] == sp].sort_values("_dt")
                    n_contacts_total = len(df_sp)
                    n_nuits_sp = len(df_sp["_dt"].dt.date.unique())
                    
                    # Logique simplifiée Seebens-Hoyer pour l'exemple
                    # (Ici vous gardez votre algorithme de calcul d'individus)
                    est_indiv = 1 # Valeur par défaut pour l'exemple
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric(t["stat_total_nights"], n_nuits_sp)
                    c2.metric(t["stat_total_contacts"], n_contacts_total)
                    c3.metric(t["stat_indiv_est"], est_indiv)

                    # Graphique
                    fig = px.histogram(df_sp, x="_dt", title=f"{t['chart_title']} : {sp}")
                    st.plotly_chart(fig, use_container_width=True)

                    # Rapport automatique
                    st.markdown(f"#### {t['report_gen']}")
                    if n_contacts_total >= min_contacts_night:
                        txt = t["summary_template_full"].format(
                            sp=sp, start=per_start, end=per_end, 
                            n_nights_total=n_nuits_total, n_contacts_total=n_contacts_total,
                            n_nuits_sp=n_nuits_sp, n_ind=est_indiv, pic_date="-"
                        )
                    else:
                        txt = t["summary_template_excl"].format(
                            sp=sp, start=per_start, end=per_end,
                            n_nights_total=n_nuits_total, n_contacts_total=n_contacts_total,
                            n_nuits_sp=n_nuits_sp, motif=t["excl_reason_low"]
                        )
                    st.code(txt, language=None)

            st.caption(t["report_caption"])
            st.markdown(f"--- \n {t['method_note']}")
else:
    st.info(t["no_data"])
