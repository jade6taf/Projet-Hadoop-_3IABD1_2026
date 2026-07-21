"""
Appli Streamlit — Facteurs de reussite scolaire
Version minimale : acces au dataset + quelques stats et chiffres simples.
Pas de pandas (consigne du prof) : lecture et calculs via PyArrow.
Couleurs par defaut de Streamlit, rien de personnalise.

Lancer : streamlit run app/app.py
Necessite que app/prepare_data.py ait deja ete execute au moins une fois
(genere app/cache/dataset.csv).
"""
import os

import numpy as np
import pyarrow.compute as pc
import pyarrow.csv as pa_csv
import streamlit as st

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "Code", "figures")

# Meme encodage que Code/analyse.ipynb, pour la matrice de correlation.
CATEGORY_ENCODINGS = {
    "Implication_Parentale": {"Bas": 0, "Moyen": 1, "Haut": 2},
    "Acces_aux_Ressources": {"Bas": 0, "Moyen": 1, "Haut": 2},
    "Niveau_Motivation": {"Bas": 0, "Moyen": 1, "Haut": 2},
    "Qualite_Enseignant": {"Bas": 0, "Moyen": 1, "Haut": 2},
    "Revenu_Famille": {"Bas": 0, "Moyen": 1, "Haut": 2},
    "Distance_Maison": {"Proche": 0, "Moderee": 1, "Loin": 2},
    "Niveau_Education_Parents": {"Lycee": 0, "Licence": 1, "Master": 2},
    "Influence_Entourage": {"Negative": -1, "Neutre": 0, "Positif": 1},
    "Activites_Extrascolaires": {"Non": 0, "Oui": 1},
    "Troubles_Apprentissage": {"Non": 0, "Oui": 1},
    "Acces_Internet": {"Non": 0, "Oui": 1},
    "Type_Ecole": {"Publique": 0, "Privee": 1},
    "Genre": {"Homme": 0, "Femme": 1},
}

st.set_page_config(page_title="Facteurs de reussite scolaire", layout="wide")


@st.cache_data
def load_data():
    return pa_csv.read_csv(os.path.join(CACHE_DIR, "dataset.csv"))


table = load_data()

st.title("Facteurs de reussite scolaire")

tab_donnees, tab_figures, tab_visualisation = st.tabs(["Donnees", "Graphiques", "Visualisation de donnees"])

#############################################################################

