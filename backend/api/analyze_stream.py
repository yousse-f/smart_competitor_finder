from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import pandas as pd
import logging
import io
import json
import asyncio
from datetime import datetime

from core.keyword_extraction import extract_keywords_bulk
from .upload_analyze import classify_competitor_status, CompetitorMatch, analyze_competitors_bulk
from .analysis_manager import (
    create_analysis_id,
    create_analysis_file,
    update_analysis_progress,
    complete_analysis,
    fail_analysis,
    add_failed_site
)
from utils.excel_utils import ExcelProcessor
import math

router = APIRouter()

# 🎯 In-memory cache per AI analysis (evita rianalisi stessi competitor)
_ai_cache = {}
_client_context_cache = {}

# 🛠️ Helper function per categorizzare errori e fornire suggerimenti
def _get_error_suggestion(error_msg: str) -> str:
    """Fornisce suggerimenti actionable basati sul tipo di errore"""
    error_lower = error_msg.lower()
    
    if 'timeout' in error_lower or 'timed out' in error_lower:
        return 'Sito troppo lento o bloccato - riprova manualmente o contatta il sito'
    elif '403' in error_msg or '401' in error_msg:
        return 'Sito protetto da WAF/firewall - necessario accesso manuale o credenziali'
    elif 'connection' in error_lower or 'connect' in error_lower:
        return 'Sito temporaneamente irraggiungibile - verifica che sia online'
    elif 'ssl' in error_lower or 'certificate' in error_lower:
        return 'Problemi certificato SSL - sito potrebbe avere configurazione errata'
    elif '404' in error_msg:
        return 'Pagina non trovata - verifica URL corretto'
    elif '500' in error_msg or '502' in error_msg or '503' in error_msg:
        return 'Errore server del sito - riprova più tardi'
    else:
        return 'Errore generico - verifica manualmente il sito'


# ============================================================
# Le funzioni enrich_keywords_context, analyze_client_context,
# get_ai_analysis_cached, validate_and_blend_scores sono state
# RIMOSSE nel refactoring v2.0 (18/02/2026).
# Classificazione ora delegata interamente a classify_competitor_with_ai()
# in core/ai_site_analyzer.py
# ============================================================


