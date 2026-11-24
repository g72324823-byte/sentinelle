"""J1 — Chargement de l'historique dans le lakehouse Iceberg (À COMPLÉTER).

À lancer dans le conteneur spark :  spark-submit j1_bronze_argent.py
Le catalogue « lake » (Iceberg REST + MinIO) est configuré dans spark-defaults.conf.
"""
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("sentinelle-j1").getOrCreate()
spark.sql("CREATE NAMESPACE IF NOT EXISTS lake.bronze")
spark.sql("CREATE NAMESPACE IF NOT EXISTS lake.argent")

# Bronze : les fichiers bruts, tels quels, plus la date d'ingestion
brut = (spark.read.parquet("/data/historique/")
        .withColumn("_ingere_le", F.current_timestamp())
        .withColumn("_fichier", F.input_file_name()))
brut.writeTo("lake.bronze.transactions").createOrReplace()

# Argent : TODO
#  1. typer et nettoyer (montant > 0, type dans la liste connue, dédoublonnage sur tx_id)
#  2. partitionner par jour : PARTITIONED BY (days(ts))
#  3. joindre le référentiel des comptes (segment, kyc_niveau) — broadcast ou non ? justifiez
#  4. vérifier le plan avec .explain() et le noter dans le dossier d'architecture
# Bonus : time travel (VERSION AS OF), évolution de schéma (ajout d'une colonne)

print(spark.table("lake.bronze.transactions").count(), "lignes en bronze")
