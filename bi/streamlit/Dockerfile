FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir streamlit~=1.67 psycopg[binary] confluent-kafka requests pandas
COPY app.py .
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
