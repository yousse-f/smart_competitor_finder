# ======================================================
# ✅ Dockerfile ottimizzato con cache layers per Railway
# ======================================================

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Copia solo requirements per sfruttare la cache Docker
COPY requirements.txt .

# Installa solo le dipendenze base di sistema
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl xvfb chromium \
    libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libxcomposite1 libxrandr2 libxdamage1 libgbm1 libpango-1.0-0 libcairo2 \
    fonts-liberation fonts-dejavu-core libx11-xcb1 libxtst6 libxshmfence1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installa solo i pacchetti Python (usa cache Docker)
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

# Installa solo Chromium (senza --with-deps per velocità)
RUN playwright install chromium

# Copia il resto del codice (questo layer cambia spesso, ma è veloce)
COPY . .

# Crea cartella reports
RUN mkdir -p reports && chmod 777 reports

# Variabili d'ambiente
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Esegui FastAPI tramite Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
