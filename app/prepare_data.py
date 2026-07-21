"""
Prepare les artefacts pour l'appli Streamlit : lit le dataset depuis HDFS (Spark)
et le sauvegarde en CSV, sans pandas (consigne du prof : pas de toPandas / pandas).

Spark calcule et .collect() les lignes (action Spark native), puis l'ecriture du
fichier se fait en Python pur (module csv standard) plutot que via
df.write.csv(...), pour eviter le besoin de winutils.exe sur Windows (Spark ne
peut pas ecrire sur le systeme de fichiers local sans lui, mais collect() + une
ecriture Python classique n'en ont pas besoin).

A relancer si le dataset HDFS change : python app/prepare_data.py
"""
import csv
import os

os.environ.setdefault("PYSPARK_SUBMIT_ARGS", "--conf spark.hadoop.dfs.client.use.datanode.hostname=true pyspark-shell")

from pyspark.sql import SparkSession

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

port = "9000"
spark = SparkSession.builder.appName("streamlit_prepare_data").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
df = spark.read.csv(f"hdfs://localhost:{port}/projet/donnees/StudentPerformanceFactors_propre.csv", header=True, inferSchema=True)
df = df.dropDuplicates()

columns = df.columns
rows = df.collect()  # action Spark native (pas pandas)

out_path = os.path.join(CACHE_DIR, "dataset.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row[c] for c in columns])

print(f"dataset.csv sauvegarde : {len(rows)} lignes, {len(columns)} colonnes")
spark.stop()