with tab_donnees:
    st.metric("Nombre total d'eleves dans le dataset", table.num_rows)

    st.header("Acces au dataset")
    st.write(f"Table complete : {table.num_rows} lignes, {table.num_columns} colonnes.")
    st.dataframe(table, width='stretch', height=400)

    st.header("Statistiques descriptives")
    numeric_cols = ["Heures_Etudiees", "Presence", "Heures_Sommeil", "Scores_Precedents", "Sessions_Tutorat", "Score_Examen"]
    stats_rows = []
    for col_name in numeric_cols:
        col = table.column(col_name)
        stats_rows.append({
            "Variable": col_name,
            "Moyenne": round(pc.mean(col).as_py(), 2),
            "Ecart-type": round(pc.stddev(col).as_py(), 2),
            "Min": pc.min(col).as_py(),
            "Max": pc.max(col).as_py(),
        })
    st.dataframe(stats_rows, width='stretch')

    st.header("Quelques chiffres")

    def top_row(by_column, ascending=False):
        order = "ascending" if ascending else "descending"
        return table.sort_by([(by_column, order)]).slice(0, 1).to_pylist()[0]

    best = top_row("Score_Examen")
    worst = top_row("Score_Examen", ascending=True)
    most_hours = top_row("Heures_Etudiees")
    total_hours = pc.sum(table.column("Heures_Etudiees")).as_py()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Meilleur score")
        st.metric("Score", f"{best['Score_Examen']} / 100")
        st.dataframe([best], width='stretch')
    with col2:
        st.subheader("Pire score")
        st.metric("Score", f"{worst['Score_Examen']} / 100")
        st.dataframe([worst], width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Total d'heures etudiees (tous eleves confondus)")
        st.metric("Heures", f"{total_hours:,}".replace(",", " "))
    with col4:
        st.subheader("Eleve qui a le plus etudie")
        st.metric("Heures / semaine", f"{most_hours['Heures_Etudiees']}")
        st.dataframe([most_hours], width='stretch')

    st.header("Distribution du score d'examen")
    value_counts = [item.as_py() for item in pc.value_counts(table.column("Score_Examen"))]
    dist_rows = sorted(
        ({"Score_Examen": v["values"], "Nombre d'eleves": v["counts"]} for v in value_counts),
        key=lambda r: r["Score_Examen"],
    )
    st.bar_chart(dist_rows, x="Score_Examen", y="Nombre d'eleves")

    st.header("Statistiques detaillees")

    def read_csv_if_exists(filename):
        path = os.path.join(CACHE_DIR, filename)
        return pa_csv.read_csv(path) if os.path.exists(path) else None

    samuel_numeriques = read_csv_if_exists("samuel_stats_numeriques.csv")
    samuel_quartiles = read_csv_if_exists("samuel_quartiles.csv")
    samuel_frequences = read_csv_if_exists("samuel_frequences.csv")

    if samuel_numeriques is not None:
        st.subheader("Variables numeriques")
        st.dataframe(samuel_numeriques, width='stretch')

    if samuel_quartiles is not None:
        st.subheader("Quartiles")
        st.dataframe(samuel_quartiles, width='stretch')

    if samuel_frequences is not None:
        st.subheader("Variables categorielles")
        st.dataframe(samuel_frequences, width='stretch')

    if samuel_numeriques is None and samuel_quartiles is None and samuel_frequences is None:
        st.info("Les stats de Samuel n'ont pas encore ete generees (relancer Code/analyse.ipynb).")

#############################################################################

with tab_figures:
    figures = [
        ("01_distribution_score.png", "Distribution du score d'examen"),
        ("02_matrice_correlation.png", "Matrice de correlation"),
        ("03_top_correlations.png", "Correlation de chaque variable avec le score"),
        ("04_scatter_presence.png", "Presence vs score d'examen"),
        ("05_scatter_heures_etudiees.png", "Heures etudiees vs score d'examen"),
        ("06_box_motivation.png", "Score selon le niveau de motivation"),
        ("07_box_ressources.png", "Score selon l'acces aux ressources"),
        ("08_box_type_ecole.png", "Score : ecole publique vs privee"),
    ]

    any_found = False
    for filename, caption in figures:
        path = os.path.join(FIGURES_DIR, filename)
        if os.path.exists(path):
            any_found = True
            st.image(path, caption=caption, width=500)

    if not any_found:
        st.info("Aucune figure trouvee dans Code/figures (relancer Code/dataviz.ipynb).")

#############################################################################

with tab_visualisation:
    st.caption("Les memes graphes que dans \"Graphiques\", mais en version interactive (zoom, survol, tooltip).")

    numeric_cols_no_score = ["Heures_Etudiees", "Presence", "Heures_Sommeil", "Scores_Precedents", "Sessions_Tutorat"]
    categorical_cols = list(CATEGORY_ENCODINGS.keys())
    score_arr = table.column("Score_Examen").to_numpy(zero_copy_only=False).astype(float)

    st.header("1. Distribution du score d'examen")
    value_counts = [item.as_py() for item in pc.value_counts(table.column("Score_Examen"))]
    dist_rows = sorted(
        ({"Score_Examen": v["values"], "Nombre d'eleves": v["counts"]} for v in value_counts),
        key=lambda r: r["Score_Examen"],
    )
    st.vega_lite_chart({
        "data": {"values": dist_rows},
        "mark": "bar",
        "height": 350,
        "encoding": {
            "x": {"field": "Score_Examen", "type": "ordinal"},
            "y": {"field": "Nombre d'eleves", "type": "quantitative"},
        },
    }, width="stretch", key="viz_distribution_v2")

    st.header("2. Matrice de correlation")
    valeurs_par_variable = {c: table.column(c).to_numpy(zero_copy_only=False).astype(float) for c in numeric_cols_no_score}
    for col_name, mapping in CATEGORY_ENCODINGS.items():
        valeurs_par_variable[col_name] = np.array([mapping.get(v) for v in table.column(col_name).to_pylist()], dtype=float)
    valeurs_par_variable["Score_Examen"] = score_arr

    variables_matrice = numeric_cols_no_score + categorical_cols + ["Score_Examen"]
    matrice = np.array([valeurs_par_variable[v] for v in variables_matrice])
    corr_matrix = np.corrcoef(matrice)

    heatmap_rows = [
        {"Variable 1": v1, "Variable 2": v2, "Correlation": round(float(corr_matrix[i, j]), 3)}
        for i, v1 in enumerate(variables_matrice)
        for j, v2 in enumerate(variables_matrice)
    ]
    st.vega_lite_chart({
        "data": {"values": heatmap_rows},
        "mark": "rect",
        "height": 500,
        "encoding": {
            "x": {"field": "Variable 1", "type": "nominal"},
            "y": {"field": "Variable 2", "type": "nominal"},
            "color": {"field": "Correlation", "type": "quantitative", "scale": {"scheme": "redblue", "domain": [-1, 1]}},
            "tooltip": [{"field": "Variable 1"}, {"field": "Variable 2"}, {"field": "Correlation"}],
        },
    }, width="stretch", key="viz_heatmap")

    st.header("3. Correlation de chaque variable avec le score")
    toutes_correlations = sorted(
        (
            {"Variable": v, "Correlation": round(float(np.corrcoef(valeurs_par_variable[v], score_arr)[0, 1]), 3)}
            for v in variables_matrice if v != "Score_Examen"
        ),
        key=lambda r: abs(r["Correlation"]), reverse=True,
    )
    st.bar_chart(toutes_correlations, x="Variable", y="Correlation")

    st.header("4. Presence vs score d'examen")
    st.vega_lite_chart({
        "data": {"values": table.select(["Presence", "Score_Examen"]).to_pylist()},
        "layer": [
            {"mark": {"type": "point", "opacity": 0.25}},
            {"mark": {"type": "line", "color": "red"}, "transform": [{"regression": "Score_Examen", "on": "Presence"}]},
        ],
        "encoding": {
            "x": {"field": "Presence", "type": "quantitative"},
            "y": {"field": "Score_Examen", "type": "quantitative"},
        },
        "height": 350,
    }, width="stretch", key="viz_scatter_presence")

    st.header("5. Heures etudiees vs score d'examen")
    st.vega_lite_chart({
        "data": {"values": table.select(["Heures_Etudiees", "Score_Examen"]).to_pylist()},
        "layer": [
            {"mark": {"type": "point", "opacity": 0.25}},
            {"mark": {"type": "line", "color": "red"}, "transform": [{"regression": "Score_Examen", "on": "Heures_Etudiees"}]},
        ],
        "encoding": {
            "x": {"field": "Heures_Etudiees", "type": "quantitative"},
            "y": {"field": "Score_Examen", "type": "quantitative"},
        },
        "height": 350,
    }, width="stretch", key="viz_scatter_heures")

    st.header("6. Score selon le niveau de motivation")
    st.vega_lite_chart({
        "data": {"values": table.select(["Niveau_Motivation", "Score_Examen"]).to_pylist()},
        "mark": "boxplot",
        "encoding": {
            "x": {"field": "Niveau_Motivation", "type": "nominal", "sort": ["Bas", "Moyen", "Haut"]},
            "y": {"field": "Score_Examen", "type": "quantitative"},
        },
        "height": 350,
    }, width="stretch", key="viz_box_motivation")

    st.header("7. Score selon l'acces aux ressources")
    st.vega_lite_chart({
        "data": {"values": table.select(["Acces_aux_Ressources", "Score_Examen"]).to_pylist()},
        "mark": "boxplot",
        "encoding": {
            "x": {"field": "Acces_aux_Ressources", "type": "nominal", "sort": ["Bas", "Moyen", "Haut"]},
            "y": {"field": "Score_Examen", "type": "quantitative"},
        },
        "height": 350,
    }, width="stretch", key="viz_box_ressources")

    st.header("8. Score : ecole publique vs privee")
    st.vega_lite_chart({
        "data": {"values": table.select(["Type_Ecole", "Score_Examen"]).to_pylist()},
        "mark": "boxplot",
        "encoding": {
            "x": {"field": "Type_Ecole", "type": "nominal", "sort": ["Publique", "Privee"]},
            "y": {"field": "Score_Examen", "type": "quantitative"},
        },
        "height": 350,
    }, width="stretch", key="viz_box_type_ecole")
