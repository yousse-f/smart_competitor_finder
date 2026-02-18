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
    
    Soglie ottimizzate per ridurre falsi positivi:
    - DIRECT: >= 40% (competitor diretto stesso mercato)
    - POTENTIAL: >= 25% (da valutare - possibile overlap) 
    - NON_COMPETITOR: < 25% (settore completamente diverso)
    
    Note: Soglie più alte per evitare falsi positivi (es: noleggio auto vs IT)
    
    Returns:
        dict con category, label, color, priority
    """
    if score >= 40:  # 🔄 Manteniamo 40%
        return {
            "category": "DIRECT",
            "label": "Competitor Diretto",
            "label_en": "Direct Competitor",
            "color": "green",
            "emoji": "🟢",
            "priority": 1,
            "action": "Monitora attentamente"
        }
    elif score >= 25:  # 🔄 Aumentato da 20 a 25 (evita falsi positivi)
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
    def __init__(
        self, 
        url: str, 
        score: int, 
        keywords_found: List[str], 
        title: str = "", 
        description: str = "",
        # 🆕 Nuovi campi AI
        classification: str = "not_competitor",
        reason: str = "",
        ai_confidence: float = 0.0,
        competitor_description: str = "",
        competitor_sector: str = "",
        recommended_action: str = "",
        overlap_percentage: int = 0
    ):
        self.url = url
        self.score = score
        self.keywords_found = keywords_found
        self.title = title
        self.description = description
        # Aggiungi classificazione KPI automatica (mantiene compatibilità)
        self.status = classify_competitor_status(score)
        
        # 🆕 Nuovi campi AI per analisi avanzata
        self.classification = classification  # direct_competitor | potential_competitor | not_competitor
        self.reason = reason  # Spiegazione del perché
        self.ai_confidence = ai_confidence  # Confidence score AI (0.0-1.0)
        self.competitor_description = competitor_description  # Descrizione business competitor
        self.competitor_sector = competitor_sector  # Settore industriale competitor
        self.recommended_action = recommended_action  # Azione consigliata
        self.overlap_percentage = overlap_percentage  # Percentuale sovrapposizione mercato

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
    🎯 REFACTORED: Single source of truth - no double scraping.
    
    Pipeline:
    1. hybrid_scraper_v2.scrape_intelligent() → UNICA fonte di contenuto
    2. Usa full_text dal risultato scraping
    3. Ogni sito produce SEMPRE un risultato (success/partial/error)
    4. Nessun skip definitivo (no continue)
    """
    from core.hybrid_scraper_v2 import hybrid_scraper_v2
    from core.matching import keyword_matcher
    
    matches = []
    
    logging.info(f"🚀 Starting REFACTORED batch analysis for {len(urls)} competitors")
    logging.info(f"   Target keywords: {len(keywords)}")
    logging.info(f"   Pipeline: Single scraping source → deterministic results")
    
    for i, url in enumerate(urls):
        logging.info(f"📊 [{i+1}/{len(urls)}] Processing: {url}")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Scraping (UNICA SOURCE OF TRUTH)
        # ═══════════════════════════════════════════════════════════
        try:
            scrape_result = await hybrid_scraper_v2.scrape_intelligent(
                url, 
                max_keywords=50,  # 🔄 Aumentato per catturare più termini tecnici 
                use_advanced=True
            )
            
            scraping_status = scrape_result.get('status', 'unknown')
            full_text = scrape_result.get('full_text', '')
            content_length = scrape_result.get('content_length', 0)
            
            logging.info(f"   Scraping: {scraping_status} | Content: {content_length} chars | Method: {scrape_result.get('scraping_method', 'unknown')}")
            
        except Exception as scraping_error:
            logging.error(f"   ❌ Scraping exception: {scraping_error}")
            scrape_result = {
                'status': 'error',
                'error': str(scraping_error),
                'full_text': '',
                'title': '',
                'description': '',
                'content_length': 0
            }
            scraping_status = 'error'
            full_text = ''
            content_length = 0
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Validazione Contenuto (Guardrails)
        # ═══════════════════════════════════════════════════════════
        MIN_CONTENT_THRESHOLD = 500  # 500 caratteri minimi
        
        if scraping_status != 'success':
            # Scraping fallito completamente
            logging.warning(f"   ⚠️ Scraping failed: {scrape_result.get('error', 'Unknown error')}")
            matches.append(CompetitorMatch(
                url=url,
                score=0,
                keywords_found=[],
                title=f"❌ Scraping Failed",
                description=f"Error: {scrape_result.get('error', 'Unknown error')}"
            ))
            continue  # Prossimo sito
            
        elif content_length < MIN_CONTENT_THRESHOLD:
            # Contenuto insufficiente → status partial
            logging.warning(f"   ⚠️ Insufficient content: {content_length} < {MIN_CONTENT_THRESHOLD} chars")
            matches.append(CompetitorMatch(
                url=url,
                score=0,
                keywords_found=[],
                title=scrape_result.get('title', '❌ Insufficient Content'),
                description=f"Partial scraping: only {content_length} chars extracted"
            ))
            continue  # Prossimo sito
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: Matching (usa full_text dallo scraper)
        # ═══════════════════════════════════════════════════════════
        try:
            match_results = await keyword_matcher.calculate_match_score(
                target_keywords=keywords,
                site_content=full_text,  # ✅ SOURCE OF TRUTH
                business_context=None,
                site_title=scrape_result.get('title', ''),
                meta_description=scrape_result.get('description', ''),
                client_sector_data=None
            )
            
            score = int(match_results['match_score'])
            found_keywords = match_results['found_keywords']
            
            logging.info(f"   ✅ Matching: {score}% | Keywords: {len(found_keywords)}")
            logging.info(f"      Quality: {match_results.get('score_details', {}).get('quality_flag', 'N/A')}")
            
            matches.append(CompetitorMatch(
                url=url,
                score=score,
                keywords_found=found_keywords,
                title=scrape_result.get('title', ''),
                description=scrape_result.get('description', '')
            ))
            
        except Exception as matching_error:
            logging.error(f"   ❌ Matching exception: {matching_error}")
            matches.append(CompetitorMatch(
                url=url,
                score=0,
                keywords_found=[],
                title=scrape_result.get('title', '❌ Matching Failed'),
                description=f"Scraping OK, Matching error: {str(matching_error)}"
            ))
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x.score, reverse=True)
    
    logging.info(f"🎉 Batch analysis complete:")
    logging.info(f"   Total sites: {len(urls)}")
    logging.info(f"   Results: {len(matches)}")
    logging.info(f"   Success rate: {len([m for m in matches if m.score > 0])}/{len(urls)} ({len([m for m in matches if m.score > 0])/len(urls)*100:.1f}%)")
    
    return matches