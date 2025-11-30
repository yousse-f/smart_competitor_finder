# PRD: Timeout e Batch Processing Improvements

**Data Creazione**: 30 novembre 2025  
**Priorità**: CRITICA (Production Bug Fix)  
**Issue di Riferimento**: Analisi bloccata al 14% su Railway (analysis_id: 20251124_094234)

---

## 🎯 Obiettivi

### Problema Principale
Analisi di 91 siti si è bloccata su site #48 (euroventilatori-int.com) per 7 ore senza timeout, causando:
- Cliente non può vedere risultati parziali (43 siti completati con successo)
- Nessuna visibilità su 4 siti completamente falliti
- SSE stream frozen, frontend continua a fare polling inutilmente

### Risultati Attesi
1. **Zero hang infiniti**: Ogni sito ha max 60s per completare
2. **Trasparenza totale**: Cliente vede quali siti sono falliti e perché
3. **Scalabilità 500+ siti**: Batch automatico per dataset grandi
4. **UX migliorata**: Progress bar mostra batch corrente

---

## 📋 FASE 1 - Quick Wins (20 minuti)

### ✅ Task 1.1: Timeout Assoluto per Singolo Sito
**File**: `backend/api/analyze_stream.py`  
**Tempo Stimato**: 5 minuti

**Implementazione**:
```python
# Riga ~55, dentro il loop for url in urls:
try:
    async with asyncio.timeout(60):  # ⏱️ Max 60s per sito
        result = await hybrid_scraper_v2.scrape_intelligent(url, ...)
        # ... existing code ...
except asyncio.TimeoutError:
    logger.error(f"⏱️ TIMEOUT (60s) for {url}")
    failed_sites.append({
        'url': url,
        'error': 'Timeout dopo 60 secondi',
        'suggestion': 'Sito troppo lento o bloccato'
    })
    # Send SSE event
    await send_sse_event({
        'event': 'site_failed',
        'data': {'url': url, 'reason': 'timeout_60s'}
    })
    continue  # Skip to next site
```

**Test Case**:
- URL: `https://euroventilatori-int.com` (il sito che ha causato il freeze)
- Expected: Timeout dopo 60s, analysis continua con sito successivo
- Log Expected: `⏱️ TIMEOUT (60s) for https://euroventilatori-int.com`

**Success Criteria**:
- ✅ Nessun sito può bloccare per più di 60s
- ✅ Analisi continua anche dopo timeout
- ✅ Frontend riceve evento SSE "site_failed"

---

### ✅ Task 1.2: Tracking Siti Falliti
**File**: `backend/api/analyze_stream.py`  
**Tempo Stimato**: 5 minuti

**Implementazione**:
```python
# Riga ~30, all'inizio della funzione analyze_urls_stream:
failed_sites = []  # Track per Excel report

# Dentro il loop, cattura tutti i fallimenti:
except Exception as e:
    logger.error(f"❌ ERROR processing {url}: {str(e)}")
    failed_sites.append({
        'url': url,
        'error': str(e)[:100],  # Primi 100 caratteri
        'suggestion': _get_error_suggestion(str(e))
    })
```

**Helper Function**:
```python
def _get_error_suggestion(error_msg: str) -> str:
    if 'timeout' in error_msg.lower():
        return 'Riprova manualmente o contatta il sito'
    elif '403' in error_msg or '401' in error_msg:
        return 'Sito protetto da WAF, necessario proxy premium'
    elif 'connection' in error_msg.lower():
        return 'Sito temporaneamente irraggiungibile'
    else:
        return 'Errore generico, verifica manualmente'
```

**Success Criteria**:
- ✅ Tutti i fallimenti registrati in `failed_sites` list
- ✅ Categorizzazione errori (timeout, WAF, connection)
- ✅ Suggerimenti actionable per il cliente

---

### ✅ Task 1.3: Sheet "Siti Non Analizzati" in Excel
**File**: `backend/core/report_generator.py`  
**Tempo Stimato**: 10 minuti

**Implementazione**:
```python
# Riga ~45, dopo la creazione dello sheet "Competitor Analizzati":
if failed_sites and len(failed_sites) > 0:
    # Crea nuovo sheet
    ws_failed = wb.create_sheet(title="Siti Non Analizzati")
    
    # Headers con stile
    headers = ['URL', 'Motivo Errore', 'Suggerimento', 'Timestamp']
    for col_idx, header in enumerate(headers, start=1):
        cell = ws_failed.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='DC3545', end_color='DC3545', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')
    
    # Data rows
    for row_idx, site in enumerate(failed_sites, start=2):
        ws_failed.cell(row=row_idx, column=1, value=site['url'])
        ws_failed.cell(row=row_idx, column=2, value=site['error'])
        ws_failed.cell(row=row_idx, column=3, value=site['suggestion'])
        ws_failed.cell(row=row_idx, column=4, value=datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    # Auto-size columns
    for col in ws_failed.columns:
        max_length = max(len(str(cell.value or '')) for cell in col)
        ws_failed.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)
```

