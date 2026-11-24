# Spark 4 + PySpark + Jupyter, avec les bibliothèques Iceberg et S3 pré-téléchargées.
FROM spark:4.2.0-python3
USER root
RUN pip install --no-cache-dir jupyterlab pyiceberg[s3fs] duckdb pandas pyarrow
# Versions à aligner sur votre Spark : vérifier sur https://iceberg.apache.org/releases/
ARG ICEBERG=1.10.1
ARG SCALA=2.13
RUN cd /opt/spark/jars && \
    curl -fsSLO https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.0_${SCALA}/${ICEBERG}/iceberg-spark-runtime-4.0_${SCALA}-${ICEBERG}.jar && \
    curl -fsSLO https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG}/iceberg-aws-bundle-${ICEBERG}.jar
COPY spark-defaults.conf /opt/spark/conf/spark-defaults.conf
USER spark
WORKDIR /opt/sentinelle/spark
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--IdentityProvider.token=", "--ServerApp.root_dir=/opt/sentinelle"]
