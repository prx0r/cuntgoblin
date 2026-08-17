FROM python:3.11-slim

WORKDIR /opt/mcptruth

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests
COPY data ./data
COPY scripts ./scripts

ENV MCPTRUTH_DB=/opt/mcptruth/data/mcptruth.db
ENV MCPTRUTH_PORT=8000

EXPOSE 8000

# Seed registry at container start, then serve.
CMD ["sh", "-c", "python -m app.runner seed && python -m app.api"]