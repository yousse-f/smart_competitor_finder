# ======================================================
# ✅ Dockerfile ottimizzato per Railway + Playwright + FastAPI
# ======================================================

FROM python:3.11-slim

# Installa dipendenze di sistema necessarie per Playwright e Chromium
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl xvfb \
    libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libxcomposite1 libxrandr2 libxdamage1 libgbm1 libpango-1.0-0 libcairo2 \
    fonts-liberation libappindicator3-1 libx11-xcb1 libxtst6 libxshmfence1 \
    chromium && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installa Playwright e dipendenze Python
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Installa i browser necessari (Chromium headless)
RUN playwright install --with-deps chromium

# Copia tutto il codice sorgente
COPY . .

# Crea directory reports con permessi corretti
RUN mkdir -p reports && chmod 777 reports

# Imposta l'ambiente
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Esegui FastAPI tramite Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
