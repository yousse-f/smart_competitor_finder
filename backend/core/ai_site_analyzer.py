"""
🤖 AI Site Analyzer - Generazione automatica riassunti business
Sistema per creare presentazioni automatiche dei siti clienti usando OpenAI
"""

import openai
import logging
from typing import Dict, Any, Optional, List
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
        
        # Template prompt OTTIMIZZATO per l'analisi business
        # 🎯 Prompt progettato per dati strutturati, non HTML grezzo
        self.analysis_prompt = """
Sei un esperto analista business specializzato nella classificazione di siti web aziendali.

Ti verrà fornito un estratto STRUTTURATO di un sito web con:
- TITLE (titolo pagina)
- DESCRIZIONE (meta description)
- KEYWORDS PRINCIPALI (parole chiave estratte)
- SEZIONI PRINCIPALI (headers H1/H2/H3)

DATI STRUTTURATI DEL SITO:
{content}

ISTRUZIONI:
1. Analizza attentamente TITLE e KEYWORDS per identificare il settore
2. Usa DESCRIZIONE e SEZIONI per confermare l'area business
3. Classifica il settore con PRECISIONE:
   - "Tecnologia dell'Informazione e Software" → per software house, web agency, sviluppo app, IT services, ERP
   - "Consulenza e Servizi Professionali" → per consulenza strategica, business advisory
   - "Design e Comunicazione" → per agenzie creative, graphic design, marketing
   - "Produzione Industriale" → per manifattura, carpenteria, metalworking
   - "Edilizia e Costruzioni" → per costruzioni, ristrutturazioni, real estate
   - "Commercio e Retail" → per e-commerce, vendita al dettaglio
   - "Altri Servizi" → per settori non classificabili sopra

4. Scrivi una descrizione chiara di 2-3 frasi che riassuma:
   - Cosa fa l'azienda
   - Settore specifico di attività  
   - Target clienti principali

5. Elenca 3-5 servizi/prodotti principali trovati nei dati

FORMATO RISPOSTA (JSON):
{{
    "business_description": "Descrizione chiara di 2-3 frasi basata sui dati strutturati",
    "industry_sector": "Settore preciso tra quelli elencati sopra",
    "target_market": "Target clienti identificato",
    "key_services": ["servizio_1", "servizio_2", "servizio_3"],
    "confidence_score": 0.90
}}

REGOLE:
- Usa le KEYWORDS per identificare il settore (es: 'software', 'ERP', 'development' → IT)
- Descrizione MAX 3 frasi, linguaggio professionale
- Se dati insufficienti, confidence_score < 0.5
- PRIORITÀ: classificazione accurata del settore
"""

    async def analyze_site(self, url: str) -> SiteSummary:
        """
        🔍 Analizza un sito e genera riassunto business automatico
        """
        import time
        start_time = time.time()
        
        logger.info(f"🤖 Starting AI analysis for: {url}")
        
        try:
            # 1. Scraping del contenuto con FALLBACK INTELLIGENTE
            logger.info("📡 Scraping site content...")
            
            # Step 1: Try fast basic HTTP first
            scraping_result = await self.scraper._scrape_basic(url)
            content = None
            scraping_method = "unknown"
            
            if scraping_result.success and scraping_result.content:
                content = scraping_result.content
                scraping_method = "basic_http"
                logger.info(f"✅ Basic HTTP returned {len(content)} characters")
                
                # Check if content is sufficient (HTTP 202 might return incomplete content)
                if len(content) < 1000:
                    logger.warning(f"⚠️ Content too short ({len(content)} chars), trying Browser Pool fallback...")
                    content = None  # Force fallback
            
            # Step 2: Fallback to Browser Pool if basic failed or content insufficient
            if not content:
                logger.info("🔄 Using Browser Pool fallback for better content...")
                from core.browser_pool import browser_pool
                
                try:
                    session = await browser_pool.get_session()
                    html_content = await browser_pool.scrape_with_session(session, url)
                    
                    if html_content and len(html_content) > 1000:
                        content = html_content
                        scraping_method = "browser_pool"
                        logger.info(f"✅ Browser Pool returned {len(content)} characters")
                    else:
                        raise ValueError(f"Browser Pool returned insufficient content: {len(html_content) if html_content else 0} chars")
                except Exception as pool_error:
                    logger.error(f"❌ Browser Pool fallback failed: {pool_error}")
                    raise ValueError(f"All scraping methods failed for {url}")
            
            # Final validation
            if not content or len(content) < 500:
                raise ValueError(f"Insufficient content from {url}: only {len(content) if content else 0} characters")
            
            logger.info(f"📊 Final content: {len(content)} chars via {scraping_method}")
            
            # 2. Pulizia e ottimizzazione del contenuto
            clean_content = self._clean_content_for_ai(content, url)
            
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
    
    async def analyze_site_from_content(
        self, 
        site_content: str, 
        site_title: str = "", 
        meta_description: str = ""
    ) -> SiteSummary:
        """
        🎯 HYBRID MODE: Analyze site from already-scraped content (no re-scraping).
        Used for validation when keyword-based classification has low confidence.
        
        Args:
            site_content: Already scraped HTML/text content
            site_title: Page title
            meta_description: Meta description
            
        Returns:
            SiteSummary with AI classification
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"🤖 AI validation mode - analyzing from pre-scraped content")
            
            # 1. Use already scraped content (skip scraping step)
            if not site_content or len(site_content) < 500:
                raise ValueError(f"Insufficient content for AI analysis: {len(site_content)} chars")
            
            # 2. Clean and prepare content using optimized structured extraction
            clean_content = self._clean_content_for_ai_from_text(
                site_content, site_title, meta_description
            )
            
            # 3. AI analysis with OpenAI
            logger.info("🤖 Running OpenAI classification...")
            ai_response = await self._generate_ai_summary(clean_content)
            
            # 4. Parse and validate response
            summary_data = self._parse_ai_response(ai_response)
            
            processing_time = time.time() - start_time
            
            # 5. Create result object (with fake URL since we're analyzing content)
            summary = SiteSummary(
                url="validation",  # Placeholder
                business_description=summary_data.get('business_description', ''),
                industry_sector=summary_data.get('industry_sector', ''),
                target_market=summary_data.get('target_market', ''),
                key_services=summary_data.get('key_services', []),
                confidence_score=summary_data.get('confidence_score', 0.0),
                processing_time=processing_time
            )
            
            logger.info(f"✅ AI validation completed in {processing_time:.2f}s")
            logger.info(f"🏢 AI Sector: {summary.industry_sector} (confidence: {summary.confidence_score:.2f})")
            
            return summary
            
        except Exception as e:
            logger.error(f"💥 AI validation failed: {e}")
            raise e
    
    def _clean_content_for_ai_from_text(
        self, 
        text_content: str, 
        title: str = "", 
        description: str = ""
    ) -> str:
        """
        🧹 Extract structured data from plain text (for hybrid validation mode).
        Similar to _clean_content_for_ai but works with plain text instead of HTML.
        """
        try:
            # Extract keywords from text
            from core.keyword_extraction import _extractor
            keywords_list = _extractor._process_text(text_content)[:15]
            keywords_text = ", ".join(keywords_list) if keywords_list else ""
            
            # Extract main topics (simple sentence extraction)
            sentences = [s.strip() for s in text_content.split('.') if len(s.strip()) > 50]
            main_topics = " | ".join(sentences[:3])  # First 3 meaningful sentences
            
            # Build structured format for OpenAI
            structured_content = f"""ANALISI SITO WEB