@router.post("/upload-and-analyze-stream")
async def upload_and_analyze_stream(
    file: UploadFile = File(...),
    keywords: str = Form(...),
    client_url: str = Form(None)  # 🆕 Optional: URL del sito client per context migliore
):
    """
    🚀 Real-time streaming analysis with Server-Sent Events (SSE).
    Sends progress updates as each competitor is analyzed.
    
    🆕 IMPROVEMENTS:
    - AI classification vera (non hardcoded)
    - Blending intelligente KW + AI
    - Client context arricchito
    - Caching AI results
    - Validazione score finale
    """
    try:
        # Parse keywords from form data
        keywords_list = [k.strip() for k in keywords.replace('"', '').replace('[', '').replace(']', '').split(',')]
        
        logging.info(f"Starting STREAMING bulk analysis with {len(keywords_list)} keywords")
        if client_url:
            logging.info(f"Client URL provided: {client_url}")
        
        # Read the uploaded file
        contents = await file.read()
        
        # 🆕 Use new ExcelProcessor for intelligent column detection
        excel_processor = ExcelProcessor()
        sites_data = []
        
        try:
            if file.filename and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
                # Use intelligent Excel processing with auto-detection
                sites_data = excel_processor.process_excel_file(contents, file.filename)
                urls = [site['url'] for site in sites_data]
                
            elif file.filename and file.filename.endswith('.csv'):
                # CSV processing (simple first column extraction)
                df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
                urls = []
                first_column = df.iloc[:, 0].dropna()
                for url in first_column:
                    url_str = str(url).strip()
                    if url_str and url_str.lower() not in ['nan', 'none', '']:
                        if not url_str.startswith(('http://', 'https://')):
                            url_str = 'https://' + url_str
                        urls.append(url_str)
                
            else:
                # Plain text file processing
                text_content = contents.decode('utf-8')
                urls = []
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                for line in lines:
                    if line and line.lower() not in ['nan', 'none', '']:
                        if not line.startswith(('http://', 'https://')):
                            line = 'https://' + line
                        urls.append(line)
                
        except Exception as file_error:
            logging.error(f"File parsing error: {str(file_error)}")
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to parse file. Error: {str(file_error)}"
            )
        
        logging.info(f"Extracted {len(urls)} URLs for streaming analysis")
        
        if not urls:
            raise HTTPException(status_code=400, detail="No valid URLs found in the file")
        
        # 🆕 Generate analysis ID and create persistent file
        analysis_id = create_analysis_id()
        client_url_for_analysis = client_url or "bulk_analysis"
        
        try:
            create_analysis_file(
                analysis_id=analysis_id,
                client_url=client_url_for_analysis,
                client_keywords=keywords_list,
                total_sites=len(urls)
            )
            logging.info(f"✅ Created analysis file: {analysis_id}")
        except Exception as create_error:
            logging.error(f"❌ Failed to create analysis file: {create_error}")
            # Continue anyway - analysis will work but won't be persistent
        
        # Return SSE stream
        return StreamingResponse(
            stream_analysis_progress(urls, keywords_list, analysis_id, client_url),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        logging.error(f"Error in streaming analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


# 📦 Batch configuration
BATCH_SIZE = 100  # Split analyses into batches of 100 sites

async def stream_analysis_progress(
    urls: List[str], 
    keywords: List[str], 
    analysis_id: str,
    client_url: Optional[str] = None
):
    """
    🚀 TWO-PASS ORCHESTRA: Parallel wget + fallback + AI generation
    
    Architettura v2.0 (18/02/2026):
    - WAVE 1: Wget parallelo (fast scraping, 15 concurrent)
    - WAVE 2: Fallback Playwright + classify_competitor_with_ai() (gpt-4o-mini)
      → 1 sola chiamata OpenAI per competitor, nessun sistema locale
    
    Performance: 93 sites in 4-6 min (vs 15 min sequenziale)
    """
    from core.wget_scraper import wget_scraper
    from core.hybrid_scraper_v2 import hybrid_scraper_v2
    
    matches = []
    failed_sites = []
    total_urls = len(urls)
    failed_count = 0  # Track fallimenti per timeout progressivo
    
    # 🆕 Send initial event
    yield f"data: {json.dumps({'event': 'started', 'analysis_id': analysis_id, 'total': total_urls, 'message': 'Analisi Two-Pass avviata'})}\n\n"
    
    # 🚀 WAVE 1: WGET PARALLEL BLAST WITH LIVE PROGRESS
    logging.info(f"🚀 WAVE 1: Wget scraping parallelo per {total_urls} competitors...")
    yield f"data: {json.dumps({'event': 'wave1_started', 'method': 'wget', 'concurrent': 15, 'message': 'Scraping parallelo in corso...'})}\n\n"
    
    # Genera job_id unico per questo batch
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Lancia wget in parallelo per TUTTI gli URL
    wget_tasks = [wget_scraper.scrape(url, job_id) for url in urls]
    
    # 🆕 Process results AS THEY COMPLETE (real-time progress!)
    wget_results = []
    wget_results_map = {}  # 🔑 FIX: url → result dict (as_completedè in completion order, non in URL order)
    scraped_count = 0
    successful_count = 0
    wget_failed_count = 0
    
    for completed_task in asyncio.as_completed(wget_tasks):
        try:
            result = await completed_task
            
            # Handle exceptions
            if isinstance(result, Exception):
                result = {
                    'success': False,
                    'url': urls[len(wget_results)],
                    'error': str(result),
                    'method': 'wget_exception'
                }
            
            wget_results.append(result)
            wget_results_map[result.get('url', '')] = result  # 🔑 FIX: indicizza per URL
            scraped_count += 1
            
            # Update counters
            if result.get('success'):
                successful_count += 1
                status = 'success'
                words = result.get('word_count', 0)
                pages = result.get('page_count', 0)
                message = f"{pages} pages, {words} words"
            else:
                wget_failed_count += 1
                status = 'failed'
                message = result.get('error', 'Unknown error')[:50]
            
            # 🎉 Send LIVE progress update for THIS site
            progress_data = {
                'event': 'wave1_progress',
                'current': scraped_count,
                'total': total_urls,
                'percentage': int((scraped_count / total_urls) * 100),
                'url': result.get('url', 'unknown'),
                'status': status,
                'message': message,
                'successful': successful_count,
                'failed': wget_failed_count
            }
            yield f"data: {json.dumps(progress_data)}\n\n"
            
            logging.info(f"✅ Wave 1: {scraped_count}/{total_urls} - {result.get('url', 'unknown')}: {status}")
            
        except Exception as e:
            logging.error(f"❌ Error processing task: {e}")
            scraped_count += 1
            wget_failed_count += 1
            
            # Send error progress
            error_data = {
                'event': 'wave1_progress',
                'current': scraped_count,
                'total': total_urls,
                'percentage': int((scraped_count / total_urls) * 100),
                'status': 'error',
                'message': str(e)[:50],
                'successful': successful_count,
                'failed': wget_failed_count
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    # Statistiche Wave 1
    successful_wget = [r for r in wget_results if r.get('success')]
    failed_wget = [r for r in wget_results if not r.get('success')]
    
    logging.info(f"✅ WAVE 1 complete: {len(successful_wget)} success, {len(failed_wget)} failed")
    yield f"data: {json.dumps({'event': 'wave1_complete', 'successful': len(successful_wget), 'failed': len(failed_wget), 'success_rate': round(len(successful_wget)/total_urls*100, 1)})}\n\n"
    
    # 🚀 WAVE 2: FALLBACK + AI PROCESSING (parallelo con limits)
    logging.info(f"🔄 WAVE 2: Fallback per {len(failed_wget)} falliti + AI per tutti...")
    yield f"data: {json.dumps({'event': 'wave2_started', 'method': 'fallback+AI', 'concurrent': 10, 'message': 'Analisi AI in corso...'})}\n\n"
    
    # Semaphore limits per evitare overload
    ai_semaphore = asyncio.Semaphore(10)  # Max 10 AI calls concorrenti
    fallback_semaphore = asyncio.Semaphore(5)  # Max 5 fallback Playwright concorrenti
    
    async def process_competitor_with_ai(url: str, scrape_result: Dict, index: int):
        """Processa singolo competitor: fallback se necessario + AI analysis"""
        nonlocal failed_count
        
        try:
            # Fallback se wget fallito
            if not scrape_result.get('success'):
                # Timeout progressivo: più fallimenti = timeout più breve
                timeout = 30 if failed_count < 10 else 20 if failed_count < 20 else 10
                
                logging.info(f"🔄 Fallback per {url} (timeout: {timeout}s)...")
                async with fallback_semaphore:
                    try:
                        scrape_result = await asyncio.wait_for(
                            hybrid_scraper_v2.scrape_intelligent(url, max_keywords=50, use_advanced=True),
                            timeout=timeout
                        )
                    except asyncio.TimeoutError:
                        scrape_result = {
                            'status': 'failed',
                            'error': f'Timeout dopo {timeout}s'
                        }
                    
                    if not scrape_result.get('status') == 'success':
                        error_msg = scrape_result.get('error', 'Fallback failed')
                        logging.warning(f"⚠️ Fallback fallito per {url}: {error_msg}")
                        
                        failed_count += 1
                        
                        # Track failed site
                        failed_site_data = {
                            'url': url,
                            'error': error_msg[:100],
                            'suggestion': _get_error_suggestion(error_msg),
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        failed_sites.append(failed_site_data)
                        add_failed_site(analysis_id, failed_site_data)
                        
                        return  # Skip questo competitor
            
            # � Estrai testo dal scrape result
            full_text = scrape_result.get('text', '') or scrape_result.get('content', '')            
            logging.info(f"📄 SCRAPE {url}: {len(full_text)} chars")
            logging.info(f"📄 PREVIEW: {full_text[:300].replace(chr(10), ' ')}")            
            # Keyword trovate (per display UI)
            found_keywords = [kw for kw in keywords if kw.lower() in full_text.lower()]
            
            # 🤖 CLASSIFICAZIONE UNICA via OpenAI gpt-4o-mini
            async with ai_semaphore:
                from core.ai_site_analyzer import classify_competitor_with_ai
                logging.info(f"🤖 AI classify: {url}")
                ai_result = await classify_competitor_with_ai(
                    client_keywords=keywords,
                    competitor_content=full_text,
                    competitor_url=url
                )
            
            final_score          = ai_result['score']
            final_classification = ai_result['classification']
            reason               = ai_result['reason']
            competitor_sector    = ai_result.get('competitor_sector', 'unknown')
            overlap_percentage   = 0
            recommended_action   = "Valutare manualmente"
            
            logging.info(f"✅ {index}/{total_urls} - {url}: {final_score}% [{final_classification}] — {reason}")
            
            # Crea match con dati AI
            match = CompetitorMatch(
                url=url,
                score=final_score,
                keywords_found=found_keywords,
                title=scrape_result.get('title', ''),
                description=scrape_result.get('description', ''),
                classification=final_classification,
                reason=reason,
                ai_confidence=1.0,
                competitor_description="",
                competitor_sector=competitor_sector,
                recommended_action=recommended_action,
                overlap_percentage=overlap_percentage
            )
            
            # Store info for parent to yield events
            match._index = index
            match._percentage = int((index / total_urls) * 100)
            match.keywords_found = found_keywords
            match.classification = final_classification
            match.ai_confidence = 1.0
            
            # Save progress
            update_analysis_progress(
                analysis_id=analysis_id,
                processed_sites=index,
                new_result={
                    'url': url,
                    'score': final_score,
                    'keywords_found': found_keywords,
                    'title': match.title,
                    'description': match.description,
                    'status': match.status,
                    'classification': final_classification,
                    'ai_confidence': 0.0
                }
            )
            
            return match
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"❌ Error processing {url}: {error_msg}")
            
            failed_count += 1
            
            # Track failed
            failed_site_data = {
                'url': url,
                'error': error_msg[:100],
                'suggestion': _get_error_suggestion(error_msg),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            failed_sites.append(failed_site_data)
            add_failed_site(analysis_id, failed_site_data)
            
            # Return None - parent will handle event
            return None
    
    # Lancia processing parallelo per tutti i competitors
    processing_tasks = []
    for idx, url in enumerate(urls, 1):
        # 🔑 FIX: cerca il risultato wget per questo URL specifico (non per posizione)
        wget_result = wget_results_map.get(url, {'success': False, 'error': 'no wget result', 'url': url})
        task = process_competitor_with_ai(url, wget_result, idx)
        processing_tasks.append(task)
    
    # Process results as they complete
    for idx, task in enumerate(processing_tasks, 1):
        try:
            match = await task
            if match:
                # Yield progress event
                yield f"data: {json.dumps({'event': 'progress', 'url': match.url, 'current': match._index, 'total': total_urls, 'percentage': match._percentage})}\n\n"
                
                # Yield result event  
                yield f"data: {json.dumps({'event': 'result', 'url': match.url, 'score': match.score, 'keywords_found': match.keywords_found, 'classification': match.classification, 'ai_confidence': match.ai_confidence})}\n\n"
                
                matches.append(match)
        except Exception as e:
            logging.error(f"❌ Error awaiting task: {str(e)}")
            failed_site_data = {
                'url': urls[idx-1] if idx <= len(urls) else 'unknown',
                'error': str(e)[:100],
                'suggestion': _get_error_suggestion(str(e)),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            failed_sites.append(failed_site_data)
            add_failed_site(analysis_id, failed_site_data)
    
    try:
        # Sort by score
        matches.sort(key=lambda x: x.score, reverse=True)
        
        # Mark analysis complete
        complete_analysis(analysis_id)
        
        # Calculate summary
        total_competitors = len(matches)
        average_score = sum(match.score for match in matches) / len(matches) if matches else 0
        
        direct_competitors = [m for m in matches if m.status['category'] == 'DIRECT']
        potential_competitors = [m for m in matches if m.status['category'] == 'POTENTIAL']
        non_competitors = [m for m in matches if m.status['category'] == 'NON_COMPETITOR']
        
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate statistics from results
        successful_count = len(successful_wget)
        total_sites = len(urls)
        success_rate = (successful_count / total_sites * 100) if total_sites > 0 else 0
        
        # Calculate average duration from wget_results (if available)
        durations = [r.get('duration', 0) for r in wget_results if r.get('success') and r.get('duration')]
        avg_duration = sum(durations) / len(durations) if durations else 0
        total_duration = sum(durations) if durations else 0
        
        # Log statistiche finali
        logging.info(f"📊 WAVE 1 Stats - Success: {successful_count}, Failed: {wget_failed_count}, Avg: {avg_duration:.1f}s")
        logging.info(f"📊 WAVE 2 Stats - Total: {total_competitors}, Failed: {len(failed_sites)}")
        logging.info(f"📊 Classifications - Direct: {len(direct_competitors)}, Potential: {len(potential_competitors)}, Non: {len(non_competitors)}")
        
        # Send completion event
        final_response = {
            "event": "complete",
            "status": "success",
            "total_competitors": total_competitors,
            "matches": [
                {
                    "url": match.url,
                    "score": match.score,
                    "keywords_found": match.keywords_found,
                    "title": match.title,
                    "description": match.description,
                    "competitor_status": match.status,
                    "classification": match.classification,
                    "ai_confidence": match.ai_confidence
                }
                for match in matches
            ],
            "failed_sites": failed_sites,
            "failed_count": len(failed_sites),
            "average_score": round(average_score, 1),
            "report_id": report_id,
            "summary_by_status": {
                "direct": {
                    "count": len(direct_competitors),
                    "label": "Competitor Diretti",
                    "emoji": "🟢"
                },
                "potential": {
                    "count": len(potential_competitors),
                    "label": "Da Valutare",
                    "emoji": "🟡"
                },
                "non_competitor": {
                    "count": len(non_competitors),
                    "label": "Non Competitor",
                    "emoji": "🔴"
                }
            },
            "performance": {
                "wget_success_rate": round(success_rate, 1),
                "wget_avg_duration": round(avg_duration, 1),
                "total_duration": round(total_duration, 1)
            },
            "client_context": {
                "primary_sector": "Rilevato da OpenAI per ogni competitor",
                "confidence": 1.0
            }
        }
        
        yield f"data: {json.dumps(final_response)}\n\n"
        
        logging.info(f"🎉 Two-Pass analysis complete: {total_competitors} competitors in {total_duration:.1f}s")
    
    except Exception as e:
        # Mark analysis as failed
        fail_analysis(analysis_id, str(e))
        
        logging.error(f"❌ Critical error in analysis {analysis_id}: {str(e)}")
        
        # Send error event
        error_response = {
            "event": "error",
            "status": "failed",
            "message": f"Analisi fallita: {str(e)}"
        }
        yield f"data: {json.dumps(error_response)}\n\n"