from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import pandas as pd
import logging
import io
from datetime import datetime

from core.keyword_extraction import extract_keywords_bulk

router = APIRouter()

def classify_competitor_status(score: float) -> dict:
    """
    Classifica competitor in base allo score con sistema KPI a 3 colori.
    
    Soglie aggiornate (Task 3):
    - DIRECT: >= 65% (era 60%)
    - POTENTIAL: >= 50% (era 40%)
    - NON_COMPETITOR: < 50%
    
    Returns:
        dict con category, label, color, priority
    """
    if score >= 65:  # 🔄 Aumentato da 60 a 65
        return {
            "category": "DIRECT",
            "label": "Competitor Diretto",
            "label_en": "Direct Competitor",
            "color": "green",
            "emoji": "🟢",
            "priority": 1,
            "action": "Monitora attentamente"
        }
    elif score >= 50:  # 🔄 Aumentato da 40 a 50
        return {
            "category": "POTENTIAL",
            "label": "Da Valutare",
            "label_en": "Potential Competitor",
            "color": "yellow",
            "emoji": "🟡",
            "priority": 2,
            "action": "Valuta caso per caso"
        }
    else:
        return {
            "category": "NON_COMPETITOR",
            "label": "Non Competitor",
            "label_en": "Not a Competitor",
            "color": "red",
            "emoji": "🔴",
            "priority": 3,
            "action": "Ignora"
        }

class CompetitorMatch:
    def __init__(self, url: str, score: int, keywords_found: List[str], title: str = "", description: str = ""):
        self.url = url
        self.score = score
        self.keywords_found = keywords_found
        self.title = title
        self.description = description
        # Aggiungi classificazione KPI automatica
        self.status = classify_competitor_status(score)