**Pass failed_sites to report_generator**:
```python
# In analyze_stream.py, riga ~90:
report_path = report_generator.generate_excel_report(
    client_keywords=keywords,
    competitor_results=final_results,
    failed_sites=failed_sites,  # ⬅️ NEW PARAM
    output_dir=reports_dir
)
```

**Success Criteria**:
- ✅ Sheet creato solo se `len(failed_sites) > 0`
- ✅ Colori rossi per headers (DC3545)
- ✅ Colonne auto-sized
- ✅ Timestamp per tracciare quando è fallito

---

## 📋 FASE 2 - Scalabilità (30 minuti)

### ✅ Task 2.1: Batch Automatico da 100 Siti
**File**: `backend/api/analyze_stream.py`  
**Tempo Stimato**: 15 minuti

**Implementazione**:
```python
# Riga ~20, prima del loop principale:
BATCH_SIZE = 100

async def analyze_urls_stream(urls: List[str], ...):
    total_sites = len(urls)
    
    if total_sites > BATCH_SIZE:
        logger.info(f"📦 BATCH MODE: {total_sites} siti divisi in {math.ceil(total_sites/BATCH_SIZE)} batch")
        await send_sse_event({
            'event': 'batch_info',
            'data': {
                'total_sites': total_sites,
                'batch_size': BATCH_SIZE,
                'num_batches': math.ceil(total_sites / BATCH_SIZE)
            }
        })
    
    # Split in batch
    for batch_num in range(0, total_sites, BATCH_SIZE):
        batch_urls = urls[batch_num:batch_num + BATCH_SIZE]
        batch_index = batch_num // BATCH_SIZE + 1
        total_batches = math.ceil(total_sites / BATCH_SIZE)
        
        logger.info(f"🔄 Processing BATCH {batch_index}/{total_batches} ({len(batch_urls)} siti)")
        await send_sse_event({
            'event': 'batch_start',
            'data': {
                'batch_num': batch_index,
                'total_batches': total_batches,
                'batch_size': len(batch_urls)
            }
        })
        
        # Process batch (existing loop logic)
        for idx, url in enumerate(batch_urls):
            global_index = batch_num + idx + 1
            # ... existing code con global_index invece di idx ...
        
        # Batch completed
        await send_sse_event({
            'event': 'batch_complete',
            'data': {
                'batch_num': batch_index,
                'sites_processed': len(batch_urls)
            }
        })
```

**Success Criteria**:
- ✅ Batch automatico quando `len(urls) > 100`
- ✅ Log chiaro: "BATCH 1/5 (100 siti)"
- ✅ SSE events per batch_start, batch_complete
- ✅ Indici globali corretti per progress tracking

---

### ✅ Task 2.2: Progress Bar Batch-Aware
**File**: `frontend/src/app/analyze/page.tsx`  
**Tempo Stimato**: 15 minuti

**Implementazione**:
```typescript
// Riga ~30, aggiungi state per batch:
const [batchInfo, setBatchInfo] = useState<{
  currentBatch: number;
  totalBatches: number;
  totalSites: number;
} | null>(null);

// Nel SSE listener, aggiungi handler:
eventSource.addEventListener('batch_info', (e) => {
  const data = JSON.parse(e.data);
  setBatchInfo({
    currentBatch: 1,
    totalBatches: data.num_batches,
    totalSites: data.total_sites
  });
});

eventSource.addEventListener('batch_start', (e) => {
  const data = JSON.parse(e.data);
  setBatchInfo(prev => ({
    ...prev,
    currentBatch: data.batch_num,
    totalBatches: data.total_batches,
    totalSites: prev?.totalSites || 0
  }));
});

// Nel render della progress bar:
{batchInfo && batchInfo.totalBatches > 1 && (
  <div className="mb-2 text-sm text-gray-600">
    📦 Batch {batchInfo.currentBatch} di {batchInfo.totalBatches}
    <span className="text-xs ml-2">
      ({batchInfo.totalSites} siti totali)
    </span>
  </div>
)}

<ProgressBar 
  current={progress.processed} 
  total={progress.total}
  label={batchInfo?.totalBatches > 1 
    ? `Sito ${progress.processed}/${progress.total} (Batch ${batchInfo.currentBatch})`
    : `Sito ${progress.processed}/${progress.total}`
  }
/>
```

**Success Criteria**:
- ✅ Mostra "Batch X di Y" solo se `totalBatches > 1`
- ✅ Progress bar riflette conteggio globale (non per-batch)
- ✅ UI update smooth durante transizioni batch

