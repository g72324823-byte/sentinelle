# Flink 2.3 + connecteurs Kafka et Avro / Schema Registry pour Flink SQL.
FROM flink:2.3
# Versions des connecteurs : vérifier la compatibilité avec Flink 2.3 sur
# https://flink.apache.org/downloads/#apache-flink-connectors
ARG KAFKA_CONNECTOR=4.0.1-2.0
ARG FLINK=2.3.0
RUN cd /opt/flink/lib && \
    curl -fsSLO https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/${KAFKA_CONNECTOR}/flink-sql-connector-kafka-${KAFKA_CONNECTOR}.jar && \
    curl -fsSLO https://repo1.maven.org/maven2/org/apache/flink/flink-sql-avro-confluent-registry/${FLINK}/flink-sql-avro-confluent-registry-${FLINK}.jar && \
    mkdir -p /opt/flink/plugins/s3-fs-presto && cp /opt/flink/opt/flink-s3-fs-presto-*.jar /opt/flink/plugins/s3-fs-presto/
