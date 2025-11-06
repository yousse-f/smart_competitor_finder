🧭 FASE 1 — Definizione del Prodotto e MVP
🎯 Obiettivo della Fase 1

Costruire la prima versione funzionante (MVP) di “Smart Competitor Finder”, in grado di:

ricevere il sito del cliente,

estrarre automaticamente prodotti/servizi (keyword),

permettere la selezione delle parole chiave,

analizzare un file Excel di siti,

restituire un report con i competitor realmente pertinenti.

🔹 STEP 1.1 — Architettura generale
⚙️ Stack Tecnologico
Componente	Tecnologia	Note
Frontend	Next.js 14 + Tailwind CSS	UI moderna, veloce, facilmente integrabile con API
Backend	FastAPI (Python 3.11+)	API REST, gestione scraping, orchestrazione
Scraping Engine	Playwright + BeautifulSoup + asyncio	Analisi massiva, compatibile con JavaScript pages
Database	PostgreSQL + SQLAlchemy	Caching siti analizzati, log richieste
Report	Pandas + OpenPyXL	Generazione Excel automatico
AI Layer (Fase 2)	OpenAI Embeddings / LangChain	Analisi semantica competitor
🔹 STEP 1.2 — Flusso Utente

Input:
L’utente inserisce l’URL del sito cliente.

Scraping #1:
Il backend analizza il sito, estrae titoli, heading, meta tag, testo principale e genera una lista di parole chiave rappresentative (servizi/prodotti).

Interfaccia Keyword Selection:
Sul frontend appare la lista; il consulente seleziona le keyword da cercare nei competitor.

Upload Excel:
L’utente carica un file .xlsx con le colonne Nome azienda, URL, e opzionalmente Codice ATECO.

Scraping #2 (Bulk):
Il backend processa tutti i siti in modo asincrono, cercando nei contenuti la presenza delle keyword selezionate.

Output:
Il sistema genera un report Excel con:

URL sito

Match score (%)

Keyword trovate

Numero di occorrenze

Screenshot (facoltativo, Playwright)

Download / Dashboard:
L’utente scarica il file o visualizza i risultati in una tabella web interattiva.

🔹 STEP 1.3 — Roadmap di sviluppo MVP
Fase	Attività	Deliverable
1. Analisi & Design	- Definizione requisiti funzionali
- Schema DB
- Mockup UI	Documentazione tecnica
2. Setup Backend	- Configurazione FastAPI
- Endpoint: /analyze-site, /analyze-bulk, /generate-report	API funzionante
3. Modulo Scraping Base	- Funzione extract_keywords(url)
- Funzione search_keywords_in_sites(file, keywords)	Motore scraping
4. Frontend UI (MVP)	- Pagina input URL
- Lista keyword cliccabili
- Upload Excel + progress bar	Interfaccia web pronta
5. Generazione Report	- Elaborazione dati → Excel
- Ordinamento per match score	File .xlsx
6. Testing & Demo	- Test 100 siti
- Ottimizzazione velocità	MVP presentabile
7. Deploy Demo	- Docker Compose (Backend + Frontend)	Demo online
🔹 STEP 1.4 — Struttura API
Endpoint	Metodo	Descrizione
/api/analyze-site	POST	Riceve l’URL, restituisce lista keyword
/api/upload-file	POST	Riceve Excel con siti
/api/analyze-bulk	POST	Avvia scraping massivo
/api/report	GET	Restituisce file Excel finale
🔹 STEP 1.5 — Output Esempio (Report Excel)
URL Competitor	Match Score (%)	Keyword Trovate	Screenshot
www.ventilacasa.it
	96 %	ventola residenziale, aspiratore bagno	✅
www.ventolemarine.it
	5 %	—	❌
www.climahome.it
	88 %	ventilazione casa, ricambio aria	✅
🔹 STEP 1.6 — Miglioramenti Previsti (Fase 2 / Fase 3)
Modulo	Descrizione
🔍 AI Semantic Filter	Classificazione “rilevante/non rilevante” con embeddings e cosine similarity
📊 Dashboard Interattiva	Grafici su affinità, clusterizzazione dei competitor
☁️ Cloud Scaling	Parallelizzazione scraping con Celery + Redis
🔐 User Auth / Teams	Multi-utente con login aziendale
📈 API per CRM	Integrazione con gestionali esistenti (import/export dati)