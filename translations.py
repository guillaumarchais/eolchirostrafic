# translations.py

LANGUAGES = {
    "FR": {

        # ── Page / App ────────────────────────────────────────────────────────
        "page_title": "Séparateur d'individus — Chiroptères",
        "app_title": "🦇 Séparateur d'individus — Acoustique chiroptères",
        "author_credit": "Application conçue par Guillaume Marchais",

        # ── Sidebar ───────────────────────────────────────────────────────────
        "sidebar_title": "🦇 Paramètres",
        "sidebar_import": "1 · Import des données",
        "sidebar_mapping": "2 · Mapping des colonnes",
        "sidebar_separator": "3 · Séparateur d'individus",
        "sidebar_filters": "4 · Filtres (optionnel)",

        # ── Demo buttons ──────────────────────────────────────────────────────
        "btn_load_demo": "🦇 Charger une démo",
        "btn_load_demo_help": "Charge un jeu de données fictif (6 espèces, 210 nuits, France 2023).",
        "btn_remove_demo": "✖ Retirer la démo",
        "info_demo_loaded": "✅ Données de démonstration chargées.",
        "or_label": "— ou —",

        # ── File uploader ─────────────────────────────────────────────────────
        "file_uploader_label": "Importer votre tableur (CSV ou Excel)",
        "file_uploader_help": "Le fichier doit contenir au minimum une colonne date/heure et une colonne espèce.",
        "info_upload_prompt": "Importez un fichier ou chargez la démo pour commencer.",
        "format_expected": (
            "**Format attendu :**\n"
            "| Date | Heure | Espèce |\n"
            "|------|-------|--------|\n"
            "| 15/08/2023 | 22:14 | Pipistrellus nathusii |\n"
            "| 15/08/2023 | 22:31 | Nyctalus noctula |\n"
            "| … | … | … |\n\n"
            "Les colonnes Date et Heure peuvent être fusionnées ou séparées."
        ),

        # ── Column mapping ────────────────────────────────────────────────────
        "datetime_format": "Format date/heure",
        "dt_mode_single": "Colonne unique (date + heure)",
        "dt_mode_double": "Deux colonnes séparées",
        "dt_mode_help": "Détection automatique — modifiez si nécessaire.",
        "col_datetime_label": "Colonne date-heure",
        "col_date_label": "Colonne date",
        "col_time_label": "Colonne heure",
        "col_species_label": "Colonne espèce",
        "warning_no_time": (
            "⚠️ La colonne **{col}** ne semble contenir que des dates sans heure. "
            "Si vos données ont une colonne heure séparée, passez en mode "
            "**Deux colonnes séparées** ci-dessus."
        ),

        # ── Slider / filters ──────────────────────────────────────────────────
        "slider_label": "Intervalle sans activité (minutes)",
        "slider_help": "Deux contacts séparés de plus de N minutes sont attribués à des individus distincts.",
        "filter_period_label": "Filtrer par période migratoire",
        "date_range_label": "Période à analyser",
        "date_range_help": "Laisser vide = toutes les dates.",
        "min_contacts_label": "Contacts minimum par nuit × espèce",
        "min_contacts_help": "Exclure les nuits avec trop peu de contacts pour une espèce donnée.",
        "warning_diptest": "⚠️ Package `diptest` non installé — test de Hartigan désactivé.\n\n`pip install diptest`",

        # ── Data errors / warnings ────────────────────────────────────────────
        "error_datetime": "Impossible de lire les dates/heures : ",
        "warning_no_data": "Aucune donnée après filtrage. Vérifiez les paramètres.",

        # ── App header / caption ──────────────────────────────────────────────
        "caption_file": "Fichier",
        "caption_separator": "Séparateur",
        "caption_method": "Méthode",

        # ── Summary metrics ───────────────────────────────────────────────────
        "metric_nights": "Nuits analysées",
        "metric_contacts": "Contacts totaux",
        "metric_individuals": "Individus estimés",
        "metric_species": "Espèces",

        # ── Tabs ──────────────────────────────────────────────────────────────
        "tab_data": "📋 Données",
        "tab_distribution": "📊 Distribution des intervalles",
        "tab_estimation": "🦇 Estimation par nuit",
        "tab_phenology": "🗓️ Vue phénologique",
        "tab_export": "💾 Export",
        "tab_report": "📝 Rapport",

        # ── Column display names (used across tabs) ───────────────────────────
        "col_datetime_display": "Date-heure",
        "col_species_display": "Espèce",
        "col_night_display": "Nuit acoustique",
        "col_contacts": "Contacts",
        "col_nights": "Nuits",
        "col_ind_display": "Individus estimés",
        "col_ratio": "Ratio ind./contacts",
        "col_contacts_total": "Contacts (total)",
        "col_ind_total": "Individus estimés (total)",
        "col_avg_ind": "Moy. ind./nuit",
        "acoustic_nights": "nuits acoustiques",

        # ── Tab 1 ─────────────────────────────────────────────────────────────
        "tab1_title": "Aperçu des données importées",
        "tab1_subtitle": "Contacts par nuit et par espèce",
        "display_limit": "Affichage limité aux 500 premières lignes sur {n:,}.",
        "contacts_by_species": "**Contacts par espèce**",
        "time_range_label": "**Plage temporelle**",
        "species_to_display": "Espèces à afficher",

        # ── Tab 2 ─────────────────────────────────────────────────────────────
        "tab2_title": "Distribution des intervalles entre contacts consécutifs",
        "tab2_subtitle": "Résultats des tests de bimodalité par espèce",
        "species_label": "Espèce",
        "max_gap_label": "Intervalle max affiché (min)",
        "max_gap_help": "Pour zoomer sur la zone du séparateur.",

        "metric_gaps": "Intervalles analysés",
        "metric_short": "Courts (≤ {sep} min)",
        "metric_short_help": "Intervalles intra-individu (même individu probable)",
        "metric_long": "Longs (> {sep} min)",
        "metric_long_help": "Intervalles inter-individus (nouvel individu probable)",
        "metric_pct_long": "% longs",
        "delta_pct_ok": "✓ > 5 %",
        "delta_pct_nok": "✗ < 5 %",

        "warning_test_na": "⛔ **Test non applicable** : ",
        "metric_bc": "BC (log)",
        "metric_bc_help": "Bimodality Coefficient sur log(intervalles). BC > 0.555 → bimodale.",
        "delta_bc_ok": "✓ > 0.555",
        "delta_bc_nok": "✗ ≤ 0.555",
        "metric_dip_d": "Dip D (log)",
        "metric_pvalue": "p-value Dip",
        "delta_pvalue_ok": "✓ < 0.05",
        "delta_pvalue_nok": "✗ ≥ 0.05",
        "metric_dip_d_na": "Dip D",
        "metric_dip_d_na_help": "Installez `diptest` pour activer.",
        "metric_pvalue_na": "p-value",

        "success_bimodal": "{emoji} **Bimodalité {lbl}** — {detail} — séparateur de **{sep} min** validé pour *{sp}*.",
        "info_bimodal_probable": "{emoji} **Bimodalité {lbl}** — {detail} — résultats des deux tests divergents, interpréter avec prudence.",
        "warning_bimodal_not": "{emoji} **Bimodalité {lbl}** — {detail} — préférer l'activité brute pour cette espèce / période.",
        "caption_test_method": (
            "Tests calculés sur log₁₊ₓ(intervalles) plafonnés à {cap} min "
            "(n={n}). La transformation log compresse le pic court "
            "et rend les deux modes comparables — recommandée pour les distributions "
            "de temps inter-événements."
        ),

        "hist_no_data": "Pas d'intervalles à afficher pour cette espèce.",
        "hist_same": "≤ {sep} min (même individu)",
        "hist_new": "> {sep} min (nouvel individu)",
        "hist_threshold": "Seuil = {sep} min",
        "xaxis_interval": "Intervalle (minutes)",
        "yaxis_count": "Nombre d'intervalles",
        "caption_hist": (
            "Intervalles > {max} min exclus de l'affichage "
            "({n} intervalles masqués). "
            "Le test de Hartigan porte sur la distribution complète (sans coupure)."
        ),

        "col_n_gaps_raw": "N gaps (brut)",
        "col_n_gaps_test": "N gaps (test)",
        "col_pct_long": "% longs",
        "col_bc": "BC (log)",
        "col_dip_d": "Dip D",
        "col_pvalue": "p-value",
        "col_bimodality": "Bimodalité",
        "col_sep_valid": "Séparateur valide",
        "val_yes": "Oui",
        "val_probable": "Probable",
        "val_no": "Non",
        "val_na": "N/A",
        "caption_bc_explanation": (
            "BC = Bimodality Coefficient sur log₁₊ₓ(intervalles plafonnés). "
            "BC > 0.555 → bimodale. Dip test calculé sur la même distribution log. "
            "Plafond = max(4 × séparateur, 90 min)."
        ),

        # ── Tab 3 ─────────────────────────────────────────────────────────────
        "tab3_title": "Individus estimés par nuit et par espèce",
        "tab3_subtitle_ratio": "Ratio individus / contacts",
        "tab3_subtitle_table": "Tableau de synthèse",
        "regression_label": "Régression (pente={slope:.2f})",
        "totaux_by_species": "**Totaux par espèce (toutes nuits)**",

        # ── Tab 4 ─────────────────────────────────────────────────────────────
        "tab4_title": "Vue phénologique — détail d'une nuit",
        "tab4_subtitle_pheno": "Phénologie saisonnière — individus estimés",
        "no_contact_info": "Aucun contact pour *{sp}* la nuit du {night}.",
        "metric_median_gap": "Intervalle médian",
        "individual_label": "Individu {n}",
        "hover_individual": "<b>Individu {n}</b><br>%{{x|%H:%M}}<extra></extra>",
        "xaxis_time": "Heure",
        "caption_timeline": (
            "Chaque barre verticale = 1 contact. Couleur = individu estimé. "
            "Ligne rouge pointillée = intervalle > {sep} min → séparation d'individus."
        ),
        "expander_intervals": "Détail des intervalles de cette nuit",
        "col_from": "De",
        "col_to": "À",
        "col_interval_min": "Intervalle (min)",
        "col_status": "Statut",
        "status_new": "🔴 Nouvel individu",
        "status_same": "🟢 Même individu",

        # ── Tab 5 ─────────────────────────────────────────────────────────────
        "tab5_title": "Export des résultats",
        "export_section1": "**1 · Tableau individus estimés (nuit × espèce)**",
        "export_section2": "**2 · Tableau des intervalles (tous contacts)**",
        "export_section3": "**3 · Résultats tests de bimodalité (BC + Dip)**",
        "export_section4": "**4 · Export complet (toutes tables, un seul fichier)**",
        "export_section5": "**5 · Paramètres de l'analyse (traçabilité)**",
        "download_excel": "⬇️ Télécharger (Excel)",
        "download_full": "⬇️ Télécharger le rapport complet (Excel)",

        "col_new_ind_exp": "Nouvel individu",
        "col_prev_contact": "Contact précédent",
        "col_next_contact": "Contact suivant",
        "col_n_gaps_raw_exp": "N gaps brut",
        "col_cap": "Plafond (min)",
        "col_bc_ok": "BC > 0.555",
        "col_pvalue_dip": "p-value Dip",

        "param_source": "Fichier source",
        "param_separator": "Séparateur (min)",
        "param_col_dt": "Colonne date-heure",
        "param_col_sp": "Colonne espèce",
        "param_nights": "Nuits analysées",
        "param_species": "Espèces",
        "param_total_contacts": "Total contacts",
        "param_total_ind": "Total individus estimés",
        "param_diptest": "diptest disponible",
        "param_reference": "Référence méthode",

        # ── Tab 6 — Rapport ───────────────────────────────────────────────────
        "tab6_title": "Rapport — Texte de conclusion par espèce",
        "report_intro": (
            "Ce texte synthétique est prêt à être intégré dans un rapport d'étude d'impact. "
            "Il est généré automatiquement à partir des résultats de l'analyse avec le séparateur "
            "de **{sep} min** et la méthode Seebens-Hoyer et al. (2026)."
        ),
        "copy_button": "📋 Copier le texte brut",
        "caption_report": (
            "Les textes ci-dessus sont générés automatiquement à partir des paramètres de l'analyse. "
            "Ils doivent être adaptés au contexte de l'étude (type de projet, localisation, "
            "espèces protégées concernées) avant intégration dans un rapport réglementaire."
        ),

        "motif_insufficient": (
            "en raison d'un effectif insuffisant "
            "({n} intervalles disponibles, minimum 30 requis pour le test de bimodalité)"
        ),
        "motif_no_long_mode": (
            "en raison de l'absence de mode long dans la distribution des intervalles "
            "({pct} % des intervalles dépassent {sep} min)"
        ),
        "motif_not_confirmed": (
            "la distribution des intervalles ne présente pas "
            "de structure bimodale significative (BC = {bc})"
        ),
        "motif_default": "les conditions d'application du test de bimodalité ne sont pas réunies",

        "report_valide": (
            "**{sp}**\n\n"
            "Au cours de la période de suivi ({periode_debut} au {periode_fin}, {n_nuits_total} nuits), "
            "l'espèce *{sp}* a été contactée {n_contacts_total} fois sur {n_nuits_sp} nuits de présence, "
            "soit en moyenne {contacts_moy} contacts/nuit.\n\n"
            "**Estimation du nombre d'individus (méthode du séparateur, {sep_min} min)**\n\n"
            "Le test de bimodalité des intervalles entre contacts (Bimodality Coefficient, BC = {bc_str}) "
            "confirme la structure bimodale de la distribution : un pic d'intervalles courts "
            "(< {sep_min} min, intra-individu) et un second pic d'intervalles longs "
            "(> {sep_min} min, inter-individus). La méthode du séparateur est donc applicable pour cette espèce.\n\n"
            "Un total de **{n_ind_total} occurrences d'individus distincts** a été estimé sur l'ensemble "
            "de la période, soit une moyenne de **{ind_moy} occurrence(s) d'individu(s) par nuit de présence**. "
            "La nuit la plus active est celle du {pic_date} avec {pic_ind} individu(s) estimé(s).\n\n"
            "⚠️ *Note : un même individu peut être détecté à plusieurs reprises au cours de nuits successives. "
            "Le total ci-dessus représente donc le cumul des occurrences nocturnes d'individus distincts "
            "au sein de chaque nuit, et non nécessairement le nombre d'individus uniques sur l'ensemble "
            "de la période de suivi.*\n\n"
            "Ces résultats constituent une estimation minimale conservative (Seebens-Hoyer et al., 2026). "
            "Ils permettent d'évaluer l'exposition potentielle de l'espèce au risque de collision avec "
            "les éoliennes et de dimensionner les mesures de bridage à mettre en œuvre.\n\n"
            "*Référence : Seebens-Hoyer et al. (2026). Estimating the traffic rates of bats migrating "
            "across the North and Baltic Seas to develop efficient mitigation measures at offshore wind "
            "energy facilities. Biological Conservation, 316, 111741.*"
        ),
        "report_nonvalide": (
            "**{sp}**\n\n"
            "Au cours de la période de suivi ({periode_debut} au {periode_fin}, {n_nuits_total} nuits), "
            "l'espèce *{sp}* a été contactée {n_contacts_total} fois sur {n_nuits_sp} nuits de présence, "
            "soit en moyenne {contacts_moy} contacts/nuit.\n\n"
            "**Indicateur retenu : activité brute (contacts)**\n\n"
            "La méthode du séparateur n'a pas été appliquée pour cette espèce, {motif_excl}. "
            "L'activité brute est conservée comme indicateur de fréquentation du site.\n\n"
            "Par défaut, on peut néanmoins retenir qu'au moins **un individu distinct** a été détecté "
            "pour chaque nuit de présence, quel que soit le nombre de contacts enregistrés au cours de "
            "cette même nuit. Cela représente un minimum de **{n_nuits_sp} occurrence(s) d'individu(s)** "
            "sur l'ensemble de la période.\n\n"
            "La nuit la plus active est celle du {pic_date}. Ces données d'activité permettent de qualifier "
            "la présence de l'espèce sur le site d'étude, mais ne permettent pas d'estimer le nombre "
            "d'individus distincts ayant transité. En l'absence de conversion en individus, l'appréciation "
            "du risque de collision doit s'appuyer sur les indices d'activité brute et les données "
            "bibliographiques disponibles pour l'espèce."
        ),
        "report_raw_valide": (
            "{sp}\n\n"
            "Au cours de la période de suivi ({periode_debut} au {periode_fin}, "
            "{n_nuits_total} nuits), l'espèce {sp} a été contactée "
            "{n_contacts_total} fois sur {n_nuits_sp} nuits de présence, "
            "soit en moyenne {contacts_moy} contacts/nuit.\n\n"
            "Estimation du nombre d'individus (méthode du séparateur, {sep_min} min)\n\n"
            "Le test de bimodalité (BC = {bc_str}) "
            "confirme l'applicabilité de la méthode du séparateur pour cette espèce. "
            "Un total de {n_ind_total} individus distincts a été estimé sur l'ensemble de la période, "
            "soit une moyenne de {ind_moy} individu(s) par nuit de présence. "
            "La nuit la plus active est celle du {pic_date} avec {pic_ind} individu(s) estimé(s). "
            "Ces résultats constituent une estimation minimale conservative (Seebens-Hoyer et al., 2026).\n\n"
            "Référence : Seebens-Hoyer et al. (2026), Biological Conservation, 316, 111741."
        ),
        "report_raw_nonvalide": (
            "{sp}\n\n"
            "Au cours de la période de suivi ({periode_debut} au {periode_fin}, "
            "{n_nuits_total} nuits), l'espèce {sp} a été contactée "
            "{n_contacts_total} fois sur {n_nuits_sp} nuits de présence, "
            "soit en moyenne {contacts_moy} contacts/nuit.\n\n"
            "Indicateur retenu : activité brute (contacts)\n\n"
            "La méthode du séparateur n'a pas été appliquée ({motif_excl}). "
            "La nuit la plus active est celle du {pic_date}."
        ),

        # ── Internal df column names (not translated, used as dict keys) ──────
        "nuit_acoustique": "Nuit acoustique",
        "t_debut": "t_debut",
        "t_fin": "t_fin",
        "intervalle_min": "intervalle_min",

        # ── Legacy keys (kept for compatibility) ──────────────────────────────
        "sidebar_params": "⚙️ Paramètres",
        "step_1": "1 · Import des données",
        "load_demo": "Charger les données de démonstration",
        "demo_loaded": "Données de démonstration chargées.",
        "upload_label": "Importer votre tableur (CSV ou Excel)",
        "step_2": "2 · Mapping des colonnes",
        "format_dt": "Format date/heure",
        "single_col": "Colonne unique (date + heure)",
        "two_cols": "Deux colonnes séparées",
        "col_dt": "Colonne Date/Heure",
        "col_date": "Colonne date",
        "col_time": "Colonne heure",
        "col_sp": "Colonne espèce",
        "step_3": "3 · Séparateur d'individus",
        "interval_label": "Intervalle sans activité (minutes)",
        "step_4": "4 · Filtres (optionnel)",
        "min_contacts": "Contacts minimum par nuit × espèce",
        "run_btn": "Lancer l'analyse",
        "results_header": "📊 Résultats de l'analyse",
        "no_data": "Veuillez charger des données pour commencer.",
        "err_date": "Impossible de lire les dates/heures : ",
        "stat_total_nights": "Nuits de suivi",
        "stat_total_contacts": "Total contacts",
        "stat_indiv_est": "Individus estimés",
        "chart_title": "Activité nocturne & Estimation d'abondance",
        "report_gen": "📝 Synthèse automatique (Rapport)",
        "report_caption": (
            "Ces textes doivent être adaptés au contexte de l'étude avant "
            "intégration dans un rapport réglementaire."
        ),
        "method_note": "Méthode : Seebens-Hoyer et al. (2026)",
        "excl_reason_low": "Activité trop faible",
        "excl_reason_mono": "Distribution unimodale (un seul individu probable)",
        "summary_template": (
            "{sp}\n\nSur la période ({start} au {end}), {n_contacts} séquences acoustiques "
            "ont été enregistrées sur {n_nights} nuits. L'estimation par la méthode du séparateur "
            "suggère un maximum de {n_ind} individus simultanés."
        ),
    },

    "EN": {

        # ── Page / App ────────────────────────────────────────────────────────
        "page_title": "Bat Individual Separator — Acoustic Monitoring",
        "app_title": "🦇 Bat Individual Separator — Acoustic Monitoring",
        "author_credit": "Application designed by Guillaume Marchais",

        # ── Sidebar ───────────────────────────────────────────────────────────
        "sidebar_title": "🦇 Parameters",
        "sidebar_import": "1 · Data Import",
        "sidebar_mapping": "2 · Column Mapping",
        "sidebar_separator": "3 · Individual Separator",
        "sidebar_filters": "4 · Filters (optional)",

        # ── Demo buttons ──────────────────────────────────────────────────────
        "btn_load_demo": "🦇 Load demo dataset",
        "btn_load_demo_help": "Loads a sample dataset (6 species, 210 nights, France 2023).",
        "btn_remove_demo": "✖ Remove demo",
        "info_demo_loaded": "✅ Demo dataset loaded.",
        "or_label": "— or —",

        # ── File uploader ─────────────────────────────────────────────────────
        "file_uploader_label": "Upload your spreadsheet (CSV or Excel)",
        "file_uploader_help": "File must contain at least one date/time column and one species column.",
        "info_upload_prompt": "Upload a file or load the demo to get started.",
        "format_expected": (
            "**Expected format:**\n"
            "| Date | Time | Species |\n"
            "|------|------|---------|\n"
            "| 15/08/2023 | 22:14 | Pipistrellus nathusii |\n"
            "| 15/08/2023 | 22:31 | Nyctalus noctula |\n"
            "| … | … | … |\n\n"
            "Date and Time columns can be merged or separate."
        ),

        # ── Column mapping ────────────────────────────────────────────────────
        "datetime_format": "Date/Time format",
        "dt_mode_single": "Single column (date + time)",
        "dt_mode_double": "Two separate columns",
        "dt_mode_help": "Auto-detected — change if needed.",
        "col_datetime_label": "Date-time column",
        "col_date_label": "Date column",
        "col_time_label": "Time column",
        "col_species_label": "Species column",
        "warning_no_time": (
            "⚠️ Column **{col}** appears to contain only dates without times. "
            "If your data has a separate time column, switch to "
            "**Two separate columns** above."
        ),

        # ── Slider / filters ──────────────────────────────────────────────────
        "slider_label": "Activity-free interval (minutes)",
        "slider_help": "Two bat passes separated by more than N minutes are assigned to distinct individuals.",
        "filter_period_label": "Filter by migratory period",
        "date_range_label": "Period to analyse",
        "date_range_help": "Leave empty = all dates.",
        "min_contacts_label": "Minimum bat passes per night × species",
        "min_contacts_help": "Exclude nights with too few detections for a given species.",
        "warning_diptest": "⚠️ Package `diptest` not installed — Hartigan's Dip test disabled.\n\n`pip install diptest`",

        # ── Data errors / warnings ────────────────────────────────────────────
        "error_datetime": "Unable to parse dates/times: ",
        "warning_no_data": "No data after filtering. Please check the parameters.",

        # ── App header / caption ──────────────────────────────────────────────
        "caption_file": "File",
        "caption_separator": "Separator",
        "caption_method": "Method",

        # ── Summary metrics ───────────────────────────────────────────────────
        "metric_nights": "Nights analysed",
        "metric_contacts": "Total bat passes",
        "metric_individuals": "Estimated individuals",
        "metric_species": "Species",

        # ── Tabs ──────────────────────────────────────────────────────────────
        "tab_data": "📋 Data",
        "tab_distribution": "📊 Interval distribution",
        "tab_estimation": "🦇 Nightly estimation",
        "tab_phenology": "🗓️ Phenological view",
        "tab_export": "💾 Export",
        "tab_report": "📝 Report",

        # ── Column display names ──────────────────────────────────────────────
        "col_datetime_display": "Date-time",
        "col_species_display": "Species",
        "col_night_display": "Acoustic night",
        "col_contacts": "Bat passes",
        "col_nights": "Nights",
        "col_ind_display": "Estimated individuals",
        "col_ratio": "Ind./passes ratio",
        "col_contacts_total": "Bat passes (total)",
        "col_ind_total": "Estimated individuals (total)",
        "col_avg_ind": "Avg ind./night",
        "acoustic_nights": "acoustic nights",

        # ── Tab 1 ─────────────────────────────────────────────────────────────
        "tab1_title": "Imported data overview",
        "tab1_subtitle": "Bat passes per night and species",
        "display_limit": "Display limited to the first 500 rows out of {n:,}.",
        "contacts_by_species": "**Bat passes by species**",
        "time_range_label": "**Temporal range**",
        "species_to_display": "Species to display",

        # ── Tab 2 ─────────────────────────────────────────────────────────────
        "tab2_title": "Distribution of inter-pass intervals",
        "tab2_subtitle": "Bimodality test results by species",
        "species_label": "Species",
        "max_gap_label": "Maximum displayed interval (min)",
        "max_gap_help": "Zoom in on the separator threshold area.",

        "metric_gaps": "Intervals analysed",
        "metric_short": "Short (≤ {sep} min)",
        "metric_short_help": "Intra-individual intervals (same individual likely)",
        "metric_long": "Long (> {sep} min)",
        "metric_long_help": "Inter-individual intervals (new individual likely)",
        "metric_pct_long": "% long",
        "delta_pct_ok": "✓ > 5%",
        "delta_pct_nok": "✗ < 5%",

        "warning_test_na": "⛔ **Test not applicable**: ",
        "metric_bc": "BC (log)",
        "metric_bc_help": "Bimodality Coefficient on log(intervals). BC > 0.555 → bimodal.",
        "delta_bc_ok": "✓ > 0.555",
        "delta_bc_nok": "✗ ≤ 0.555",
        "metric_dip_d": "Dip D (log)",
        "metric_pvalue": "Dip p-value",
        "delta_pvalue_ok": "✓ < 0.05",
        "delta_pvalue_nok": "✗ ≥ 0.05",
        "metric_dip_d_na": "Dip D",
        "metric_dip_d_na_help": "Install `diptest` to enable.",
        "metric_pvalue_na": "p-value",

        "success_bimodal": "{emoji} **Bimodality {lbl}** — {detail} — **{sep}-min** separator validated for *{sp}*.",
        "info_bimodal_probable": "{emoji} **Bimodality {lbl}** — {detail} — divergent test results, interpret with caution.",
        "warning_bimodal_not": "{emoji} **Bimodality {lbl}** — {detail} — raw activity index preferred for this species / period.",
        "caption_test_method": (
            "Tests computed on log₁₊ₓ(intervals) capped at {cap} min "
            "(n={n}). Log transformation compresses the short-interval peak "
            "and makes both modes comparable — recommended for inter-event time distributions."
        ),

        "hist_no_data": "No intervals to display for this species.",
        "hist_same": "≤ {sep} min (same individual)",
        "hist_new": "> {sep} min (new individual)",
        "hist_threshold": "Threshold = {sep} min",
        "xaxis_interval": "Interval (minutes)",
        "yaxis_count": "Number of intervals",
        "caption_hist": (
            "Intervals > {max} min excluded from display "
            "({n} intervals hidden). "
            "Hartigan's test is performed on the complete distribution."
        ),

        "col_n_gaps_raw": "N gaps (raw)",
        "col_n_gaps_test": "N gaps (test)",
        "col_pct_long": "% long",
        "col_bc": "BC (log)",
        "col_dip_d": "Dip D",
        "col_pvalue": "p-value",
        "col_bimodality": "Bimodality",
        "col_sep_valid": "Separator valid",
        "val_yes": "Yes",
        "val_probable": "Probable",
        "val_no": "No",
        "val_na": "N/A",
        "caption_bc_explanation": (
            "BC = Bimodality Coefficient on log₁₊ₓ(capped intervals). "
            "BC > 0.555 → bimodal. Dip test computed on the same log distribution. "
            "Cap = max(4 × separator, 90 min)."
        ),

        # ── Tab 3 ─────────────────────────────────────────────────────────────
        "tab3_title": "Estimated individuals per night and species",
        "tab3_subtitle_ratio": "Individual-to-pass ratio",
        "tab3_subtitle_table": "Summary table",
        "regression_label": "Regression (slope={slope:.2f})",
        "totaux_by_species": "**Totals by species (all nights)**",

        # ── Tab 4 ─────────────────────────────────────────────────────────────
        "tab4_title": "Phenological view — single-night detail",
        "tab4_subtitle_pheno": "Seasonal phenology — estimated individuals",
        "no_contact_info": "No detections for *{sp}* on the night of {night}.",
        "metric_median_gap": "Median interval",
        "individual_label": "Individual {n}",
        "hover_individual": "<b>Individual {n}</b><br>%{{x|%H:%M}}<extra></extra>",
        "xaxis_time": "Time",
        "caption_timeline": (
            "Each vertical bar = 1 bat pass. Colour = estimated individual. "
            "Dashed red line = interval > {sep} min → individual separation."
        ),
        "expander_intervals": "Interval detail for this night",
        "col_from": "From",
        "col_to": "To",
        "col_interval_min": "Interval (min)",
        "col_status": "Status",
        "status_new": "🔴 New individual",
        "status_same": "🟢 Same individual",

        # ── Tab 5 ─────────────────────────────────────────────────────────────
        "tab5_title": "Export results",
        "export_section1": "**1 · Estimated individuals table (night × species)**",
        "export_section2": "**2 · Interval table (all bat passes)**",
        "export_section3": "**3 · Bimodality test results (BC + Dip)**",
        "export_section4": "**4 · Full export (all tables, single file)**",
        "export_section5": "**5 · Analysis parameters (traceability)**",
        "download_excel": "⬇️ Download (Excel)",
        "download_full": "⬇️ Download full report (Excel)",

        "col_new_ind_exp": "New individual",
        "col_prev_contact": "Previous detection",
        "col_next_contact": "Next detection",
        "col_n_gaps_raw_exp": "N gaps raw",
        "col_cap": "Cap (min)",
        "col_bc_ok": "BC > 0.555",
        "col_pvalue_dip": "Dip p-value",

        "param_source": "Source file",
        "param_separator": "Separator (min)",
        "param_col_dt": "Date-time column",
        "param_col_sp": "Species column",
        "param_nights": "Nights analysed",
        "param_species": "Species",
        "param_total_contacts": "Total bat passes",
        "param_total_ind": "Total estimated individuals",
        "param_diptest": "diptest available",
        "param_reference": "Method reference",

        # ── Tab 6 — Report ────────────────────────────────────────────────────
        "tab6_title": "Report — Conclusion text by species",
        "report_intro": (
            "This synthesis text is ready for inclusion in an environmental impact assessment. "
            "It is automatically generated from the analysis results using a **{sep}-min** separator "
            "and the Seebens-Hoyer et al. (2026) method."
        ),
        "copy_button": "📋 Copy plain text",
        "caption_report": (
            "The texts above are automatically generated from analysis parameters. "
            "They must be adapted to the study context (project type, location, "
            "protected species involved) before inclusion in a regulatory document."
        ),

        "motif_insufficient": (
            "due to insufficient sample size "
            "({n} intervals available, minimum 30 required for the bimodality test)"
        ),
        "motif_no_long_mode": (
            "due to the absence of a long-interval mode in the distribution "
            "({pct}% of intervals exceed {sep} min)"
        ),
        "motif_not_confirmed": (
            "the interval distribution does not show "
            "a significant bimodal structure (BC = {bc})"
        ),
        "motif_default": "the conditions for applying the bimodality test are not met",

        "report_valide": (
            "**{sp}**\n\n"
            "Over the monitoring period ({periode_debut} to {periode_fin}, {n_nuits_total} nights), "
            "*{sp}* was detected {n_contacts_total} times across {n_nuits_sp} nights of presence, "
            "averaging {contacts_moy} bat passes per night.\n\n"
            "**Individual estimation (separator method, {sep_min} min)**\n\n"
            "The bimodality test on inter-pass intervals (Bimodality Coefficient, BC = {bc_str}) confirms "
            "the bimodal structure of the distribution: one peak of short intervals (< {sep_min} min, "
            "intra-individual) and a second peak of long intervals (> {sep_min} min, inter-individual). "
            "The separator method is therefore applicable for this species.\n\n"
            "A total of **{n_ind_total} distinct individual occurrences** were estimated over the full period, "
            "averaging **{ind_moy} individual occurrence(s) per night of presence**. "
            "The most active night was {pic_date} with {pic_ind} estimated individual(s).\n\n"
            "⚠️ *Note: the same individual may be detected on successive nights. The total above therefore "
            "represents the cumulative nightly occurrences of distinct individuals within each night, not "
            "necessarily the number of unique individuals across the entire monitoring period.*\n\n"
            "These results represent a conservative minimum estimate (Seebens-Hoyer et al., 2026). "
            "They can be used to assess the potential exposure of the species to wind turbine collision risk "
            "and to calibrate curtailment mitigation measures.\n\n"
            "*Reference: Seebens-Hoyer et al. (2026). Estimating the traffic rates of bats migrating "
            "across the North and Baltic Seas to develop efficient mitigation measures at offshore wind "
            "energy facilities. Biological Conservation, 316, 111741.*"
        ),
        "report_nonvalide": (
            "**{sp}**\n\n"
            "Over the monitoring period ({periode_debut} to {periode_fin}, {n_nuits_total} nights), "
            "*{sp}* was detected {n_contacts_total} times across {n_nuits_sp} nights of presence, "
            "averaging {contacts_moy} bat passes per night.\n\n"
            "**Retained indicator: raw activity (bat passes)**\n\n"
            "The separator method was not applied for this species, because {motif_excl}. "
            "Raw activity is retained as the site occupancy indicator.\n\n"
            "By default, at least **one distinct individual** can be assumed to have been detected "
            "on each night of presence, regardless of the number of bat passes recorded that night. "
            "This represents a minimum of **{n_nuits_sp} individual occurrence(s)** over the full period.\n\n"
            "The most active night was {pic_date}. These activity data characterise species presence "
            "at the study site but do not allow estimation of distinct individuals in transit. "
            "Without individual conversion, collision risk assessment must rely on raw activity indices "
            "and available bibliographic data for the species."
        ),
        "report_raw_valide": (
            "{sp}\n\n"
            "Over the monitoring period ({periode_debut} to {periode_fin}, "
            "{n_nuits_total} nights), {sp} was detected "
            "{n_contacts_total} times across {n_nuits_sp} nights of presence, "
            "averaging {contacts_moy} bat passes per night.\n\n"
            "Individual estimation (separator method, {sep_min} min)\n\n"
            "The bimodality test (BC = {bc_str}) confirms applicability of the separator method "
            "for this species. A total of {n_ind_total} distinct individual occurrences were estimated "
            "over the full period, averaging {ind_moy} individual(s) per night of presence. "
            "The most active night was {pic_date} with {pic_ind} estimated individual(s). "
            "These results represent a conservative minimum estimate (Seebens-Hoyer et al., 2026).\n\n"
            "Reference: Seebens-Hoyer et al. (2026), Biological Conservation, 316, 111741."
        ),
        "report_raw_nonvalide": (
            "{sp}\n\n"
            "Over the monitoring period ({periode_debut} to {periode_fin}, "
            "{n_nuits_total} nights), {sp} was detected "
            "{n_contacts_total} times across {n_nuits_sp} nights of presence, "
            "averaging {contacts_moy} bat passes per night.\n\n"
            "Retained indicator: raw activity (bat passes)\n\n"
            "The separator method was not applied ({motif_excl}). "
            "The most active night was {pic_date}."
        ),

        # ── Internal df column names ──────────────────────────────────────────
        "nuit_acoustique": "Acoustic night",
        "t_debut": "t_debut",
        "t_fin": "t_fin",
        "intervalle_min": "intervalle_min",

        # ── Legacy keys (kept for compatibility) ──────────────────────────────
        "sidebar_params": "⚙️ Settings",
        "step_1": "1 · Data Import",
        "load_demo": "Load demonstration data",
        "demo_loaded": "Demonstration data loaded.",
        "upload_label": "Upload spreadsheet (CSV or Excel)",
        "step_2": "2 · Column Mapping",
        "format_dt": "Date/Time format",
        "single_col": "Single column (date + time)",
        "two_cols": "Two separate columns",
        "col_dt": "Date/Time column",
        "col_date": "Date column",
        "col_time": "Time column",
        "col_sp": "Species column",
        "step_3": "3 · Individual Separator",
        "interval_label": "Activity-free interval (minutes)",
        "step_4": "4 · Filters (optional)",
        "min_contacts": "Minimum bat passes per night × species",
        "run_btn": "Run Analysis",
        "results_header": "📊 Analysis Results",
        "no_data": "Please upload data to begin.",
        "err_date": "Unable to parse dates/times: ",
        "stat_total_nights": "Survey nights",
        "stat_total_contacts": "Total bat passes",
        "stat_indiv_est": "Estimated individuals",
        "chart_title": "Nocturnal Activity & Abundance Proxy",
        "report_gen": "📝 Automated Summary (Report)",
        "report_caption": (
            "This text must be adapted to the study context (EIA, regulatory framework) "
            "before inclusion."
        ),
        "method_note": "Reference: Seebens-Hoyer et al. (2026)",
        "excl_reason_low": "Insufficient activity",
        "excl_reason_mono": "Unimodal distribution (single individual probable)",
        "summary_template": (
            "{sp}\n\nFrom {start} to {end}, {n_contacts} bat passes were recorded "
            "over {n_nights} nights. The individual separator method suggests a maximum "
            "of {n_ind} simultaneous individuals."
        ),
    }
}
