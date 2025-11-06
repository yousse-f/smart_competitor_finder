# =====================================================
# ✅ Smart Competitor Finder - Dockerfile (Railway-ready)
# =====================================================
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Copia requirements.txt
COPY requirements.txt .

# Installa librerie di sistema richieste da Playwright e Pandas
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl xvfb chromium \
    libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libxcomposite1 libxrandr2 libxdamage1 libgbm1 libpango-1.0-0 libcairo2 \
    fonts-liberation fonts-dejavu-core libx11-xcb1 libxtst6 libxshmfence1 \
    build-essential gcc g++ gfortran libopenblas-dev liblapack-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installa pip e setuptools aggiornati
RUN pip install --upgrade pip setuptools wheel

# Installa dipendenze scientifiche PRIMA con binary wheels
RUN pip install --no-cache-dir --only-binary :all: \
    numpy==1.26.4 \
    pandas==2.1.4 \
    scikit-learn==1.3.2

# Installa il resto delle dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Installa Chromium per Playwright
RUN playwright install chromium

# Copia il resto del progetto
COPY . .

# Crea la cartella report
RUN mkdir -p reports && chmod 777 reports

# Espone la porta
EXPOSE 8000

# Comando di avvio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