TITLE: {title}

DESCRIZIONE: {description}

KEYWORDS PRINCIPALI: {keywords_text}

CONTENUTO PRINCIPALE: {main_topics}
"""
            
            logger.info(f"✅ Extracted structured data: title={len(title)} chars, keywords={len(keywords_list)}")
            return structured_content.strip()
            
        except Exception as e:
            logger.error(f"💥 Content structuring failed: {e}")
            # Fallback: use first 1000 chars
            return f"TITLE: {title}\nDESCRIZIONE: {description}\nCONTENUTO: {text_content[:1000]}"
    
    async def analyze_sites_batch(
        self, 
        sites_data: List[Dict[str, str]],
        batch_size: int = 5
    ) -> List[Dict[str, Any]]:
        """
        🚀 BATCH ANALYSIS: Analizza più siti in una singola chiamata API OpenAI
        
        Ottimizzazione costi: invece di N chiamate (1 per sito), fa N/batch_size chiamate
        Esempio: 100 siti con batch_size=5 → 20 chiamate invece di 100 (risparmio 80%!)
        
        Args:
            sites_data: Lista di dict con {content, title, description, url}
            batch_size: Numero di siti per batch (default 5, max 10)
            
        Returns:
            Lista di dict con {url, sector, confidence, description}
        """
        import time
        start_time = time.time()
        
        logger.info(f"🚀 Batch analysis: {len(sites_data)} siti, batch_size={batch_size}")
        
        # Limita batch size per evitare overflow token OpenAI
        batch_size = min(batch_size, 10)  # Max 10 siti per batch
        
        all_results = []
        total_api_calls = 0
        
        # Dividi siti in batch
        for i in range(0, len(sites_data), batch_size):
            batch = sites_data[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(sites_data) + batch_size - 1) // batch_size
            
            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} siti)")
            
            try:
                # Prepara contenuto strutturato per ogni sito nel batch
                batch_content = self._prepare_batch_content(batch)
                
                # 1 chiamata API per tutto il batch
                batch_results = await self._analyze_batch_with_openai(batch_content, batch)
                total_api_calls += 1
                
                all_results.extend(batch_results)
                logger.info(f"✅ Batch {batch_num} completato: {len(batch_results)} siti classificati")
                
            except Exception as e:
                logger.error(f"❌ Batch {batch_num} failed: {e}")
                # Fallback: risultati vuoti per questo batch
                for site in batch:
                    all_results.append({
                        'url': site.get('url', 'unknown'),
                        'sector': 'unknown',
                        'confidence': 0.0,
                        'description': f'Batch analysis failed: {str(e)}',
                        'error': str(e)
                    })
        
        processing_time = time.time() - start_time
        
        logger.info(f"🎉 Batch analysis completata!")
        logger.info(f"   📊 Siti: {len(sites_data)}")
        logger.info(f"   🔥 API calls: {total_api_calls} (invece di {len(sites_data)})")
        logger.info(f"   💰 Risparmio: {((len(sites_data) - total_api_calls) / len(sites_data) * 100):.0f}%")
        logger.info(f"   ⏱️  Tempo: {processing_time:.2f}s")
        
        return all_results
    
    def _prepare_batch_content(self, batch: List[Dict]) -> str:
        """Prepara contenuto strutturato per analisi batch"""
        batch_text = "ANALISI BATCH MULTIPLA - Classifica il settore di ogni sito:\n\n"
        
        for idx, site in enumerate(batch, 1):
            content = site.get('content', '')
            title = site.get('title', '')
            description = site.get('description', '')
            
            # Estrai keywords
            from core.keyword_extraction import _extractor
            keywords = _extractor._process_text(content)[:10]
            keywords_text = ", ".join(keywords)
            
            batch_text += f"SITO #{idx}:\n"
            batch_text += f"URL: {site.get('url', 'N/A')}\n"
            batch_text += f"TITLE: {title}\n"
            batch_text += f"DESCRIZIONE: {description}\n"
            batch_text += f"KEYWORDS: {keywords_text}\n"
            batch_text += f"\n"
        
        return batch_text
    
    async def _analyze_batch_with_openai(
        self, 
        batch_content: str, 
        original_batch: List[Dict]
    ) -> List[Dict]:
        """Analizza batch con OpenAI e restituisce risultati per ogni sito"""
        
        prompt = f"""Sei un esperto analista di settori aziendali. 

