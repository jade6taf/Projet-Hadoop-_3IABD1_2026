"""
Appli Streamlit — Facteurs de reussite scolaire
Version minimale : acces au dataset + quelques stats et chiffres simples.
Couleurs par defaut de Streamlit, rien de personnalise.

Lancer : streamlit run app/app.py
Necessite que app/prepare_data.py ait deja ete execute au moins une fois
(genere app/cache/dataset.parquet).
"""
import os

import pandas as pd
import streamlit as st

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

st.set_page_config(page_title="Facteurs de reussite scolaire", layout="wide")


@st.cache_data
def load_data():
    return pd.read_parquet(os.path.join(CACHE_DIR, "dataset.parquet"))


df = load_data()

st.title("Facteurs de reussite scolaire")

st.metric("Nombre total d'eleves dans le dataset", len(df))

st.header("Acces au dataset")
st.write(f"Table complete : {len(df)} lignes, {len(df.columns)} colonnes.")
st.dataframe(df, use_container_width=True, height=400)

st.header("Statistiques descriptives")
numeric_cols = ["Heures_Etudiees", "Presence", "Heures_Sommeil", "Scores_Precedents", "Sessions_Tutorat", "Score_Examen"]
st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)

st.header("Quelques chiffres")

best = df.loc[df["Score_Examen"].idxmax()]
worst = df.loc[df["Score_Examen"].idxmin()]
most_hours = df.loc[df["Heures_Etudiees"].idxmax()]
total_hours = int(df["Heures_Etudiees"].sum())

col1, col2 = st.columns(2)
with col1:
    st.subheader("Meilleur score")
    st.metric("Score", f"{best['Score_Examen']} / 100")
    st.dataframe(best.to_frame().T, use_container_width=True)
with col2:
    st.subheader("Pire score")
    st.metric("Score", f"{worst['Score_Examen']} / 100")
    st.dataframe(worst.to_frame().T, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Total d'heures etudiees (tous eleves confondus)")
    st.metric("Heures", f"{total_hours:,}".replace(",", " "))
with col4:
    st.subheader("Eleve qui a le plus etudie")
    st.metric("Heures / semaine", f"{most_hours['Heures_Etudiees']}")
    st.dataframe(most_hours.to_frame().T, use_container_width=True)

st.header("Distribution du score d'examen")
st.bar_chart(df["Score_Examen"].value_counts().sort_index())
