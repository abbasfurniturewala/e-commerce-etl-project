FROM apache/airflow:3.2.2

USER root

COPY pyproject.toml /opt/ecommerce/pyproject.toml
COPY src /opt/ecommerce/src

RUN chown -R airflow:root /opt/ecommerce

USER airflow
RUN pip install --no-cache-dir '/opt/ecommerce[warehouse]'