Analizza OGNI sito nel batch e classifica il suo settore di appartenenza.

{batch_content}

SETTORI DISPONIBILI:
1. "Tecnologia e Software" → software house, IT, ERP, web agency, app, cybersecurity
2. "Consulenza" → business consulting, advisory, strategia
3. "Design e Comunicazione" → graphic design, marketing, branding
4. "Produzione Industriale" → manufacturing, carpenteria, metalworking
5. "Edilizia" → costruzioni, ristrutturazioni
6. "Commercio" → e-commerce, retail, vendita
7. "Servizi Professionali" → servizi generici, assistenza
8. "Automotive" → auto, veicoli, noleggio, fleet
9. "Altro" → settori non classificabili

Per OGNI sito, restituisci:
- Numero sito
- Settore identificato
- Livello confidence (0.0-1.0)
- Breve motivazione (1 frase)

FORMATO RISPOSTA (JSON array):
[
  {{
    "site_number": 1,
    "sector": "Tecnologia e Software",
    "confidence": 0.95,
    "reason": "Keywords: software, ERP, development indicano chiaramente IT"
  }},
  {{
    "site_number": 2,
    "sector": "Consulenza",
    "confidence": 0.80,
    "reason": "Focus su consulenza aziendale e advisory"
  }}
]

IMPORTANTE: Restituisci ESATTAMENTE {len(original_batch)} risultati, uno per ogni sito nel batch."""

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sei un esperto classificatore di settori aziendali. Analizza batch di siti e identifica il settore di ognuno."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,  # Maggiore per batch analysis
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"🤖 OpenAI batch response: {len(ai_response)} chars")
            
            # Parse risposta
            import json
            parsed = json.loads(ai_response)
            
            # Estrai array risultati
            if isinstance(parsed, dict) and 'results' in parsed:
                results_array = parsed['results']
            elif isinstance(parsed, list):
                results_array = parsed
            else:
                raise ValueError(f"Unexpected response format: {type(parsed)}")
            
            # Mappa risultati ai siti originali
            final_results = []
            for idx, site in enumerate(original_batch):
                # Trova risultato corrispondente
                site_result = next(
                    (r for r in results_array if r.get('site_number') == idx + 1),
                    None
                )
                
                if site_result:
                    # Mappa settore AI a codice interno
                    sector_code = self._map_ai_sector_to_code(site_result.get('sector', 'unknown'))
                    
                    final_results.append({
                        'url': site.get('url', 'unknown'),
                        'sector': sector_code,
                        'sector_name': site_result.get('sector', 'unknown'),
                        'confidence': site_result.get('confidence', 0.5),
                        'reason': site_result.get('reason', ''),
                        'ai_batch_analyzed': True
                    })
                else:
                    # Fallback se manca risultato
                    logger.warning(f"Missing result for site #{idx+1}")
                    final_results.append({
                        'url': site.get('url', 'unknown'),
                        'sector': 'unknown',
                        'confidence': 0.0,
                        'reason': 'Result not found in batch response'
                    })
            
            return final_results
            
        except Exception as e:
            logger.error(f"Batch OpenAI analysis failed: {e}")
            raise e
    
    def _map_ai_sector_to_code(self, ai_sector_name: str) -> str:
        """Map AI sector name to internal code"""
        sector_lower = ai_sector_name.lower()
        
        if any(word in sector_lower for word in ['tecnologia', 'software', 'informazione', 'it', 'digital']):
            return 'digital_tech'
        elif any(word in sector_lower for word in ['consulenza', 'consulting']):
            return 'consulting'
        elif any(word in sector_lower for word in ['design', 'comunicazione', 'marketing']):
            return 'services'
        elif any(word in sector_lower for word in ['produzione', 'manufacturing', 'industriale']):
            return 'manufacturing'
        elif any(word in sector_lower for word in ['edilizia', 'costruzioni']):
            return 'construction'
        elif any(word in sector_lower for word in ['commercio', 'retail', 'e-commerce']):
            return 'services'
        elif any(word in sector_lower for word in ['automotive', 'auto']):
            return 'automotive'
        else:
            return 'services'

    def _clean_content_for_ai(self, html_content: str, url: str) -> str:
        """🧹 Estrae dati strutturati dall'HTML per analisi AI ad alta precisione
        
        🎯 STRATEGIA VINCENTE (100% accuratezza nei test):
        Invece di inviare HTML grezzo che confonde OpenAI, estraiamo SOLO i dati
        strutturati significativi: title, keywords, headers, servizi.
        Questo permette a OpenAI di classificare correttamente il settore.
        """
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Rimuovi elementi non necessari
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            # 1. TITLE - peso massimo nella classificazione
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # 2. META DESCRIPTION - contesto business
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # 3. KEYWORDS META TAG (se presente)
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            meta_keywords_text = meta_keywords.get('content', '').strip() if meta_keywords else ""
            
            # 4. HEADERS (H1, H2, H3) - struttura contenuto
            headers = []
            for h in soup.find_all(['h1', 'h2', 'h3']):
                header_text = h.get_text().strip()
                if header_text and len(header_text) > 3 and len(header_text) < 150:
                    headers.append(header_text)
            headers_text = " | ".join(headers[:5])  # Top 5 headers più rilevanti
            
            # 5. ESTRAZIONE KEYWORDS DAL CONTENUTO
            main_content = soup.get_text()
            
            # Pulizia testo per estrazione keywords
            lines = (line.strip() for line in main_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk and len(chunk) > 3)
            
            # Estrai top keywords usando keyword_extraction
            from core.keyword_extraction import _extractor
            keywords_list = _extractor._process_text(clean_text)[:15]  # Top 15 keywords
            keywords_text = ", ".join(keywords_list) if keywords_list else ""
            
            # 6. STRUTTURA OTTIMIZZATA PER OPENAI
            # Formato compatto e chiaro - massima precisione di classificazione
            structured_content = f"""ANALISI SITO WEB

