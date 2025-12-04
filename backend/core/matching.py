import re
import os
from typing import List, Dict, Set, Optional
from collections import Counter
import logging

from core.semantic_filter import semantic_filter
from core.sector_classifier import sector_classifier
from core.keyword_extraction import GENERIC_KEYWORDS, is_generic_keyword

logger = logging.getLogger(__name__)

class KeywordMatcher:
    """Handles keyword matching and scoring for competitor analysis with AI semantic analysis."""
    
    def __init__(self):
        # Common words to ignore when calculating scores
        self.ignore_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'il', 'la', 'le', 'lo', 'gli', 'un', 'una', 'dei', 'delle', 'del', 'della',
            'che', 'con', 'per', 'da', 'di', 'su', 'tra', 'fra', 'come', 'quando', 'dove',
            'it', 'e', 'è', 'a', 'o', 'si', 'se', 'ne', 'ci', 'vi', 'sono', 'hanno',
            'questa', 'questo', 'questi', 'queste', 'all', 'alla', 'alle', 'allo', 'agli'
        }
        
        # Note: Generic keywords are now defined in keyword_extraction.py as GENERIC_KEYWORDS
        # and accessed via is_generic_keyword() function for consistency
        
        # Semantic analysis configuration
        self.semantic_enabled = os.getenv("SEMANTIC_ANALYSIS_ENABLED", "true").lower() == "true"
        self.keyword_weight = float(os.getenv("KEYWORD_WEIGHT", "0.4"))
        self.semantic_weight = float(os.getenv("SEMANTIC_WEIGHT", "0.6"))
    
    def _split_keywords_to_words(self, keywords: List[str]) -> List[str]:
        """
        Split compound keywords into individual words for better matching.
        
        Examples:
            Input: ["Consulenza informatica", "Sviluppo di soluzioni IT"]
            Output: ["consulenza", "informatica", "sviluppo", "soluzioni", "it"]
        
        Args:
            keywords: List of keywords (can be phrases or single words)
            
        Returns:
            List of individual words, lowercase, without stopwords and duplicates
        """
        individual_words = []
        
        for keyword in keywords:
            # Split by spaces and commas
            words = re.split(r'[\s,]+', keyword.lower().strip())
            
            for word in words:
                # Clean the word
                clean_word = re.sub(r'[^a-zA-ZÀ-ÿ]', '', word)
                
                # Filter: min 2 chars, not in stopwords/ignore list
                # Note: We don't filter generic keywords here, they're just weighted differently in scoring
                if (len(clean_word) >= 2 and 
                    clean_word not in self.ignore_words):
                    individual_words.append(clean_word)
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for word in individual_words:
            if word not in seen:
                seen.add(word)
                result.append(word)
        
        logger.info(f"🔍 Keyword splitting: {len(keywords)} phrases → {len(result)} words")
        logger.debug(f"   Original: {keywords}")
        logger.debug(f"   Splitted: {result}")
        
        return result
    
    async def calculate_match_score(
        self, 
        target_keywords: List[str], 
        site_content: str, 
        business_context: Optional[str] = None,
        site_title: str = "",
        meta_description: str = "",
        client_sector_data: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate how well a site matches the target keywords using hybrid approach.
        Combines traditional keyword matching with AI semantic analysis and sector relevance.
        
        Args:
            target_keywords: List of keywords to search for (can be phrases or single words)
            site_content: Full text content from the scraped site
            business_context: Optional business context for better semantic analysis
            site_title: Page title for sector analysis
            meta_description: Meta description for sector analysis
            client_sector_data: Sector analysis data from the client site
            
        Returns:
            Dictionary with comprehensive match score, analysis details, and relevance classification
        """
        try:
            # 🎯 NEW: Split compound keywords into individual words
            original_keywords = target_keywords.copy()
            target_keywords = self._split_keywords_to_words(target_keywords)
            
            logger.info(f"📊 Matching analysis: {len(original_keywords)} original keywords → {len(target_keywords)} words")
            
            # Clean and prepare content for searching
            content_lower = site_content.lower()
            content_words = self._extract_words(content_lower)
            
            # Find matching keywords (traditional approach)
            keyword_matches = self._find_keyword_matches(target_keywords, content_words, content_lower)
            keyword_score_data = self._calculate_keyword_score(target_keywords, keyword_matches)
            
            # Semantic analysis (if enabled)
            semantic_results = {}
            if self.semantic_enabled:
                try:
                    semantic_results = await semantic_filter.analyze_semantic_similarity(
                        target_keywords, site_content, business_context
                    )
                except Exception as e:
                    logger.warning(f"Semantic analysis failed, using keyword-only scoring: {str(e)}")
                    semantic_results = {'semantic_score': 0}
            
            # Sector analysis and relevance scoring
            sector_results = {}
            relevance_results = {'relevance_score': 1.0, 'relevance_label': 'relevant', 'reason': 'No sector analysis'}
            
            try:
                # Analyze competitor sector
                competitor_sector_data = await sector_classifier.analyze_sector(
                    site_content, site_title, meta_description
                )
                sector_results = competitor_sector_data
                
                # Calculate relevance if client sector data is available
                if client_sector_data:
                    relevance_results = sector_classifier.calculate_relevance_score(
                        client_sector_data, competitor_sector_data
                    )
                    
            except Exception as e:
                logger.warning(f"Sector analysis failed: {str(e)}")
                relevance_results = {'relevance_score': 0.8, 'relevance_label': 'partially_relevant', 'reason': 'Sector analysis error'}
            
            # Calculate combined score
            final_score = self._calculate_combined_score(keyword_score_data, semantic_results)
            
            # Apply relevance adjustment to final score
            adjusted_score = self._apply_relevance_adjustment(final_score['combined_score'], relevance_results)
            
            return {
                'match_score': adjusted_score,
                'found_keywords': keyword_matches['found_keywords'],
                'keyword_counts': keyword_matches['keyword_counts'],
                'total_matches': keyword_matches['total_occurrences'],
                'unique_matches': len(keyword_matches['found_keywords']),
                'score_details': {
                    'keyword_score': keyword_score_data['score'],
                    'semantic_score': semantic_results.get('semantic_score', 0),
                    'combined_method': final_score['method'],
                    'keyword_weight': self.keyword_weight,
                    'semantic_weight': self.semantic_weight,
                    'semantic_enabled': self.semantic_enabled,
                    'original_combined_score': final_score['combined_score'],
                    'relevance_adjusted_score': adjusted_score,
                    # ⭐ NEW: Generic keyword filter details
                    'generic_matches': keyword_score_data.get('generic_matches', []),
                    'specific_matches': keyword_score_data.get('specific_matches', []),
                    'quality_flag': keyword_score_data.get('quality_flag', 'UNKNOWN')
                },
                'semantic_analysis': semantic_results if self.semantic_enabled else None,
                'sector_analysis': sector_results,
                'relevance_label': relevance_results['relevance_label'],
                'relevance_score': relevance_results['relevance_score'],
                'relevance_reason': relevance_results['reason']
            }
            
        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return {
                'match_score': 0,
                'found_keywords': [],
                'keyword_counts': {},
                'total_matches': 0,
                'unique_matches': 0,
                'error': str(e)
            }
    
    def _extract_words(self, text: str) -> Set[str]:
        """Extract words from text, removing special characters."""
        # Remove special characters, keep only letters and spaces
        clean_text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', text)
        words = set(clean_text.split())
        
        # Filter out short words and common words
        return {word for word in words if len(word) >= 3 and word not in self.ignore_words}
    
    def _find_keyword_matches(self, target_keywords: List[str], content_words: Set[str], content_text: str) -> Dict:
        """Find which target keywords appear in the content."""
        found_keywords = []
        keyword_counts = {}
        total_occurrences = 0
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower().strip()
            
            if not keyword_lower or len(keyword_lower) < 2:
                continue
            
            # Count occurrences in full text (for phrases)
            phrase_count = content_text.count(keyword_lower)
            
            # Also check if keyword appears as individual word
            if keyword_lower in content_words:
                phrase_count = max(phrase_count, 1)
            
            if phrase_count > 0:
                found_keywords.append(keyword)
                keyword_counts[keyword] = phrase_count
                total_occurrences += phrase_count
        
        return {
            'found_keywords': found_keywords,
            'keyword_counts': keyword_counts,
            'total_occurrences': total_occurrences
        }
    
    def _calculate_keyword_score(self, target_keywords: List[str], matches: Dict) -> Dict:
        """
        Calculate the keyword-based match score with quality weighting.
        
        Uses GENERIC_KEYWORDS from keyword_extraction.py to apply reduced weight (0.3x)
        to generic keywords and penalize matches with ONLY generic keywords (50% reduction).
        """
        if not target_keywords:
            return {'score': 0, 'method': 'no_keywords'}
        
        total_target_keywords = len(target_keywords)
        found_keywords = matches['found_keywords']
        keyword_counts = matches['keyword_counts']
        
        if len(found_keywords) == 0:
            return {'score': 0, 'method': 'no_matches'}
        
        # ⭐ NEW: Separate generic vs specific matches
        generic_matches = []
        specific_matches = []
        
        for keyword in found_keywords:
            if is_generic_keyword(keyword):
                generic_matches.append(keyword)
            else:
                specific_matches.append(keyword)
        
        # Calculate weighted score
        GENERIC_WEIGHT = float(os.getenv('GENERIC_KEYWORD_WEIGHT', '0.3'))
        SPECIFIC_WEIGHT = 1.0
        
        weighted_matches = 0.0
        max_possible_weight = len(target_keywords) * SPECIFIC_WEIGHT  # Assuming all keywords are specific
        
        for keyword in found_keywords:
            count = keyword_counts.get(keyword, 1)
            # Frequency bonus (max 1.5x): 1x at 1 occurrence, 1.5x at 5+ occurrences
            frequency_multiplier = min(1.5, 1 + (count - 1) * 0.1)
            
            if is_generic_keyword(keyword):
                weighted_matches += GENERIC_WEIGHT * frequency_multiplier
            else:
                weighted_matches += SPECIFIC_WEIGHT * frequency_multiplier
        
        # Calculate base score
        if max_possible_weight > 0:
            keyword_score = (weighted_matches / max_possible_weight) * 100
        else:
            keyword_score = 0
        
        # ⚠️ PENALTY: If ONLY generic keywords matched (no specific ones), reduce score by 50%
        quality_flag = ''
        if len(specific_matches) == 0 and len(generic_matches) > 0:
            keyword_score *= 0.5  # 50% penalty
            quality_flag = 'LOW_QUALITY_ONLY_GENERIC'
        elif len(specific_matches) >= 5:
            quality_flag = 'HIGH_QUALITY'
        elif len(specific_matches) >= 2:
            quality_flag = 'MEDIUM_QUALITY'
        elif len(specific_matches) >= 1:
            quality_flag = 'LOW_QUALITY'
        else:
            quality_flag = 'NO_SPECIFIC_KEYWORDS'
        
        # Cap at 100
        final_score = min(100, keyword_score)
        
        logger.info(f"🎯 Match quality: {len(specific_matches)} specific + {len(generic_matches)} generic = {quality_flag}")
        
        return {
            'score': round(final_score, 1),
            'method': 'quality_weighted_generic_filter',
            'weighted_matches': round(weighted_matches, 2),
            'max_possible_weight': round(max_possible_weight, 2),
            'unique_matches': len(found_keywords),
            'total_target': total_target_keywords,
            'generic_matches': generic_matches,
            'specific_matches': specific_matches,
            'quality_flag': quality_flag,
            'breakdown': {
                'generic_keywords': len(generic_matches),
                'specific_keywords': len(specific_matches),
                'penalty_applied': len(specific_matches) == 0 and len(generic_matches) > 0
            }
        }
    
    def _calculate_combined_score(self, keyword_data: Dict, semantic_data: Dict) -> Dict:
        """Calculate combined score from keyword and semantic analysis."""
        keyword_score = keyword_data.get('score', 0)
        semantic_score = semantic_data.get('semantic_score', 0)
        
        if not self.semantic_enabled or semantic_score == 0:
            # Use keyword-only scoring
            return {
                'combined_score': keyword_score,
                'method': 'keyword_only'
            }
        
        # Weighted combination of keyword and semantic scores
        combined_score = (keyword_score * self.keyword_weight) + (semantic_score * self.semantic_weight)
        combined_score = min(100, round(combined_score, 1))
        
        return {
            'combined_score': combined_score,
            'method': 'hybrid_keyword_semantic',
            'keyword_contribution': round(keyword_score * self.keyword_weight, 1),
            'semantic_contribution': round(semantic_score * self.semantic_weight, 1)
        }
    
    def _apply_relevance_adjustment(self, original_score: float, relevance_data: Dict) -> float:
        """Apply sector relevance adjustment to the final score."""
        relevance_score = relevance_data.get('relevance_score', 1.0)
        relevance_label = relevance_data.get('relevance_label', 'relevant')
        
        # Apply different adjustments based on relevance level
        if relevance_label == 'relevant':
            # Keep the original score for truly relevant competitors
            adjusted_score = original_score
        elif relevance_label == 'partially_relevant':
            # Moderate reduction for partially relevant competitors
            adjusted_score = original_score * max(0.6, relevance_score)
        elif relevance_label == 'irrelevant':
            # Significant reduction for irrelevant competitors
            adjusted_score = original_score * max(0.1, relevance_score * 0.3)
        else:
            # Default case
            adjusted_score = original_score * relevance_score
        
        return round(min(100, max(0, adjusted_score)), 1)


def format_match_criteria(
    match_result: Dict,
    keyword_counts: Dict[str, int] = None,
    semantic_score: float = None
) -> str:
    """
    Formatta i criteri di matching in stringa leggibile per il report Excel.
    
    Mostra al cliente PERCHÉ un sito è stato classificato come competitor,
    includendo keywords matchate (con frequenza), score semantico, e quality flag.
    
    Args:
        match_result: Risultato completo di calculate_match_score() con score_details
        keyword_counts: Dict con conteggio occorrenze keywords (opzionale)
        semantic_score: Score semantico 0-100 (opzionale)
        
    Returns:
        Stringa formattata es: "Keywords: Ventilatori(3x), Centrifughi(2x), hvac | Semantic: 75% | ⭐⭐ BUONO"
        
    Examples:
        >>> format_match_criteria(
        ...     {'score_details': {'generic_matches': ['hvac'], 'specific_matches': ['ventilatori'], 'quality_flag': 'HIGH_QUALITY'}},
        ...     {'ventilatori': 3, 'hvac': 1},
        ...     85.0
        ... )
        'Keywords: Ventilatori(3x), hvac | Semantic: 85% | ⭐⭐⭐ OTTIMO'
    """
    from collections import Counter
    
    score_details = match_result.get('score_details', {})
    
    # Estrai keywords matchate
    generic_matches = score_details.get('generic_matches', [])
    specific_matches = score_details.get('specific_matches', [])
    
    # Se non ci sono score_details, prova a usare i campi legacy
    if not generic_matches and not specific_matches:
        found_keywords = match_result.get('found_keywords', [])
        # Separa in base a GENERIC_KEYWORDS
        for kw in found_keywords:
            if is_generic_keyword(kw):
                generic_matches.append(kw)
            else:
                specific_matches.append(kw)
    
    # Prepara lista keywords con frequenza
    keyword_with_freq = []
    
    # Prima le specifiche (in Title Case per evidenziarle)
    for kw in specific_matches[:5]:  # Max 5 per non sovraccaricare
        freq = keyword_counts.get(kw, 1) if keyword_counts else 1
        kw_formatted = kw.title()  # Title Case per keywords specifiche
        if freq > 1:
            keyword_with_freq.append(f"{kw_formatted}({freq}x)")
        else:
            keyword_with_freq.append(kw_formatted)
    
    # Poi le generiche (in lowercase per distinguerle)
    for kw in generic_matches[:3]:  # Max 3 generiche
        freq = keyword_counts.get(kw, 1) if keyword_counts else 1
        kw_lower = kw.lower()  # lowercase per keywords generiche
        if freq > 1:
            keyword_with_freq.append(f"{kw_lower}({freq}x)")
        else:
            keyword_with_freq.append(kw_lower)
    
    # Limita totale a 6-7 keywords
    if len(keyword_with_freq) > 7:
        remaining = len(specific_matches) + len(generic_matches) - 7
        keyword_with_freq = keyword_with_freq[:7]
        keywords_str = ", ".join(keyword_with_freq) + f" +{remaining}"
    else:
        keywords_str = ", ".join(keyword_with_freq) if keyword_with_freq else "Nessuna"
    
    # Costruisci parti della stringa
    parts = [f"Keywords: {keywords_str}"]
    
    # Aggiungi semantic score se disponibile
    if semantic_score is not None and semantic_score > 0:
        parts.append(f"Semantic: {semantic_score:.0f}%")
    
    # Aggiungi quality flag con emoji
    quality_flag = score_details.get('quality_flag', 'UNKNOWN')
    quality_mapping = {
        'HIGH_QUALITY': '⭐⭐⭐ OTTIMO',
        'MEDIUM_QUALITY': '⭐⭐ BUONO',
        'LOW_QUALITY': '⭐ ACCETTABILE',
        'LOW_QUALITY_ONLY_GENERIC': '⚠️ SCARSO (solo generiche)',
        'NO_SPECIFIC_KEYWORDS': '⚠️ SCARSO',
        'UNKNOWN': '❓'
    }
    quality_str = quality_mapping.get(quality_flag, quality_flag)
    parts.append(quality_str)
    
    return " | ".join(parts)


# Global matcher instance
keyword_matcher = KeywordMatcher()

# Alias for backward compatibility
MatchingEngine = KeywordMatcher