---

## 🧪 Test Plan

### Test 1: Timeout Singolo Sito
```bash
# Crea file test con URL lento:
echo "https://euroventilatori-int.com" > test_timeout.txt

# Run analysis:
curl -X POST http://localhost:8000/api/analyze-stream \
  -F "file=@test_timeout.txt" \
  -F "keywords=test"

# Expected:
# - Timeout dopo 60s
# - Log: "⏱️ TIMEOUT (60s) for ..."
# - SSE event: site_failed
# - Analisi continua (non si blocca)
```

### Test 2: Siti Falliti in Excel
```bash
# Usa dataset con siti noti per fallire:
# - saiver.com (connection reset)
# - vecamco.com (HTTP 403)
# - enginiasrl.com (timeout)

# Expected:
# - Sheet "Siti Non Analizzati" creato
# - 3 righe con URL, errore, suggerimento
# - Headers rossi, colonne auto-sized
```

### Test 3: Batch Processing
```bash
# Crea file con 250 URLs:
python -c "
with open('test_250_sites.txt', 'w') as f:
    for i in range(250):
        f.write(f'https://example{i}.com\n')
"

# Run analysis:
# Expected:
# - Log: "📦 BATCH MODE: 250 siti divisi in 3 batch"
# - SSE events: batch_info, batch_start (x3), batch_complete (x3)
# - Progress: "Batch 1/3", "Batch 2/3", "Batch 3/3"
# - Total processed: 250/250
```

### Test 4: Railway Production
```bash
# Deploy su Railway:
git add -A
git commit -m "feat: timeout 60s + batch processing + failed sites report"
git push origin main

# Railway auto-deploy, poi test con dataset reale:
# - Upload "Prova 2.xls" (91 siti)
# - Monitor logs per timeout/batch behavior
# - Download report → verificare sheet "Siti Non Analizzati"
```

---

## 📊 Success Metrics

### Before (Production Issue)
- ❌ 7 ore di freeze su site #48
- ❌ 43 siti completati ma cliente non può vederli
- ❌ 4 siti falliti senza traccia
- ❌ Progress bloccato al 14%
- ❌ Batch di 500+ siti impossibile

### After (Target)
- ✅ Max 60s per sito, zero freeze infiniti
- ✅ Risultati parziali sempre disponibili
- ✅ Sheet Excel con siti falliti + suggerimenti
- ✅ Progress bar accurato anche per 500+ siti
- ✅ Log strutturati per debugging

---

## 🚀 Rollout Plan

### Fase 1 (Immediate)
1. Implementare Task 1.1, 1.2, 1.3 (20 min)
2. Test locale con URL noti per timeout
3. Commit: `feat(analysis): add 60s timeout + failed sites report`

### Fase 2 (Same Session)
4. Implementare Task 2.1, 2.2 (30 min)
5. Test locale con 250 URLs fake
6. Commit: `feat(analysis): add batch processing for 100+ sites`

### Fase 3 (Deploy)
7. Push to GitHub
8. Railway auto-deploy
9. Test con dataset reale del cliente
10. Monitor logs per 1 analisi completa

---

## 📝 Checklist Implementazione

### FASE 1
- [ ] Task 1.1: asyncio.timeout(60) wrapper in analyze_stream.py
- [ ] Task 1.2: failed_sites tracking + error categorization
- [ ] Task 1.3: Sheet "Siti Non Analizzati" in report_generator.py
- [ ] Test timeout con euroventilatori-int.com
- [ ] Test Excel report con siti falliti
- [ ] Commit + push Fase 1

### FASE 2
- [ ] Task 2.1: Batch logic (BATCH_SIZE=100) in analyze_stream.py
- [ ] Task 2.2: Progress bar batch-aware in frontend
- [ ] Test con 250 URLs fake
- [ ] Test SSE events (batch_info, batch_start, batch_complete)
- [ ] Commit + push Fase 2

### FASE 3 (Validation)
- [ ] Railway deploy successful
- [ ] Test produzione con "Prova 2.xls" (91 siti)
- [ ] Verify zero timeout > 60s in logs
- [ ] Verify "Siti Non Analizzati" sheet exists
- [ ] Cliente conferma può vedere siti falliti
- [ ] Close issue "Analisi bloccata al 14%"

---

## 🔄 Rollback Plan

Se problemi in produzione:
1. Revert commit: `git revert HEAD`
2. Push: `git push origin main`
3. Railway auto-rollback to previous version
4. Debug locally con logs
5. Fix + redeploy

---

**Status**: 🟡 PRONTO PER IMPLEMENTAZIONE  
**Next Step**: Implementare FASE 1 (Task 1.1 → 1.2 → 1.3)
