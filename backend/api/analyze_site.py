from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal
import logging
import os
from datetime import datetime

from core.keyword_extraction import extract_keywords
from core.hybrid_scraper_v2 import hybrid_scraper_v2

router = APIRouter()

# 🎯 Helper function per messaggi user-friendly
def _get_user_friendly_error(error: str, url: str) -> dict:
    """Converte errori tecnici in messaggi comprensibili con azioni pratiche"""
    error_lower = error.lower()
    
    # WAF / Firewall (403)
    if '403' in error or 'waf' in error_lower or 'firewall' in error_lower:
        return {
            'message': f'🛡️ Il sito "{url}" ha una protezione anti-bot attiva che sta bloccando l\'accesso.',
            'suggestion': '💡 **Cosa puoi fare:**\n- Riprova tra 1-2 minuti (il sito ti "ricorderà")\n- Visita il sito manualmente nel browser prima di analizzarlo\n- Se il problema persiste, il sito potrebbe richiedere credenziali di accesso',
            'can_retry': True
        }
    
    # Timeout
    elif 'timeout' in error_lower or 'timed out' in error_lower:
        return {
            'message': f'⏱️ Il sito "{url}" impiega troppo tempo a rispondere.',
            'suggestion': '💡 **Cosa puoi fare:**\n- Verifica che il sito sia online (aprilo nel browser)\n- Riprova tra qualche minuto\n- Il sito potrebbe essere temporaneamente sovraccarico',
            'can_retry': True
        }
    
    # Connection refused / unreachable
    elif 'connection' in error_lower or 'unreachable' in error_lower or 'refused' in error_lower:
        return {
            'message': f'🔌 Impossibile connettersi a "{url}".',
            'suggestion': '💡 **Cosa puoi fare:**\n- Controlla che l\'URL sia corretto (es: https://www.esempio.com)\n- Verifica che il sito sia online\n- Potrebbe essere temporaneamente offline per manutenzione',
            'can_retry': True
        }
    
    # SSL/Certificate errors
    elif 'ssl' in error_lower or 'certificate' in error_lower:
        return {
            'message': f'🔒 Il certificato SSL di "{url}" ha dei problemi.',
            'suggestion': '💡 **Cosa puoi fare:**\n- Prova a cambiare "https://" in "http://"\n- Verifica che l\'URL sia corretto\n- Il sito potrebbe avere un certificato scaduto',
            'can_retry': True
        }
    
    # 404 Not Found
    elif '404' in error:
        return {
            'message': f'❌ La pagina "{url}" non esiste.',
            'suggestion': '💡 **Cosa puoi fare:**\n- Controlla che l\'URL sia corretto\n- Prova a rimuovere la parte finale dell\'URL (es: /it o /home)\n- Usa solo il dominio principale (es: https://www.esempio.com)',
            'can_retry': False
        }
    
    # Server errors (500, 502, 503)
    elif '500' in error or '502' in error or '503' in error:
        return {
            'message': f'⚠️ Il server di "{url}" ha un problema tecnico.',
            'suggestion': '💡 **Cosa puoi fare:**\n- Riprova tra 5-10 minuti\n- Il sito è temporaneamente fuori servizio\n- Contatta l\'amministratore del sito se il problema persiste',
            'can_retry': True
        }
    
    # Generic error
    else:
        return {
            'message': f'❌ Non è stato possibile analizzare "{url}".',
            'suggestion': '💡 **Cosa puoi fare:**\n- Verifica che l\'URL sia completo e corretto\n- Assicurati che il sito sia accessibile dal browser\n- Riprova tra qualche minuto\n- Se il problema persiste, contatta il supporto',
            'can_retry': True
        }

# Request/Response models
class AnalyzeSiteRequest(BaseModel):
    url: HttpUrl
    max_keywords: Optional[int] = 50  # 🔄 Aumentato per settore HVAC tecnico
    use_advanced_scraping: Optional[bool] = True
    bypass_cache: Optional[bool] = False  # 🆕 Forza re-scraping ignorando cache

class KeywordData(BaseModel):
    keyword: str
    frequency: int
    relevance: Literal["high", "medium", "low"]
    category: str

class AnalyzeSiteResponse(BaseModel):
    url: str
    keywords: List[KeywordData]
    total_keywords: int
    status: str
    title: str = ""
    description: str = ""
    content_length: Optional[int] = 0
    scraping_method: Optional[str] = "basic"
    performance_stats: Optional[dict] = None
    from_cache: Optional[bool] = False  # 🆕 Indica se proviene da cache

