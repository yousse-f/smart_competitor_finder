"""
🤖 AI Competitor Comparator - Confronto intelligente tra cliente e competitor
Sistema per confrontare due business usando OpenAI e classificare il livello di competizione
"""

import openai
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class ComparisonResult:
    """Risultato del confronto tra cliente e competitor"""
    classification: str  # "direct_competitor" | "potential_competitor" | "not_competitor"
    reason: str  # Spiegazione chiara in 2-3 frasi
    confidence: float  # 0.0-1.0
    overlap_percentage: int  # 0-100
    key_differences: list  # Lista differenze principali
    key_similarities: list  # Lista somiglianze principali
    recommended_action: str  # Azione consigliata basata su classification

class AICompetitorComparator:
    """🤖 Comparatore AI per analisi competitor"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY non configurata nell'environment")
        
        openai.api_key = self.openai_api_key
        
        # Template prompt per il confronto
        self.comparison_prompt = """
Sei un esperto analista di mercato. Confronta due business e determina se sono competitor diretti, potenziali competitor, o non competitor.

BUSINESS CLIENTE:
Descrizione: {client_description}
Settore: {client_sector}
Target: {client_target}
Servizi Chiave: {client_services}

BUSINESS COMPETITOR:
Descrizione: {competitor_description}
Settore: {competitor_sector}
Target: {competitor_target}
Servizi Chiave: {competitor_services}

CRITERI CLASSIFICAZIONE:

1. DIRETTO COMPETITOR (direct_competitor):
   - Stesso settore industriale specifico
   - Stesso target di mercato (B2B/B2C)
   - Prodotti/servizi sovrapponibili >70%
   - Esempio: Due aziende che producono UTA industriali per B2B

2. POTENZIALE COMPETITOR (potential_competitor):
   - Stesso settore MA target o prodotti parzialmente diversi
   - Sovrapposizione 30-70%
   - Potrebbero competere in futuro o su segmenti specifici
   - Esempio: UTA industriali vs Climatizzatori commerciali

3. NON COMPETITOR (not_competitor):
   - Settore industriale completamente diverso
   - Target di mercato incompatibile
   - Zero o minima sovrapposizione prodotti (<30%)
   - Esempio: UTA industriali vs Ventilatori domestici

ANALISI RICHIESTA:
1. Confronta SETTORE: sono nello stesso mercato industriale?
2. Confronta TARGET: servono gli stessi clienti (dimensione, tipo)?
3. Confronta PRODOTTI/SERVIZI: quanto si sovrappongono?
4. Calcola OVERLAP PERCENTAGE realistico (0-100%)
5. Identifica DIFFERENZE CHIAVE (max 3, concrete e specifiche)
6. Identifica SOMIGLIANZE CHIAVE (max 3, concrete e specifiche)

FORMATO RISPOSTA (JSON PURO):
{{
    "classification": "direct_competitor" | "potential_competitor" | "not_competitor",
    "reason": "Spiegazione chiara in 2-3 frasi del perché. Menziona settore, target e overlap prodotti.",
    "confidence": 0.95,
    "overlap_percentage": 85,
    "key_differences": ["Differenza 1 specifica", "Differenza 2 specifica", "Differenza 3 specifica"],
    "key_similarities": ["Somiglianza 1 specifica", "Somiglianza 2 specifica", "Somiglianza 3 specifica"]
}}

REGOLE:
- Reason DEVE essere comprensibile a non-tecnici
- Focus su BUSINESS IMPACT, non solo keyword matching
- Confidence basso (<0.5) se descrizioni poco chiare o ambigue
- Differenze e somiglianze devono essere CONCRETE (non "prodotti diversi" ma "UTA industriali vs ventilatori domestici")
- Overlap percentage deve riflettere la reale sovrapposizione di mercato
"""

    async def compare_competitors(
        self,
        client_summary: Dict[str, Any],
        competitor_summary: Dict[str, Any]
    ) -> ComparisonResult:
        """
        🔍 Confronta cliente e competitor usando OpenAI
        
        Args:
            client_summary: Summary AI del cliente (da ai_site_analyzer)
            competitor_summary: Summary AI del competitor (da ai_site_analyzer)
            
        Returns:
            ComparisonResult con classificazione e dettagli
        """
        logger.info(f"🤖 Starting AI comparison analysis")
        
        try:
            # Prepara i dati per il prompt
            client_services = ", ".join(client_summary.get('key_services', []))
            competitor_services = ", ".join(competitor_summary.get('key_services', []))
            
            prompt = self.comparison_prompt.format(
                client_description=client_summary.get('business_description', ''),
                client_sector=client_summary.get('industry_sector', ''),
                client_target=client_summary.get('target_market', ''),
                client_services=client_services,
                competitor_description=competitor_summary.get('business_description', ''),
                competitor_sector=competitor_summary.get('industry_sector', ''),
                competitor_target=competitor_summary.get('target_market', ''),
                competitor_services=competitor_services
            )
            
            # Chiamata OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sei un esperto analista di mercato specializzato nel confronto competitivo tra business."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3,  # Bassa per risposte consistenti
                response_format={"type": "json_object"}
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"🤖 OpenAI comparison response length: {len(ai_response)} chars")
            
            # Parsing risposta
            comparison_data = json.loads(ai_response)
            
            # Validazione e creazione risultato
            classification = comparison_data.get('classification', 'not_competitor')
            reason = comparison_data.get('reason', 'Analisi non disponibile')
            confidence = float(comparison_data.get('confidence', 0.5))
            overlap = int(comparison_data.get('overlap_percentage', 0))
            
            # Mappa classification a recommended_action
            action_map = {
                'direct_competitor': '🔴 Monitorare attentamente: prezzi, offerte, comunicazione',
                'potential_competitor': '🟡 Tenere d\'occhio: potenziale evoluzione verso competizione diretta',
                'not_competitor': '🟢 Ignorare: target e mercato completamente diversi'
            }
            recommended_action = action_map.get(classification, 'Valutare caso per caso')
            
            result = ComparisonResult(
                classification=classification,
                reason=reason,
                confidence=confidence,
                overlap_percentage=overlap,
                key_differences=comparison_data.get('key_differences', []),
                key_similarities=comparison_data.get('key_similarities', []),
                recommended_action=recommended_action
            )
            
            logger.info(f"✅ Comparison complete: {classification} (confidence: {confidence:.2f})")
            logger.info(f"📊 Overlap: {overlap}%")
            logger.info(f"💡 Reason: {reason[:100]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"💥 AI comparison failed: {e}")
            # Fallback response
            return ComparisonResult(
                classification='not_competitor',
                reason='Impossibile confrontare i due business per errore tecnico.',
                confidence=0.0,
                overlap_percentage=0,
                key_differences=['Analisi non disponibile'],
                key_similarities=[],
                recommended_action='⚠️ Valutare manualmente'
            )

# Global instance
ai_comparator = AICompetitorComparator()
