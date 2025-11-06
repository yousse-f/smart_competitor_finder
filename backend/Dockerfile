# =====================================================
# ✅ Smart Competitor Finder - Dockerfile (Backend Directory)
# =====================================================
# Questo Dockerfile è in /backend per essere rilevato da Railway
# con Root Directory = /backend

FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

# WORKDIR di base
WORKDIR /app

# Copia requirements.txt (ora nella stessa directory del Dockerfile)
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

# ⚠️ STEP CRITICO: Installa numpy, pandas, scikit-learn SEPARATAMENTE
# Questo forza la compilazione contro Python 3.12 headers (non 3.13 di Railway)
# Li installiamo PRIMA di requirements.txt per isolarli dalla catena di dipendenze
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    pandas==2.1.4 \
    scikit-learn==1.3.2

# Installa il resto delle dipendenze da requirements.txt
# pip salterà automaticamente numpy, pandas, scikit-learn (già installati)
RUN pip install --no-cache-dir -r requirements.txt

# 🆕 NUOVO STEP: Scarica i dati NLTK durante la build
# Questo previene il crash dovuto al download durante l'avvio del container
RUN python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords')"

# Installa Chromium per Playwright
RUN playwright install chromium

# Copia tutto il contenuto della cartella corrente (backend/)
COPY . .

# Crea la cartella reports
RUN mkdir -p reports && chmod 777 reports

# Espone la porta
EXPOSE 8000

# Comando di avvio (main.py è in /app/backend)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]