"""
🤖 API Endpoint per AI Site Summary
Endpoint per generare riassunti automatici dei siti clienti
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, List
import logging
import time

# Import del nuovo analyzer
from core.ai_site_analyzer import ai_analyzer

logger = logging.getLogger(__name__)

router = APIRouter()

class SiteSummaryRequest(BaseModel):
    """Request model per l'analisi AI del sito"""
    url: HttpUrl
    detailed_analysis: bool = False  # Per analisi più approfondite in futuro

class SiteSummaryResponse(BaseModel):
    """Response model per il riassunto AI"""
    url: str
    business_description: str
    industry_sector: str
    target_market: str
    key_services: List[str]
    confidence_score: float
    processing_time: float
    status: str

@router.post("/generate-site-summary")
async def generate_site_summary(request: SiteSummaryRequest) -> SiteSummaryResponse:
    """
    🤖 Genera riassunto automatico di un sito usando AI
    
    Questo endpoint:
    1. Scrape il contenuto del sito
    2. Usa OpenAI per generare un riassunto business
    3. Restituisce descrizione professionale del cliente
    
    Args:
        request: URL del sito da analizzare
        
    Returns:
        SiteSummaryResponse: Riassunto completo del business
    """
    
    logger.info(f"🎯 AI Summary request for: {request.url}")
    
    try:
        # Validazione URL
        url_str = str(request.url)
        if not url_str.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400, 
                detail="URL deve iniziare con http:// o https://"
            )
        
        # Analisi AI del sito
        summary = await ai_analyzer.analyze_site(url_str)
        
        # Validazione qualità risultato
        if summary.confidence_score < 0.3:
            logger.warning(f"⚠️ Low confidence summary for {url_str}: {summary.confidence_score}")
        
        # Costruzione risposta
        response = SiteSummaryResponse(
            url=summary.url,
            business_description=summary.business_description,
            industry_sector=summary.industry_sector,
            target_market=summary.target_market,
            key_services=summary.key_services,
            confidence_score=summary.confidence_score,
            processing_time=summary.processing_time,
            status="success"
        )
        
        logger.info(f"✅ AI Summary completed for {url_str}")
        logger.info(f"📊 Confidence: {summary.confidence_score:.2f}")
        logger.info(f"🏢 Sector: {summary.industry_sector}")
        
        return response
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"💥 AI Summary failed for {request.url}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Errore nell'analisi AI: {str(e)}"
        )

@router.get("/site-summary-test")
async def test_ai_summary():
    """
    🧪 Endpoint di test per verificare che l'AI analyzer funzioni
    """
    try:
        # Test con un sito semplice
        test_url = "https://www.flou.it"
        
        logger.info(f"🧪 Testing AI analyzer with: {test_url}")
        summary = await ai_analyzer.analyze_site(test_url)
        
        return {
            "status": "success",
            "test_url": test_url,
            "summary": {
                "business_description": summary.business_description,
                "industry_sector": summary.industry_sector,
                "confidence_score": summary.confidence_score,
                "processing_time": summary.processing_time
            },
            "message": "AI Analyzer is working correctly!"
        }
        
    except Exception as e:
        logger.error(f"💥 Test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "AI Analyzer test failed"
        }