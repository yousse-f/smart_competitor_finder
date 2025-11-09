import os
import asyncio
from typing import List, Dict, Any, Optional
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import AsyncOpenAI
import hashlib
import json
from dotenv import load_dotenv

# Load environment variables before initializing OpenAI client
load_dotenv()

logger = logging.getLogger(__name__)

class SemanticFilter:
    """Advanced semantic analysis using OpenAI embeddings and cosine similarity."""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.semantic_threshold = float(os.getenv("SEMANTIC_THRESHOLD", "0.7"))
        
        # Simple in-memory cache for embeddings (in production, use Redis)
        self.embedding_cache = {}
        
        # Maximum text length for embeddings (OpenAI limit)
        self.max_text_length = 8000
        
    async def analyze_semantic_similarity(
        self, 
        target_keywords: List[str], 
        site_content: str, 
        business_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze semantic similarity between target keywords and site content.
        
        Args:
            target_keywords: List of keywords from the client site
            site_content: Full text content from competitor site
            business_context: Optional business context for better analysis
            
        Returns:
            Dictionary with semantic analysis results
        """
        try:
            logger.info(f"Starting semantic analysis with {len(target_keywords)} keywords")
            
            # Prepare texts for embedding
            target_text = self._prepare_target_text(target_keywords, business_context)
            competitor_text = self._prepare_competitor_text(site_content)
            
            # Get embeddings for both texts
            target_embedding = await self._get_embedding(target_text)
            competitor_embedding = await self._get_embedding(competitor_text)
            
            # Calculate cosine similarity
            similarity_score = self._calculate_cosine_similarity(
                target_embedding, competitor_embedding
            )
            
            # Analyze keyword-level semantic matches
            keyword_similarities = await self._analyze_keyword_similarities(
                target_keywords, competitor_text
            )
            
            # Calculate final semantic score
            semantic_results = self._calculate_semantic_score(
                similarity_score, keyword_similarities
            )
            
            return {
                'semantic_score': semantic_results['score'],
                'overall_similarity': similarity_score,
                'keyword_similarities': keyword_similarities,
                'is_semantically_relevant': semantic_results['is_relevant'],
                'confidence': semantic_results['confidence'],
                'analysis_method': 'openai_embeddings_cosine',
                'embedding_model': self.embedding_model
            }
            
        except Exception as e:
            logger.error(f"Error in semantic analysis: {str(e)}")
            return {
                'semantic_score': 0,
                'overall_similarity': 0,
                'keyword_similarities': {},
                'is_semantically_relevant': False,
                'confidence': 0,
                'error': str(e)
            }
    
    def _prepare_target_text(self, keywords: List[str], context: Optional[str] = None) -> str:
        """Prepare target text for embedding generation."""
        # Combine keywords into meaningful context
        keyword_text = " ".join(keywords)
        
        if context:
            return f"Business context: {context}. Key services and products: {keyword_text}"
        else:
            return f"Key business services and products: {keyword_text}"
    
    def _prepare_competitor_text(self, content: str) -> str:
        """Prepare competitor content for embedding, handling length limits."""
        # Truncate if too long
        if len(content) > self.max_text_length:
            content = content[:self.max_text_length]
        
        return content.strip()
    
    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text with caching."""
        # Create cache key
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache first
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            # Get embedding from OpenAI
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = np.array(response.data[0].embedding)
            
            # Cache the result
            self.embedding_cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Return zero vector as fallback
            return np.zeros(1536)  # Default dimension for text-embedding-3-small
    
    def _calculate_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            # Reshape for sklearn
            vec1_reshaped = vec1.reshape(1, -1)
            vec2_reshaped = vec2.reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(vec1_reshaped, vec2_reshaped)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    async def _analyze_keyword_similarities(
        self, 
        keywords: List[str], 
        competitor_text: str
    ) -> Dict[str, float]:
        """Analyze semantic similarity for individual keywords."""
        keyword_similarities = {}
        
        for keyword in keywords:
            try:
                # Get embeddings for keyword and competitor text
                keyword_embedding = await self._get_embedding(keyword)
                competitor_embedding = await self._get_embedding(competitor_text)
                
                # Calculate similarity
                similarity = self._calculate_cosine_similarity(
                    keyword_embedding, competitor_embedding
                )
                
                keyword_similarities[keyword] = round(similarity, 3)
                
            except Exception as e:
                logger.error(f"Error analyzing similarity for keyword '{keyword}': {str(e)}")
                keyword_similarities[keyword] = 0.0
        
        return keyword_similarities
    
    def _calculate_semantic_score(
        self, 
        overall_similarity: float, 
        keyword_similarities: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate final semantic score and relevance."""
        # Get average keyword similarity
        keyword_scores = list(keyword_similarities.values())
        avg_keyword_similarity = np.mean(keyword_scores) if keyword_scores else 0
        
        # Combined score (weighted average)
        combined_score = (overall_similarity * 0.6) + (avg_keyword_similarity * 0.4)
        
        # Convert to percentage
        semantic_score = round(combined_score * 100, 1)
        
        # Determine relevance
        is_relevant = combined_score >= self.semantic_threshold
        
        # Calculate confidence based on consistency
        confidence = self._calculate_confidence(overall_similarity, keyword_scores)
        
        return {
            'score': semantic_score,
            'is_relevant': is_relevant,
            'confidence': confidence,
            'overall_similarity': round(overall_similarity, 3),
            'avg_keyword_similarity': round(avg_keyword_similarity, 3)
        }
    
    def _calculate_confidence(self, overall_sim: float, keyword_sims: List[float]) -> str:
        """Calculate confidence level based on score consistency."""
        if not keyword_sims:
            return "low"
        
        # Check score variance
        variance = np.var(keyword_sims + [overall_sim])
        avg_score = (overall_sim + np.mean(keyword_sims)) / 2
        
        if avg_score > 0.8 and variance < 0.05:
            return "high"
        elif avg_score > 0.6 and variance < 0.1:
            return "medium"
        else:
            return "low"
    
    def clear_cache(self):
        """Clear embedding cache."""
        self.embedding_cache.clear()
        logger.info("Embedding cache cleared")

# Global semantic filter instance
semantic_filter = SemanticFilter()