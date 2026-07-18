"""
Prépare les artefacts pour l'appli Streamlit : lit le dataset depuis HDFS (Spark)
et le sauvegarde tel quel dans app/cache/dataset.parquet, pour que app.py
démarre instantanément (pas de JVM/Spark à chaque rerun Streamlit).

A relancer si le dataset HDFS change : python app/prepare_data.py
"""
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

pdf = df.toPandas()
pdf.to_parquet(os.path.join(CACHE_DIR, "dataset.parquet"))
print("dataset.parquet saved:", pdf.shape)

spark.stop()
