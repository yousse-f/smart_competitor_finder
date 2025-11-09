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

router = APIRouter()

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
        
        # Extract URLs (same logic as upload_analyze.py)
        urls = []
        try:
            if file.filename and file.filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
                first_column = df.iloc[:, 0].dropna()
                for url in first_column:
                    url_str = str(url).strip()
                    if url_str and url_str.lower() not in ['nan', 'none', '']:
                        if not url_str.startswith(('http://', 'https://')):
                            url_str = 'https://' + url_str
                        urls.append(url_str)
                
            elif file.filename and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
                df = pd.read_excel(io.BytesIO(contents))
                first_column = df.iloc[:, 0].dropna()
                for url in first_column:
                    url_str = str(url).strip()
                    if url_str and url_str.lower() not in ['nan', 'none', '']:
                        if not url_str.startswith(('http://', 'https://')):
                            url_str = 'https://' + url_str
                        urls.append(url_str)
                
            else:
                text_content = contents.decode('utf-8')
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                for line in lines:
                    if line and line.lower() not in ['nan', 'none', '']:
                        if not line.startswith(('http://', 'https://')):
                            line = 'https://' + line
                        urls.append(line)
                
        except Exception as file_error:
            try:
                text_content = contents.decode('utf-8')
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                for line in lines:
                    if line and line.lower() not in ['nan', 'none', '']:
                        if not line.startswith(('http://', 'https://')):
                            line = 'https://' + line
                        urls.append(line)
            except Exception as text_error:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to parse file. Error: {str(file_error)}"
                )
        
        logging.info(f"Extracted {len(urls)} URLs for streaming analysis")
        
        if not urls:
            raise HTTPException(status_code=400, detail="No valid URLs found in the file")
        
        # Return SSE stream
        return StreamingResponse(
            stream_analysis_progress(urls, keywords_list),
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


async def stream_analysis_progress(urls: List[str], keywords: List[str]):
    """
    🎯 Generator that yields SSE events for each analyzed competitor.
    
    Event format:
    data: {"event": "progress", "url": "...", "current": 1, "total": 10, "percentage": 10}
    data: {"event": "result", "url": "...", "score": 75, "keywords_found": [...]}
    data: {"event": "complete", "matches": [...], "summary": {...}}
    """
    from core.hybrid_scraper_v2 import hybrid_scraper_v2
    from core.matching import keyword_matcher
    from bs4 import BeautifulSoup
    import aiohttp
    import ssl
    
    matches = []
    total_urls = len(urls)
    
    # Send initial event
    yield f"data: {json.dumps({'event': 'start', 'total': total_urls})}\n\n"
    
    for i, url in enumerate(urls):
        current_index = i + 1
        percentage = int((current_index / total_urls) * 100)
        
        # Send progress event
        yield f"data: {json.dumps({'event': 'progress', 'url': url, 'current': current_index, 'total': total_urls, 'percentage': percentage})}\n\n"
        
        try:
            logging.info(f"📊 Streaming analysis {current_index}/{total_urls}: {url}")
            
            # 1. Scrape competitor site
            scrape_result = await hybrid_scraper_v2.scrape_intelligent(url, max_keywords=20, use_advanced=True)
            
            if not scrape_result.get('status') == 'success':
                logging.warning(f"⚠️ Scraping failed for {url}")
                # Send error event
                yield f"data: {json.dumps({'event': 'error', 'url': url, 'message': 'Scraping failed'})}\n\n"
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
            
        except Exception as e:
            logging.error(f"❌ Error processing {url}: {str(e)}")
            # Send error event but continue
            yield f"data: {json.dumps({'event': 'error', 'url': url, 'message': str(e)})}\n\n"
            
            matches.append(CompetitorMatch(
                url=url,
                score=0,
                keywords_found=[],
                title=f"Error: {url}",
                description=f"Analysis failed: {str(e)}"
            ))
    
    # Sort by score
    matches.sort(key=lambda x: x.score, reverse=True)
    
    # Calculate summary
    total_competitors = len(matches)
    average_score = sum(match.score for match in matches) / len(matches) if matches else 0
    
    direct_competitors = [m for m in matches if m.status['category'] == 'DIRECT']
    potential_competitors = [m for m in matches if m.status['category'] == 'POTENTIAL']
    non_competitors = [m for m in matches if m.status['category'] == 'NON_COMPETITOR']
    
    report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
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