@router.post("/upload-and-analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    keywords: str = Form(...)
):
    """
    Upload Excel/CSV file with competitor URLs and analyze them against keywords.
    
    Returns immediate results in the format expected by the frontend.
    """
    try:
        # Parse keywords from form data
        keywords_list = [k.strip() for k in keywords.replace('"', '').replace('[', '').replace(']', '').split(',')]
        
        logging.info(f"Starting bulk analysis with {len(keywords_list)} keywords")
        
        # Read the uploaded file
        contents = await file.read()
        
        # Determine file type and read accordingly
        urls = []
        try:
            if file.filename and file.filename.endswith('.csv'):
                # Read CSV
                df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
                # Extract URLs from first column
                first_column = df.iloc[:, 0].dropna()
                # Accept URLs with or without protocol
                for url in first_column:
                    url_str = str(url).strip()
                    if url_str and url_str.lower() not in ['nan', 'none', '']:
                        # Add https:// if missing protocol
                        if not url_str.startswith(('http://', 'https://')):
                            url_str = 'https://' + url_str
                        urls.append(url_str)
                
            elif file.filename and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
                # Read Excel
                df = pd.read_excel(io.BytesIO(contents))
                # Extract URLs from first column
                first_column = df.iloc[:, 0].dropna()
                # Accept URLs with or without protocol
                for url in first_column:
                    url_str = str(url).strip()
                    if url_str and url_str.lower() not in ['nan', 'none', '']:
                        # Add https:// if missing protocol
                        if not url_str.startswith(('http://', 'https://')):
                            url_str = 'https://' + url_str
                        urls.append(url_str)
                
            else:
                # Assume plain text with URLs separated by newlines
                text_content = contents.decode('utf-8')
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                # Accept URLs with or without protocol
                for line in lines:
                    if line and line.lower() not in ['nan', 'none', '']:
                        # Add https:// if missing protocol
                        if not line.startswith(('http://', 'https://')):
                            line = 'https://' + line
                        urls.append(line)
                
        except Exception as file_error:
            # Fallback: try to parse as plain text
            try:
                text_content = contents.decode('utf-8')
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                # Accept URLs with or without protocol
                for line in lines:
                    if line and line.lower() not in ['nan', 'none', '']:
                        # Add https:// if missing protocol
                        if not line.startswith(('http://', 'https://')):
                            line = 'https://' + line
                        urls.append(line)
            except Exception as text_error:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to parse file. Supported formats: CSV, Excel, or plain text with URLs. Error: {str(file_error)}"
                )
        
        logging.info(f"Extracted {len(urls)} URLs from file: {file.filename}")
        
        if not urls:
            raise HTTPException(status_code=400, detail="No valid URLs found in the file")
        
        # Perform bulk analysis (simplified version)
        matches = await analyze_competitors_bulk(urls, keywords_list)
        
        # Calculate summary statistics
        total_competitors = len(matches)
        average_score = sum(match.score for match in matches) / len(matches) if matches else 0
        
        # Calcola statistiche per categoria KPI
        direct_competitors = [m for m in matches if m.status['category'] == 'DIRECT']
        potential_competitors = [m for m in matches if m.status['category'] == 'POTENTIAL']
        non_competitors = [m for m in matches if m.status['category'] == 'NON_COMPETITOR']
        
        # Generate report ID
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Format response for frontend con classificazione KPI
        response = {
            "status": "success",
            "total_competitors": total_competitors,
            "matches": [
                {
                    "url": match.url,
                    "score": match.score,
                    "keywords_found": match.keywords_found,
                    "title": match.title,
                    "description": match.description,
                    "competitor_status": match.status  # 🆕 Aggiungi status KPI
                }
                for match in matches
            ],
            "average_score": round(average_score, 1),
            "report_id": report_id,
            "message": f"Analyzed {total_competitors} competitors successfully",
            # 🆕 Aggiungi summary per categoria
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
        
        logging.info(f"Bulk analysis completed: {total_competitors} competitors, avg score: {average_score:.1f}")
        
        return response
        
    except Exception as e:
        logging.error(f"Error in upload and analyze: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )

async def analyze_competitors_bulk(urls: List[str], keywords: List[str]) -> List[CompetitorMatch]:
    """
    🎯 REAL ANALYSIS with keyword quality weighting system.
    Uses the actual matching engine with semantic analysis and sector relevance.
    """
    from core.hybrid_scraper_v2 import hybrid_scraper_v2
    from core.matching import keyword_matcher
    from bs4 import BeautifulSoup
    import aiohttp
    import ssl
    
    matches = []
    
    # Process all URLs (no artificial limit)
    logging.info(f"🚀 Starting REAL analysis for {len(urls)} competitors with {len(keywords)} target keywords")
    
    for i, url in enumerate(urls):
        try:
            logging.info(f"📊 Processing {i+1}/{len(urls)}: {url}")
            
            # 1. Scrape competitor site content
            scrape_result = await hybrid_scraper_v2.scrape_intelligent(url, max_keywords=20, use_advanced=True)
            
            if not scrape_result.get('status') == 'success':
                logging.warning(f"⚠️ Scraping failed for {url}, skipping...")
                continue
            
            # Extract text content from scraping result
            # The scraper returns keywords as dicts, but we need the full text for matching
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
                            full_text = ' '.join(full_text.split())  # Clean whitespace
                        else:
                            full_text = ""
            except Exception as text_error:
                logging.warning(f"Could not extract full text from {url}: {text_error}")
                full_text = ""
            
            # 2. Calculate match score using REAL matching engine with quality weighting
            match_results = await keyword_matcher.calculate_match_score(
                target_keywords=keywords,
                site_content=full_text,
                business_context=None,
                site_title=scrape_result.get('title', ''),
                meta_description=scrape_result.get('description', ''),
                client_sector_data=None
            )
            
            # 3. Create match object with real data
            score = int(match_results['match_score'])
            found_keywords = match_results['found_keywords']
            
            matches.append(CompetitorMatch(
                url=url,
                score=score,
                keywords_found=found_keywords,
                title=scrape_result.get('title', ''),
                description=scrape_result.get('description', '')
            ))
            
            logging.info(f"✅ {url}: {score}% match ({len(found_keywords)} keywords found)")
            logging.info(f"   Quality breakdown: {match_results.get('score_details', {})}")
            
        except Exception as e:
            logging.error(f"❌ Error processing {url}: {str(e)}")
            # Add error entry
            matches.append(CompetitorMatch(
                url=url,
                score=0,
                keywords_found=[],
                title=f"Error analyzing {url}",
                description=f"Analysis failed: {str(e)}"
            ))
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x.score, reverse=True)
    
    logging.info(f"🎉 Analysis complete: {len(matches)}/{len(urls)} competitors successfully analyzed")
    
    return matches