@router.post("/analyze-site", response_model=AnalyzeSiteResponse)
async def analyze_site(request: AnalyzeSiteRequest):
    """
    🚀 Analyze a website URL to extract relevant keywords using advanced self-hosted scraping.
    
    Features:
    - 100% self-hosted: Browser Pool → Advanced Scraper → Basic HTTP
    - Anti-bot detection bypass with Playwright stealth
    - Real-time performance stats
    - Intelligent keyword extraction and categorization
    """
    try:
        url_str = str(request.url)
        max_keywords = request.max_keywords or 50  # 🔄 Aumentato per HVAC
        
        logging.info(f"🎯 Starting analysis for URL: {url_str} (max_keywords: {max_keywords})")
        logging.info(f"🔧 Advanced scraping: {request.use_advanced_scraping}")
        logging.info(f"🌐 Scraping mode: {os.getenv('SCRAPING_MODE', 'development')}")
        
        if request.use_advanced_scraping:
            # 🚀 Use hybrid V2 ultra-stable scraper (con possibile bypass cache)
            result = await hybrid_scraper_v2.scrape_intelligent(
                url_str, 
                max_keywords, 
                use_advanced=True,
                bypass_cache=request.bypass_cache  # 🆕 Forza refresh se richiesto
            )
            
            # 🎯 Check if scraping failed and provide user-friendly message
            if result.get('status') == 'failed':
                error_msg = result.get('error', 'Unknown error')
                user_message = _get_user_friendly_error(error_msg, url_str)
                
                raise HTTPException(
                    status_code=422,  # Unprocessable Entity
                    detail={
                        'message': user_message['message'],
                        'suggestion': user_message['suggestion'],
                        'technical_error': error_msg,
                        'retry_recommended': user_message['can_retry']
                    }
                )
            
            # Format response from hybrid scraper result
            return AnalyzeSiteResponse(
                url=result['url'],
                keywords=result.get('keywords', []),
                total_keywords=result.get('total_keywords', 0),
                status=result.get('status', 'unknown'),
                title=result.get('title', ''),
                description=result.get('description', ''),
                content_length=result.get('content_length', 0),
                scraping_method=result.get('scraping_method', 'hybrid_v2'),
                performance_stats=await hybrid_scraper_v2.get_enhanced_stats(),
                from_cache=result.get('from_cache', False)  # 🆕 Debug cache status
            )
        else:
            # 📡 Use basic extraction (backwards compatibility)
            raw_keywords = await extract_keywords(url_str, max_keywords)
            
            # Convert to KeywordData format
            keywords_data = []
            for i, keyword in enumerate(raw_keywords):
                relevance = "high" if i < len(raw_keywords) // 3 else "medium" if i < 2 * len(raw_keywords) // 3 else "low"
                category = categorize_keyword(keyword)
                frequency = max(1, 20 - i)
                
                keywords_data.append(KeywordData(
                    keyword=keyword,
                    frequency=frequency,
                    relevance=relevance,
                    category=category
                ))
            
            return AnalyzeSiteResponse(
                url=url_str,
                keywords=keywords_data,
                total_keywords=len(keywords_data),
                status="success" if keywords_data else "no_content",
                title="",
                description="",
                scraping_method="basic"
            )
        
    except HTTPException:
        # Re-raise HTTPException (already formatted)
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "Errore sconosciuto durante l'analisi"
        logging.error(f"❌ Error analyzing site {request.url}: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante l'analisi del sito: {error_msg}"
        )

def categorize_keyword(keyword: str) -> str:
    """Categorizza una keyword basata sul contenuto"""
    keyword_lower = keyword.lower()
    
    # Categorie business
    business_terms = ["azienda", "società", "impresa", "business", "company"]
    service_terms = ["servizio", "consulenza", "assistenza", "supporto", "service"]
    product_terms = ["prodotto", "articolo", "materiale", "equipment", "strumento"]
    tech_terms = ["tecnologia", "digitale", "software", "sistema", "tech", "innovation"]
    industry_terms = ["industria", "industriale", "manifattura", "produzione", "manufacturing"]
    
    if any(term in keyword_lower for term in business_terms):
        return "business"
    elif any(term in keyword_lower for term in service_terms):
        return "servizi"
    elif any(term in keyword_lower for term in product_terms):
        return "prodotti"
    elif any(term in keyword_lower for term in tech_terms):
        return "tecnologia"
    elif any(term in keyword_lower for term in industry_terms):
        return "industria"
    else:
        return "generale"

@router.get("/scraping-stats")
async def get_scraping_stats():
    """
    📊 Endpoint per statistiche performance scraping V2
    """
    try:
        stats = await hybrid_scraper_v2.get_enhanced_stats()
        return {
            "performance_stats": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "operational",
            "version": "v2_ultra_stable"
        }
    except Exception as e:
        logging.error(f"Error getting scraping stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))