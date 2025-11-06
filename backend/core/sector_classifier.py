import asyncio
from typing import Dict, List, Tuple, Optional
import logging
from collections import Counter
import re

from core.semantic_filter import semantic_filter

logger = logging.getLogger(__name__)

class SectorClassifier:
    """Analyzes and classifies business sectors to detect false positives in competitor analysis."""
    
    def __init__(self):
        # Define sector keywords with weights
        self.sector_definitions = {
            'digital_tech': {
                'keywords': [
                    'digitale', 'digital', 'web', 'software', 'app', 'tecnologia', 'technology',
                    'informatica', 'computer', 'programmazione', 'sviluppo software', 'dev',
                    'sito web', 'website', 'e-commerce', 'online', 'internet', 'cyber',
                    'startup', 'innovation', 'tech', 'digital agency', 'web agency'
                ],
                'weight': 1.0
            },
            'ai_ml': {
                'keywords': [
                    'intelligenza artificiale', 'artificial intelligence', 'machine learning',
                    'ai', 'ml', 'deep learning', 'neural', 'algoritmi', 'automation',
                    'automazione', 'chatbot', 'nlp', 'computer vision', 'data science',
                    'analytics', 'big data', 'predittiva', 'predictive'
                ],
                'weight': 1.0
            },
            'manufacturing': {
                'keywords': [
                    'manifattura', 'manufacturing', 'produzione', 'production', 'fabbrica',
                    'factory', 'industriale', 'industrial', 'meccanica', 'mechanical',
                    'carpenteria', 'metallica', 'metalworking', 'lavorazione', 'processing',
                    'macchine', 'machinery', 'attrezzature', 'equipment', 'componenti'
                ],
                'weight': 1.0
            },
            'construction': {
                'keywords': [
                    'costruzioni', 'construction', 'edilizia', 'building', 'cemento',
                    'mattoni', 'brick', 'ristrutturazione', 'renovation', 'immobiliare',
                    'real estate', 'architettura', 'architecture', 'ingegneria civile',
                    'civil engineering', 'infrastrutture', 'infrastructure'
                ],
                'weight': 1.0
            },
            'office_supplies': {
                'keywords': [
                    'ufficio', 'office', 'forniture', 'supplies', 'cancelleria', 'stationery',
                    'scrivania', 'desk', 'sedie', 'chairs', 'arredamento ufficio',
                    'office furniture', 'stampanti', 'printers', 'carta', 'paper',
                    'penne', 'pens', 'materiali ufficio', 'office materials'
                ],
                'weight': 1.0
            },
            'consulting': {
                'keywords': [
                    'consulenza', 'consulting', 'advisory', 'strategia', 'strategy',
                    'business', 'management', 'gestione', 'organizzazione', 'organization',
                    'processi', 'processes', 'ottimizzazione', 'optimization',
                    'efficienza', 'efficiency', 'trasformazione', 'transformation'
                ],
                'weight': 0.8  # Lower weight as it's more generic
            },
            'services': {
                'keywords': [
                    'servizi', 'services', 'assistenza', 'support', 'manutenzione',
                    'maintenance', 'riparazione', 'repair', 'installazione', 'installation',
                    'supporto tecnico', 'technical support', 'help desk', 'customer service'
                ],
                'weight': 0.6  # Lower weight as it's very generic
            }
        }
        
        # Define sector compatibility matrix (how related sectors are)
        self.sector_compatibility = {
            'digital_tech': {'ai_ml': 0.9, 'consulting': 0.7, 'services': 0.6},
            'ai_ml': {'digital_tech': 0.9, 'consulting': 0.7, 'services': 0.6},
            'manufacturing': {'construction': 0.5, 'services': 0.4, 'consulting': 0.3},
            'construction': {'manufacturing': 0.5, 'services': 0.4, 'consulting': 0.3},
            'office_supplies': {'services': 0.6, 'consulting': 0.4},
            'consulting': {'digital_tech': 0.7, 'ai_ml': 0.7, 'services': 0.8},
            'services': {'consulting': 0.8, 'digital_tech': 0.6, 'ai_ml': 0.6}
        }
    
    async def analyze_sector(self, site_content: str, site_title: str = "", meta_description: str = "") -> Dict:
        """
        Analyze the sector/category of a website based on its content.
        
        Args:
            site_content: Full text content from the site
            site_title: Page title
            meta_description: Meta description
            
        Returns:
            Dictionary with sector analysis results
        """
        try:
            # Combine all content with weights
            combined_content = []
            if site_title:
                combined_content.extend([site_title.lower()] * 3)  # Title gets highest weight
            if meta_description:
                combined_content.extend([meta_description.lower()] * 2)  # Meta description gets medium weight
            combined_content.append(site_content.lower())  # Main content gets normal weight
            
            full_text = ' '.join(combined_content)
            
            # Calculate sector scores
            sector_scores = self._calculate_sector_scores(full_text)
            
            # Determine primary and secondary sectors
            primary_sector, confidence = self._determine_primary_sector(sector_scores)
            
            # Get semantic sector analysis using AI
            semantic_sector = await self._get_semantic_sector_analysis(site_title, meta_description, site_content[:1000])
            
            return {
                'primary_sector': primary_sector,
                'confidence': confidence,
                'sector_scores': sector_scores,
                'semantic_analysis': semantic_sector,
                'keywords_found': self._extract_sector_keywords(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error in sector analysis: {str(e)}")
            return {
                'primary_sector': 'unknown',
                'confidence': 0.0,
                'sector_scores': {},
                'semantic_analysis': 'unknown',
                'error': str(e)
            }
    
    def calculate_relevance_score(self, client_sector_data: Dict, competitor_sector_data: Dict) -> Dict:
        """
        Calculate how relevant a competitor is based on sector compatibility.
        
        Args:
            client_sector_data: Sector analysis of the client site
            competitor_sector_data: Sector analysis of the competitor site
            
        Returns:
            Dictionary with relevance analysis
        """
        try:
            client_sector = client_sector_data.get('primary_sector', 'unknown')
            competitor_sector = competitor_sector_data.get('primary_sector', 'unknown')
            
            if client_sector == 'unknown' or competitor_sector == 'unknown':
                return {
                    'relevance_score': 0.5,  # Neutral score when unknown
                    'relevance_label': 'partially_relevant',
                    'reason': 'Unknown sector classification'
                }
            
            # Direct sector match
            if client_sector == competitor_sector:
                return {
                    'relevance_score': 1.0,
                    'relevance_label': 'relevant',
                    'reason': f'Same sector: {client_sector}'
                }
            
            # Check sector compatibility
            compatibility = self._get_sector_compatibility(client_sector, competitor_sector)
            
            if compatibility >= 0.7:
                return {
                    'relevance_score': compatibility,
                    'relevance_label': 'relevant',
                    'reason': f'Compatible sectors: {client_sector} ↔ {competitor_sector}'
                }
            elif compatibility >= 0.4:
                return {
                    'relevance_score': compatibility,
                    'relevance_label': 'partially_relevant',
                    'reason': f'Partially compatible: {client_sector} ↔ {competitor_sector}'
                }
            else:
                return {
                    'relevance_score': max(0.1, compatibility),  # Minimum score
                    'relevance_label': 'irrelevant',
                    'reason': f'Incompatible sectors: {client_sector} vs {competitor_sector}'
                }
                
        except Exception as e:
            logger.error(f"Error calculating relevance: {str(e)}")
            return {
                'relevance_score': 0.5,
                'relevance_label': 'partially_relevant',
                'reason': f'Error in analysis: {str(e)}'
            }
    
    def _calculate_sector_scores(self, text: str) -> Dict[str, float]:
        """Calculate scores for each sector based on keyword matches."""
        sector_scores = {}
        
        for sector, definition in self.sector_definitions.items():
            score = 0.0
            keyword_matches = 0
            
            for keyword in definition['keywords']:
                # Count occurrences of this keyword
                count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text))
                if count > 0:
                    score += count * definition['weight']
                    keyword_matches += 1
            
            # Normalize by number of keywords in sector
            if keyword_matches > 0:
                sector_scores[sector] = score / len(definition['keywords'])
            else:
                sector_scores[sector] = 0.0
        
        return sector_scores
    
    def _determine_primary_sector(self, sector_scores: Dict[str, float]) -> Tuple[str, float]:
        """Determine the primary sector and confidence level."""
        if not sector_scores or all(score == 0 for score in sector_scores.values()):
            return 'unknown', 0.0
        
        # Find the sector with highest score
        primary_sector = max(sector_scores, key=sector_scores.get)
        max_score = sector_scores[primary_sector]
        
        # Calculate confidence based on score difference
        sorted_scores = sorted(sector_scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[1] > 0:
            confidence = min(1.0, max_score / (max_score + sorted_scores[1]))
        else:
            confidence = min(1.0, max_score / 10.0)  # Normalize against expected max
        
        return primary_sector, confidence
    
    def _get_sector_compatibility(self, sector1: str, sector2: str) -> float:
        """Get compatibility score between two sectors."""
        if sector1 == sector2:
            return 1.0
        
        # Check direct compatibility
        if sector1 in self.sector_compatibility:
            if sector2 in self.sector_compatibility[sector1]:
                return self.sector_compatibility[sector1][sector2]
        
        # Check reverse compatibility
        if sector2 in self.sector_compatibility:
            if sector1 in self.sector_compatibility[sector2]:
                return self.sector_compatibility[sector2][sector1]
        
        # No defined compatibility
        return 0.1
    
    async def _get_semantic_sector_analysis(self, title: str, description: str, content_sample: str) -> str:
        """Use AI to get semantic sector classification."""
        try:
            # Prepare content for AI analysis
            analysis_text = f"Title: {title}\nDescription: {description}\nContent: {content_sample}"
            
            # Use the existing semantic filter for sector classification
            prompt = f"""Analyze this business website content and classify it into ONE of these sectors:
            - digital_tech (web agencies, software development, IT services)
            - ai_ml (artificial intelligence, machine learning, automation)
            - manufacturing (industrial production, metalworking, machinery)
            - construction (building, civil engineering, real estate)
            - office_supplies (office furniture, stationery, office equipment)
            - consulting (business consulting, strategy, management)
            - services (general services, support, maintenance)
            
            Content to analyze:
            {analysis_text}
            
            Respond with ONLY the sector name from the list above."""
            
            # This would use the semantic filter's OpenAI client
            # For now, return a simple classification based on keywords
            text_lower = analysis_text.lower()
            
            # Simple AI-like classification logic
            if any(word in text_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'automation']):
                return 'ai_ml'
            elif any(word in text_lower for word in ['web', 'digital', 'software', 'app', 'tech']):
                return 'digital_tech'
            elif any(word in text_lower for word in ['manufacturing', 'industrial', 'mechanical', 'metalworking']):
                return 'manufacturing'
            elif any(word in text_lower for word in ['construction', 'building', 'civil engineering']):
                return 'construction'
            elif any(word in text_lower for word in ['office', 'supplies', 'furniture', 'stationery']):
                return 'office_supplies'
            elif any(word in text_lower for word in ['consulting', 'advisory', 'strategy']):
                return 'consulting'
            else:
                return 'services'
                
        except Exception as e:
            logger.error(f"Error in semantic sector analysis: {str(e)}")
            return 'unknown'
    
    def _extract_sector_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract which sector keywords were found in the text."""
        found_keywords = {}
        
        for sector, definition in self.sector_definitions.items():
            sector_keywords = []
            for keyword in definition['keywords']:
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text):
                    sector_keywords.append(keyword)
            
            if sector_keywords:
                found_keywords[sector] = sector_keywords
        
        return found_keywords

# Global sector classifier instance
sector_classifier = SectorClassifier()