URL: {url}

TITLE: {title_text}

DESCRIZIONE: {description}

KEYWORDS PRINCIPALI: {keywords_text}

SEZIONI PRINCIPALI: {headers_text}
"""
            
            # 7. Aggiungi snippet di contenuto SOLO se mancano altri dati
            if len(title_text) < 10 and len(description) < 20:
                # Fallback: aggiungi primo paragrafo significativo
                paragraphs = soup.find_all('p')
                first_meaningful = ""
                for p in paragraphs[:5]:
                    text = p.get_text().strip()
                    if len(text) > 50:
                        first_meaningful = text[:300]
                        break
                if first_meaningful:
                    structured_content += f"\nCONTENUTO: {first_meaningful}..."
            
            logger.info(f"✅ Estratto strutturato: title={len(title_text)} chars, keywords={len(keywords_list)}, headers={len(headers)}")
            return structured_content.strip()
            
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
    
    async def compare_competitors(
        self,
        client_summary: SiteSummary,
        competitor_summary: SiteSummary
    ):
        """
        🔍 Confronta cliente e competitor usando AI comparator
        
        Args:
            client_summary: Summary AI del sito cliente
            competitor_summary: Summary AI del sito competitor
            
        Returns:
            ComparisonResult con classification, reason, confidence, etc.
        """
        from core.ai_competitor_comparator import ai_comparator
        
        # Converte SiteSummary in dict per il comparator
        client_dict = {
            'business_description': client_summary.business_description,
            'industry_sector': client_summary.industry_sector,
            'target_market': client_summary.target_market,
            'key_services': client_summary.key_services
        }
        
        competitor_dict = {
            'business_description': competitor_summary.business_description,
            'industry_sector': competitor_summary.industry_sector,
            'target_market': competitor_summary.target_market,
            'key_services': competitor_summary.key_services
        }
        
        # Chiama il comparator
        comparison_result = await ai_comparator.compare_competitors(
            client_dict,
            competitor_dict
        )
        
        return comparison_result

# Global instance
ai_analyzer = AISiteAnalyzer()


# ============================================================
# 🎯 NUOVA FUNZIONE STANDALONE — sostituisce tutto il vecchio sistema ibrido
# ============================================================

async def classify_competitor_with_ai(
    client_keywords: list,
    competitor_content: str,
    competitor_url: str
) -> dict:
    """
    🎯 Unica funzione di classificazione competitor.
    
    Sostituisce sector_classifier + semantic_filter + validate_and_blend_scores.
    Una sola chiamata gpt-4o-mini per competitor: più veloce, più consistente.
    
    Returns:
        dict con: classification, score (0-100), reason, competitor_sector
    """
    import json as _json
    from openai import AsyncOpenAI

    openai_api_key = os.getenv('OPENAI_API_KEY')
    _client = AsyncOpenAI(api_key=openai_api_key)

    content_preview = competitor_content[:6000] if competitor_content else "(contenuto non disponibile)"

    prompt = f"""Sei un analista di business. Analizza se questo sito è un competitor del nostro cliente.

