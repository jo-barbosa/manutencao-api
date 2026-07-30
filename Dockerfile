# ==========================================
# Dockerfile Produção - Consola de Manutenção
# ==========================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências de sistema para PostgreSQL (psycopg2) e curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código-fonte
COPY . .

# Expor as portas do FastAPI (8000) e Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Comando padrão de execução (override no docker-compose se necessário)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
