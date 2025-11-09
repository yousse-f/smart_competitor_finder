import re
import os
from typing import List, Dict, Set, Optional
from collections import Counter
import logging

from core.semantic_filter import semantic_filter
from core.sector_classifier import sector_classifier

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
        
        # ⭐ NEW: Keyword Quality Weighting
        # Generic keywords (too common across sectors) - LOW weight
        self.generic_keywords = {
            'soluzioni', 'solutions', 'innovazione', 'innovation', 'sviluppo', 'development',
            'tecnologia', 'technology', 'servizi', 'services', 'qualità', 'quality',
            'efficienza', 'efficiency', 'esperienza', 'experience', 'professionale', 'professional',
            'azienda', 'company', 'impresa', 'business', 'prodotto', 'product', 'cliente', 'customer',
            'team', 'gruppo', 'group', 'Italia', 'italy', 'mondo', 'world', 'mercato', 'market'
        }
        
        # Sector-specific keywords (high value) - HIGH weight
        self.high_value_keywords = {
            # IT/Digital
            'software', 'cloud', 'cybersecurity', 'api', 'database', 'frontend', 'backend',
            'informatica', 'digitale', 'app', 'mobile', 'web', 'sviluppatori', 'programmazione',
            'devops', 'agile', 'scrum', 'microservizi', 'kubernetes', 'docker', 'react', 'angular',
            # Manufacturing
            'meccanica', 'metalworking', 'carpenteria', 'cnc', 'tornio', 'fresatura',
            'lamiera', 'saldatura', 'assemblaggio', 'officina', 'prototipazione', 'stampi',
            # Construction
            'edilizia', 'costruzioni', 'cantiere', 'ristrutturazione', 'cemento', 'mattoni',
            # Consulting specific
            'consulenza', 'advisory', 'strategia', 'strategy', 'management', 'governance'
        }
        
        # Weight multipliers
        self.generic_weight = 0.3  # Generic keywords count 30%
        self.normal_weight = 1.0   # Normal keywords count 100%
        self.high_value_weight = 1.5  # High-value keywords count 150%
        
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
                if (len(clean_word) >= 2 and 
                    clean_word not in self.ignore_words and
                    clean_word not in self.generic_keywords):  # Don't filter generic, just flag them
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
                    'relevance_adjusted_score': adjusted_score
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
        """Calculate the keyword-based match score with quality weighting."""
        if not target_keywords:
            return {'score': 0, 'method': 'no_keywords'}
        
        total_target_keywords = len(target_keywords)
        found_keywords = matches['found_keywords']
        keyword_counts = matches['keyword_counts']
        
        if len(found_keywords) == 0:
            return {'score': 0, 'method': 'no_matches'}
        
        # ⭐ NEW: Calculate weighted matches
        weighted_matches = 0.0
        weighted_total_keywords = 0.0
        generic_count = 0
        high_value_count = 0
        normal_count = 0
        
        # Calculate total weighted keywords (denominator)
        for keyword in target_keywords:
            keyword_lower = keyword.lower().strip()
            if keyword_lower in self.generic_keywords:
                weighted_total_keywords += self.generic_weight
            elif keyword_lower in self.high_value_keywords:
                weighted_total_keywords += self.high_value_weight
            else:
                weighted_total_keywords += self.normal_weight
        
        # Calculate weighted found keywords (numerator)
        for keyword in found_keywords:
            keyword_lower = keyword.lower().strip()
            count = keyword_counts.get(keyword, 1)
            
            if keyword_lower in self.generic_keywords:
                # Generic keywords count less
                weighted_matches += self.generic_weight
                generic_count += 1
            elif keyword_lower in self.high_value_keywords:
                # High-value keywords count more + frequency bonus
                weighted_matches += self.high_value_weight * min(1.5, 1 + (count - 1) * 0.1)
                high_value_count += 1
            else:
                # Normal keywords with frequency bonus
                weighted_matches += self.normal_weight * min(1.5, 1 + (count - 1) * 0.1)
                normal_count += 1
        
        # Calculate weighted score
        if weighted_total_keywords > 0:
            weighted_score = (weighted_matches / weighted_total_keywords) * 100
        else:
            weighted_score = 0
        
        # Cap at 100
        final_score = min(100, weighted_score)
        
        return {
            'score': round(final_score, 1),
            'method': 'quality_weighted',
            'weighted_matches': round(weighted_matches, 2),
            'weighted_total': round(weighted_total_keywords, 2),
            'unique_matches': len(found_keywords),
            'total_target': total_target_keywords,
            'breakdown': {
                'generic_keywords': generic_count,
                'high_value_keywords': high_value_count,
                'normal_keywords': normal_count
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

# Global matcher instance
keyword_matcher = KeywordMatcher()

# Alias for backward compatibility
MatchingEngine = KeywordMatcher