KEYWORD DEL CLIENTE (servizi che offre):
{', '.join(client_keywords)}

CONTENUTO SITO COMPETITOR ({competitor_url}):
{content_preview}

Rispondi ESCLUSIVAMENTE con questo JSON (niente altro):
{{
  "classification": "direct_competitor",
  "score": 75,
  "reason": "Offre gli stessi servizi ERP per PMI",
  "competitor_sector": "Software gestionale"
}}

REGOLE:
- direct_competitor: offre gli STESSI servizi, stesso mercato → score 65-100
- potential_competitor: settore simile ma servizi diversi → score 30-64
- not_competitor: settore completamente diverso → score 0-29
"""

    try:
        response = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150
        )
        raw = response.choices[0].message.content.strip()
        # Rimuovi markdown code fences se presenti
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = _json.loads(raw)
        assert result['classification'] in ['direct_competitor', 'potential_competitor', 'not_competitor']
        assert 0 <= int(result['score']) <= 100
        result['score'] = int(result['score'])
        return result
    except Exception as e:
        logger.warning(f"⚠️ classify_competitor_with_ai fallback per {competitor_url}: {e}")
        return {
            "classification": "potential_competitor",
            "score": 30,
            "reason": "AI non disponibile — classificazione di default",
            "competitor_sector": "unknown"
        }