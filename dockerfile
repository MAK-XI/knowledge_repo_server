FROM postgres:16.11-alpine
ENV POSTGRES_DB=knowledge_repo
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=1234
WORKDIR /app
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install --no-cache-dir -r requirements.txt
