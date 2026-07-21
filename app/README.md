# App Dataviz (Streamlit)

Version minimale : accès au dataset complet + quelques stats et chiffres
simples, quasi directement observables sur le CSV. Pas de couleurs
personnalisées, pas de graphique complexe — les défauts de Streamlit.

## Installation (la plus simple possible)

Depuis la racine du repo :

```bash
pip install -r app/requirements.txt
streamlit run app/app.py
```

Ça ouvre l'appli sur http://localhost:8501. **Pas besoin de Hadoop, Spark ou Java
pour lancer l'appli** : elle lit un fichier déjà préparé dans `app/cache/`
(commité dans le repo), pas la donnée brute.

## Comment ça s'articule avec le reste du projet

```
1) PRÉPARATION (une seule fois, à refaire seulement si le dataset change)
   HDFS → Spark (PySpark) → Pandas
   ─────────────────────────────────────────────────────────────────────────
   app/prepare_data.py

2) AFFICHAGE (à chaque lancement de l'appli, instantané)
   app/cache/dataset.parquet  →  Streamlit
   ─────────────────────────────────────────────────────────────────────────
   app/app.py
```

**`app/prepare_data.py`** se connecte à HDFS (`hdfs://localhost:9000/projet/donnees/...`)
via PySpark, lit le CSV nettoyé tel quel (pas d'encodage, pas de transformation),
et sauvegarde le dataframe pandas dans `app/cache/dataset.parquet`.

**`app/app.py`** ne touche jamais à Spark/HDFS au démarrage : il charge
uniquement `app/cache/dataset.parquet` (via `st.cache_data`, chargé une seule fois).

## Si le dataset HDFS change

```bash
python app/prepare_data.py
```

Ça demande Hadoop/HDFS lancé + Java + Spark. Ça réécrit `app/cache/dataset.parquet`
— à recommiter ensuite.

## Structure

```
app/
├── app.py             # l'appli Streamlit
├── prepare_data.py    # génère app/cache/dataset.parquet depuis HDFS
├── requirements.txt   # dépendances Python de l'appli uniquement
├── cache/             # dataset.parquet (commité, pas de .gitignore dessus)
└── README.md          # ce fichier
```

## Détail de l'appli (`app.py`)

- Nombre total d'élèves (affiché clairement en haut — c'est bien tout le
  dataset, 6 378 lignes, pas juste les 50 premières affichées dans le tableau).
- Table complète du dataset (aperçu scrollable).
- Statistiques descriptives (moyenne, écart-type, min, max) sur les variables numériques.
- Quelques chiffres simples : meilleur score, pire score, total d'heures
  étudiées (tous élèves confondus), élève qui a le plus étudié.
- Distribution du score d'examen (graphique natif Streamlit).

## Prochaine étape

Un script Python de stats descriptives (fait par un camarade) sera branché à
cette appli plus tard. Rien à faire pour l'instant de ce côté.
