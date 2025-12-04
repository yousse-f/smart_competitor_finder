from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List
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
    fail_analysis
)
from utils.excel_utils import ExcelProcessor
import math

router = APIRouter()

# 🛠️ Helper function per categorizzare errori e fornire suggerimenti
def _get_error_suggestion(error_msg: str) -> str:
    """Fornisce suggerimenti actionable basati sul tipo di errore"""
    error_lower = error_msg.lower()
    
    if 'timeout' in error_lower or 'timed out' in error_lower:
        return 'Sito troppo lento o bloccato - riprova manualmente o contatta il sito'
    elif '403' in error_msg or '401' in error_msg:
        return 'Sito protetto da WAF/firewall - necessario proxy premium (ScrapingBee)'
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

@router.post("/upload-and-analyze-stream")
async def upload_and_analyze_stream(
    file: UploadFile = File(...),
    keywords: str = Form(...)
):
    """
    🚀 Real-time streaming analysis with Server-Sent Events (SSE).
    Sends progress updates as each competitor is analyzed.
    """
    try:
        # Parse keywords from form data
        keywords_list = [k.strip() for k in keywords.replace('"', '').replace('[', '').replace(']', '').split(',')]
        
        logging.info(f"Starting STREAMING bulk analysis with {len(keywords_list)} keywords")
        
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
        client_url = "bulk_analysis"  # For bulk analysis, we don't have a single client URL
        
        try:
            create_analysis_file(
                analysis_id=analysis_id,
                client_url=client_url,
                client_keywords=keywords_list,
                total_sites=len(urls)
            )
            logging.info(f"✅ Created analysis file: {analysis_id}")
        except Exception as create_error:
            logging.error(f"❌ Failed to create analysis file: {create_error}")
            # Continue anyway - analysis will work but won't be persistent
        
        # Return SSE stream
        return StreamingResponse(
            stream_analysis_progress(urls, keywords_list, analysis_id),
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

async def stream_analysis_progress(urls: List[str], keywords: List[str], analysis_id: str):
    """
    🎯 Generator that yields SSE events for each analyzed competitor.
    🆕 Now saves progress to persistent JSON file
    ⏱️ FASE 1: Max 60s timeout per site
    📦 FASE 2: Automatic batch processing for 100+ sites
    
    Event format:
    data: {"event": "started", "analysis_id": "...", "total": 10}
    data: {"event": "batch_info", "total_sites": 250, "batch_size": 100, "num_batches": 3}
    data: {"event": "batch_start", "batch_num": 1, "total_batches": 3, "batch_size": 100}
    data: {"event": "progress", "url": "...", "current": 1, "total": 10, "percentage": 10}
    data: {"event": "result", "url": "...", "score": 75, "keywords_found": [...]}
    data: {"event": "batch_complete", "batch_num": 1, "sites_processed": 100}
    data: {"event": "complete", "matches": [...], "summary": {...}}
    """
    from core.hybrid_scraper_v2 import hybrid_scraper_v2
    from core.matching import keyword_matcher
    from bs4 import BeautifulSoup
    import aiohttp
    import ssl
    
    matches = []
    failed_sites = []  # 🆕 FASE 1: Track failed sites for Excel report
    total_urls = len(urls)
    
    # 🆕 Send initial event with analysis_id
    yield f"data: {json.dumps({'event': 'started', 'analysis_id': analysis_id, 'total': total_urls, 'message': 'Analisi avviata con successo'})}\n\n"
    
    # 📦 FASE 2: Check if batch mode needed
    if total_urls > BATCH_SIZE:
        num_batches = math.ceil(total_urls / BATCH_SIZE)
        logging.info(f"📦 BATCH MODE: {total_urls} siti divisi in {num_batches} batch da {BATCH_SIZE}")
        yield f"data: {json.dumps({'event': 'batch_info', 'total_sites': total_urls, 'batch_size': BATCH_SIZE, 'num_batches': num_batches})}\n\n"
    
    try:
        # 📦 FASE 2: Process in batches
        for batch_num in range(0, total_urls, BATCH_SIZE):
            batch_urls = urls[batch_num:batch_num + BATCH_SIZE]
            batch_index = batch_num // BATCH_SIZE + 1
            total_batches = math.ceil(total_urls / BATCH_SIZE)
            
            if total_urls > BATCH_SIZE:
                logging.info(f"🔄 Processing BATCH {batch_index}/{total_batches} ({len(batch_urls)} siti)")
                yield f"data: {json.dumps({'event': 'batch_start', 'batch_num': batch_index, 'total_batches': total_batches, 'batch_size': len(batch_urls)})}\n\n"
            
            # Process each URL in batch
            for idx, url in enumerate(batch_urls):
                global_index = batch_num + idx + 1
                percentage = int((global_index / total_urls) * 100)
                
                # Send progress event
                yield f"data: {json.dumps({'event': 'progress', 'url': url, 'current': global_index, 'total': total_urls, 'percentage': percentage})}\n\n"
                
                try:
                    logging.info(f"📊 Streaming analysis {global_index}/{total_urls}: {url}")
                    
                    # ⏱️ Max 90s timeout per site (come analisi client - serve per doppio fallback)
                    try:
                        async with asyncio.timeout(90):
                            # 1. Scrape competitor site con DOPPIO FALLBACK (Basic HTTP → Browser Pool)
                            scrape_result = await hybrid_scraper_v2.scrape_intelligent(url, max_keywords=20, use_advanced=True)
                    except asyncio.TimeoutError:
                        logging.error(f"⏱️ TIMEOUT (90s) for {url}")
                        failed_sites.append({
                            'url': url,
                            'error': 'Timeout dopo 90 secondi',
                            'suggestion': 'Sito troppo lento o bloccato - riprova manualmente',
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        yield f"data: {json.dumps({'event': 'site_failed', 'url': url, 'reason': 'timeout_90s'})}\n\n"
                        continue
                
                    if not scrape_result.get('status') == 'success':
                        error_msg = scrape_result.get('error', 'Scraping failed')
                        logging.warning(f"⚠️ Scraping failed for {url}: {error_msg}")
                        
                        # 🆕 FASE 1: Track failed site
                        failed_sites.append({
                            'url': url,
                            'error': error_msg[:100],  # Primi 100 caratteri
                            'suggestion': _get_error_suggestion(error_msg),
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        # Send error event
                        yield f"data: {json.dumps({'event': 'site_failed', 'url': url, 'reason': 'scraping_failed', 'message': error_msg})}\n\n"
                        continue
                
                    # Extract full text
                    try:
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        
                        timeout = aiohttp.ClientTimeout(total=10)
                        async with aiohttp.ClientSession(timeout=timeout) as session:
                            async with session.get(url, ssl=ssl_context) as response:
                                if response.status == 200:
                                    html_content = await response.text()
                                    soup = BeautifulSoup(html_content, 'html.parser')
                                    for element in soup(["script", "style", "meta", "link"]):
                                        element.decompose()
                                    full_text = soup.get_text()
                                    full_text = ' '.join(full_text.split())
                                else:
                                    full_text = ""
                    except Exception:
                        full_text = ""
                    
                    # 2. Calculate match score
                    match_results = await keyword_matcher.calculate_match_score(
                        target_keywords=keywords,
                        site_content=full_text,
                        business_context=None,
                        site_title=scrape_result.get('title', ''),
                        meta_description=scrape_result.get('description', ''),
                        client_sector_data=None
                    )
                    
                    score = int(match_results['match_score'])
                    found_keywords = match_results['found_keywords']
                    
                    match = CompetitorMatch(
                        url=url,
                        score=score,
                        keywords_found=found_keywords,
                        title=scrape_result.get('title', ''),
                        description=scrape_result.get('description', '')
                    )
                    matches.append(match)
                    
                    # Send result event
                    yield f"data: {json.dumps({'event': 'result', 'url': url, 'score': score, 'keywords_found': found_keywords, 'title': match.title})}\n\n"
                    
                    logging.info(f"✅ {url}: {score}% match")
                    
                    # 💾 Save progress to file
                    update_analysis_progress(
                        analysis_id=analysis_id,
                        processed_sites=global_index,
                        new_result={
                            'url': url,
                            'score': score,
                            'keywords_found': found_keywords,
                            'title': match.title,
                            'description': match.description,
                            'status': match.status
                        }
                    )
                    
                except Exception as e:
                    error_msg = str(e)
                    logging.error(f"❌ Error processing {url}: {error_msg}")
                    
                    # 🆕 FASE 1: Track failed site with categorization
                    failed_sites.append({
                        'url': url,
                        'error': error_msg[:100],
                        'suggestion': _get_error_suggestion(error_msg),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    # Send error event but continue
                    yield f"data: {json.dumps({'event': 'site_failed', 'url': url, 'reason': 'processing_error', 'message': error_msg})}\n\n"
                    
                    # 🆕 AGGIUNGERE SITI FALLITI AL REPORT con score=0 e messaggio chiaro
                    matches.append(CompetitorMatch(
                        url=url,
                        score=0,
                        keywords_found=[],
                        title=f"⚠️ Errore Analisi",
                        description=f"Impossibile analizzare questo sito: {error_msg[:100]}"
                    ))
            
            # 📦 FASE 2: Batch complete event
            if total_urls > BATCH_SIZE:
                logging.info(f"✅ BATCH {batch_index}/{total_batches} completato ({len(batch_urls)} siti processati)")
                yield f"data: {json.dumps({'event': 'batch_complete', 'batch_num': batch_index, 'sites_processed': len(batch_urls)})}\n\n"
        
        # Sort by score
        matches.sort(key=lambda x: x.score, reverse=True)
        
        # 💾 Mark analysis as complete
        complete_analysis(analysis_id)
        
        # Calculate summary
        total_competitors = len(matches)
        average_score = sum(match.score for match in matches) / len(matches) if matches else 0
        
        direct_competitors = [m for m in matches if m.status['category'] == 'DIRECT']
        potential_competitors = [m for m in matches if m.status['category'] == 'POTENTIAL']
        non_competitors = [m for m in matches if m.status['category'] == 'NON_COMPETITOR']
        
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 🆕 FASE 1: Log failed sites summary
        if failed_sites:
            logging.warning(f"⚠️ {len(failed_sites)} siti falliti durante l'analisi")
            for failed in failed_sites:
                logging.warning(f"  - {failed['url']}: {failed['error']}")
        
        # Send completion event with full results
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
                    "competitor_status": match.status
                }
                for match in matches
            ],
            "failed_sites": failed_sites,  # 🆕 FASE 1: Include failed sites for Excel report
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
            }
        }
        
        yield f"data: {json.dumps(final_response)}\n\n"
        
        logging.info(f"🎉 Streaming analysis complete: {total_competitors} competitors")
    
    except Exception as e:
        # 💾 Mark analysis as failed
        fail_analysis(analysis_id, str(e))
        
        logging.error(f"❌ Critical error in analysis {analysis_id}: {str(e)}")
        
        # Send error event
        error_response = {
            "event": "error",
            "status": "failed",
            "message": f"Analisi fallita: {str(e)}"
        }
        yield f"data: {json.dumps(error_response)}\n\n"
