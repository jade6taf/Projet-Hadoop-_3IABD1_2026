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

import pyarrow.compute as pc
import pyarrow.csv as pa_csv
import streamlit as st

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "Code", "figures")

st.set_page_config(page_title="Facteurs de reussite scolaire", layout="wide")


@st.cache_data
def load_data():
    return pa_csv.read_csv(os.path.join(CACHE_DIR, "dataset.csv"))


table = load_data()

st.title("Facteurs de reussite scolaire")

tab_donnees, tab_figures, tab_ml = st.tabs(["Donnees", "Figures", "ML"])

with tab_donnees:
    st.metric("Nombre total d'eleves dans le dataset", table.num_rows)

    st.header("Acces au dataset")
    st.write(f"Table complete : {table.num_rows} lignes, {table.num_columns} colonnes.")
    st.dataframe(table, use_container_width=True, height=400)

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
    st.dataframe(stats_rows, use_container_width=True)

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
        st.dataframe([best], use_container_width=True)
    with col2:
        st.subheader("Pire score")
        st.metric("Score", f"{worst['Score_Examen']} / 100")
        st.dataframe([worst], use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Total d'heures etudiees (tous eleves confondus)")
        st.metric("Heures", f"{total_hours:,}".replace(",", " "))
    with col4:
        st.subheader("Eleve qui a le plus etudie")
        st.metric("Heures / semaine", f"{most_hours['Heures_Etudiees']}")
        st.dataframe([most_hours], use_container_width=True)

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
        st.dataframe(samuel_numeriques, use_container_width=True)

    if samuel_quartiles is not None:
        st.subheader("Quartiles")
        st.dataframe(samuel_quartiles, use_container_width=True)

    if samuel_frequences is not None:
        st.subheader("Variables categorielles")
        st.dataframe(samuel_frequences, use_container_width=True)

    if samuel_numeriques is None and samuel_quartiles is None and samuel_frequences is None:
        st.info("Les stats de Samuel n'ont pas encore ete generees (relancer Code/analyse.ipynb).")

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

with tab_ml:
    pass
