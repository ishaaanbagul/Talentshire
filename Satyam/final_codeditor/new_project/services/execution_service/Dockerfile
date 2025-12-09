FROM python:3.11-slim

# Install Java (required for PySpark) and SQLite
RUN apt-get update && apt-get install -y \
    default-jdk \
    sqlite3 \
    build-essential

# Set Java home for PySpark
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$PATH:$JAVA_HOME/bin
ENV SPARK_LOCAL_IP=127.0.0.1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
