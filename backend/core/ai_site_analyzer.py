"""
🤖 AI Site Analyzer - Generazione automatica riassunti business
Sistema per creare presentazioni automatiche dei siti clienti usando OpenAI
"""

import openai
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import os
from .hybrid_scraper_v2 import HybridScraperV2
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

@dataclass
class SiteSummary:
    """Risultato dell'analisi AI del sito"""
    url: str
    business_description: str
    industry_sector: str
    target_market: str
    key_services: list
    confidence_score: float
    processing_time: float

class AISiteAnalyzer:
    """🤖 Analizzatore AI per generare riassunti business automatici"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY non configurata nell'environment")
        
        # Configura OpenAI client
        openai.api_key = self.openai_api_key
        self.scraper = HybridScraperV2()
        
        # Template prompt per l'analisi business
        self.analysis_prompt = """
Sei un esperto analista business. Analizza il contenuto del sito web fornito e crea un riassunto professionale.

CONTENUTO SITO:
{content}

ISTRUZIONI:
1. Identifica chiaramente di cosa si occupa questo business
2. Scrivi una descrizione di 2-3 frasi in italiano che spieghi:
   - Settore di attività
   - Prodotti/servizi principali  
   - Target di mercato
3. Identifica il settore industriale (es: "Arredamento", "Elettronica", "E-commerce")
4. Lista massimo 5 servizi/prodotti chiave

FORMATO RISPOSTA (JSON):
{{
    "business_description": "Descrizione 2-3 frasi in italiano",
    "industry_sector": "Settore industriale",
    "target_market": "Descrizione target clienti",
    "key_services": ["servizio1", "servizio2", "servizio3"],
    "confidence_score": 0.85
}}

REGOLE:
- Descrizione MASSIMO 3 frasi
- Linguaggio professionale ma comprensibile
- Focus su cosa fa il business, non su come lo fa
- Se il sito non è chiaro, confidence_score < 0.5
"""

    async def analyze_site(self, url: str) -> SiteSummary:
        """
        🔍 Analizza un sito e genera riassunto business automatico
        """
        import time
        start_time = time.time()
        
        logger.info(f"🤖 Starting AI analysis for: {url}")
        
        try:
            # 1. Scraping del contenuto (solo HTML, non keywords)
            logger.info("📡 Scraping site content...")
            
            # Usa il metodo _scrape_basic per ottenere contenuto HTML puro
            scraping_result = await self.scraper._scrape_basic(url)
            
            if not scraping_result.success or not scraping_result.content:
                raise ValueError(f"Failed to scrape content from {url}: {getattr(scraping_result, 'error', 'Unknown error')}")
            
            # 2. Pulizia e ottimizzazione del contenuto
            clean_content = self._clean_content_for_ai(scraping_result.content, url)
            
            # 3. Analisi AI con OpenAI
            logger.info("🤖 Generating AI business summary...")
            ai_response = await self._generate_ai_summary(clean_content)
            
            # 4. Parsing e validazione risposta
            summary_data = self._parse_ai_response(ai_response)
            
            processing_time = time.time() - start_time
            
            # 5. Creazione oggetto risultato
            summary = SiteSummary(
                url=url,
                business_description=summary_data.get('business_description', ''),
                industry_sector=summary_data.get('industry_sector', ''),
                target_market=summary_data.get('target_market', ''),
                key_services=summary_data.get('key_services', []),
                confidence_score=summary_data.get('confidence_score', 0.0),
                processing_time=processing_time
            )
            
            logger.info(f"✅ AI analysis completed in {processing_time:.2f}s")
            logger.info(f"📊 Confidence: {summary.confidence_score:.2f}")
            logger.info(f"🏢 Sector: {summary.industry_sector}")
            
            return summary
            
        except Exception as e:
            logger.error(f"💥 AI analysis failed for {url}: {e}")
            raise e

    def _clean_content_for_ai(self, html_content: str, url: str) -> str:
        """🧹 Pulisce e ottimizza il contenuto HTML per l'analisi AI"""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Rimuovi elementi non necessari
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Estrai testo significativo
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Contenuto principale
            main_content = soup.get_text()
            
            # Pulizia testo
            lines = (line.strip() for line in main_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk and len(chunk) > 3)
            
            # Limita lunghezza per OpenAI (max 4000 caratteri per essere sicuri)
            max_chars = 4000
            if len(clean_text) > max_chars:
                clean_text = clean_text[:max_chars] + "..."
            
            # Combina informazioni chiave
            content_summary = f"""
URL: {url}
TITLE: {title_text}
DESCRIPTION: {description}
CONTENT: {clean_text}
"""
            
            logger.info(f"🧹 Content cleaned: {len(content_summary)} characters")
            return content_summary.strip()
            
        except Exception as e:
            logger.error(f"💥 Content cleaning failed: {e}")
            return html_content[:2000]  # Fallback

    async def _generate_ai_summary(self, content: str) -> str:
        """🤖 Genera riassunto usando OpenAI GPT"""
        
        try:
            prompt = self.analysis_prompt.format(content=content)
            
            # Chiamata OpenAI (usando la nuova API client)
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sei un esperto analista business specializzato nell'analisi di siti web aziendali."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3,  # Bassa per risposte più consistenti
                response_format={"type": "json_object"}
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"🤖 OpenAI response length: {len(ai_response)} chars")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"💥 OpenAI API call failed: {e}")
            raise e

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """📋 Parsing e validazione della risposta AI"""
        
        try:
            import json
            data = json.loads(ai_response)
            
            # Validazione campi obbligatori
            required_fields = ['business_description', 'industry_sector', 'confidence_score']
            for field in required_fields:
                if field not in data:
                    logger.warning(f"⚠️ Missing field: {field}")
                    data[field] = "N/A" if field != 'confidence_score' else 0.0
            
            # Validazione lunghezza descrizione
            desc = data.get('business_description', '')
            if len(desc) > 500:
                logger.warning("⚠️ Description too long, truncating...")
                data['business_description'] = desc[:500] + "..."
            
            # Validazione confidence score
            confidence = data.get('confidence_score', 0.0)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                logger.warning(f"⚠️ Invalid confidence score: {confidence}")
                data['confidence_score'] = 0.5
            
            # Validazione key_services
            services = data.get('key_services', [])
            if not isinstance(services, list):
                data['key_services'] = []
            elif len(services) > 5:
                data['key_services'] = services[:5]
            
            logger.info("✅ AI response validated successfully")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"💥 JSON parsing failed: {e}")
            # Fallback response
            return {
                'business_description': 'Analisi automatica non disponibile per questo sito.',
                'industry_sector': 'Non identificato',
                'target_market': 'Non specificato',
                'key_services': [],
                'confidence_score': 0.1
            }
        except Exception as e:
            logger.error(f"💥 Response parsing failed: {e}")
            raise e

# Global instance
ai_analyzer = AISiteAnalyzer()