# UPGRADE: Refactoring classificazione competitor — v2.0

**Data**: 18 febbraio 2026  
**Branch**: main  
**Motivazione**: Il sistema precedente usava 3 sistemi in conflitto  
(`sector_classifier` + `semantic_filter` + `validate_and_blend_scores`)  
producendo risultati inconsistenti — es: **Direct: 6, Potential: 0, Non: 0**  
su qualsiasi dataset, indipendentemente dai dati reali.

---

## Cosa è stato ELIMINATO

| File | Motivo |
|------|--------|
| `backend/core/semantic_filter.py` | SentenceTransformer MiniLM — locale, lento, inaccurato |
| `backend/core/sector_classifier.py` | Classificazione keyword-based locale — conflitti con AI |
| `backend/core/ai_matcher.py` | AI matcher ibrido — sostituito dalla nuova funzione |
| `sentence-transformers` in requirements.txt | ~2GB dipendenze (torch + torchvision) |
| `scikit-learn==1.3.2` in requirements.txt | Non più necessario |

### Funzioni rimosse da `analyze_stream.py`
- `enrich_keywords_context()` — generava contesto artificioso per sector detection
- `analyze_client_context()` — importava `sector_classifier`, non più necessario
- `get_ai_analysis_cached()` — cache per `analyze_site()` obsoleta
- `validate_and_blend_scores()` — blend KW + AI che produceva conflitti

---

## Cosa è stato INTRODOTTO

### `classify_competitor_with_ai()` in `backend/core/ai_site_analyzer.py`

Funzione standalone che sostituisce **tutti** i sistemi precedenti:

```python
async def classify_competitor_with_ai(
    client_keywords: list,
    competitor_content: str,
    competitor_url: str
) -> dict:
    # Restituisce: classification, score (0-100), reason, competitor_sector
```

- **Modello**: `gpt-4o-mini` (veloce ed economico)
- **Input**: keyword del cliente + testo scraped del competitor
- **Output**: `{classification, score, reason, competitor_sector}`
- **Fallback**: restituisce `potential_competitor / score: 30` se OpenAI fallisce

---

## Architettura nuova (WAVE 2)

```
WAVE 1: wget_scraper.scrape(url) → testo grezzo [parallelo, 15 concurrent]
         ↓ fallback Playwright se wget fallisce
WAVE 2: classify_competitor_with_ai(keywords, testo, url)
         → score + classification + reason  [gpt-4o-mini, 10 concurrent]
```

**Prima (3 sistemi in conflitto):**
```
scrape → keyword_matcher → sector_classifier → validate_and_blend_scores
                              ↕ SentenceTransformer          ↕ override CASO 3
                         [sistemi si sovrascrivono a vicenda]
```

**Dopo (1 sistema):**
```
scrape → classify_competitor_with_ai → risultato finale
```

---

## Impatto performance

| Metrica | Prima | Dopo |
|---------|-------|------|
| Sistemi classificazione | 3 (in conflitto) | 1 (OpenAI) |
| Docker image size | ~4GB (con torch) | ~2GB |
| Chiamate API per competitor | 2-3 | 1 |
| Consistenza risultati | ❌ Sempre tutti Direct | ✅ Distribuzione reale |
| Dipendenze ML locali | sentence-transformers, scikit-learn, torch | — |

---

## Files modificati

```
backend/core/ai_site_analyzer.py     ← aggiunta classify_competitor_with_ai()
backend/api/analyze_stream.py        ← WAVE 2 riscritta, vecchie funzioni rimosse
backend/core/batch_bulk_analyzer.py  ← rimosso sector_classifier, usa nuova funzione
backend/requirements.txt             ← rimossi sentence-transformers, scikit-learn
```

---

## Rollback

Per tornare alla v1.x:
```bash
git checkout HEAD~1 -- backend/core/semantic_filter.py
git checkout HEAD~1 -- backend/core/sector_classifier.py
git checkout HEAD~1 -- backend/core/ai_matcher.py
git checkout HEAD~1 -- backend/api/analyze_stream.py
git checkout HEAD~1 -- backend/requirements.txt
pip install sentence-transformers scikit-learn==1.3.2
```
