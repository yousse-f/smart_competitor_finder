"""
🚀 Batch Bulk Analyzer - Analisi ottimizzata con batch processing AI

Wrapper per analyze_sites_bulk che:
1. Raccoglie tutti i siti da analizzare
2. Li divide in batch per il processing parallelo
3. Usa classify_competitor_with_ai() (gpt-4o-mini) per ogni sito

NOTA v2.0 (18/02/2026): sector_classifier rimosso — classificazione
delegata interamente a classify_competitor_with_ai() in ai_site_analyzer.py
"""

import asyncio
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


async def analyze_bulk_with_batching(
    sites_data: List[Dict],
    target_keywords: List[str],
    client_url: str = None,
    batch_size: int = 5
) -> List[Dict[str, Any]]:
    """
    Analisi bulk ottimizzata con batch AI classification
    
    Args:
        sites_data: Lista siti con URL e metadata
        target_keywords: Keywords per matching
        client_url: URL cliente (non più usato per sector analysis locale)
        batch_size: Numero siti per batch (default 5, max 10)
        
    Returns:
        Lista risultati con score, classification, reason
    """
    from core.scraping import bulk_scraper
    from core.ai_site_analyzer import ai_analyzer, classify_competitor_with_ai
    
    logger.info(f"🚀 Batch Bulk Analysis: {len(sites_data)} siti, batch_size={batch_size}")
    
    # FASE 1: Scraping base
    logger.info("📡 Fase 1: Scraping e keyword matching...")
    
    initial_results = await bulk_scraper.analyze_sites_bulk(
        sites_data,
        target_keywords,
        client_url=None
    )
    
    logger.info(f"✅ Fase 1 completata: {len(initial_results)} siti elaborati")
    
    # FASE 2: AI classification per ogni sito con contenuto valido
    logger.info(f"🤖 Fase 2: AI classification via gpt-4o-mini (batch_size={batch_size})...")
    
    sites_for_ai = []
    result_map = {}
    
    for result in initial_results:
        if result.get('status') == 'success':
            url = result['url']
            sites_for_ai.append({
                'url': url,
                'content': result.get('_full_content', '') or result.get('text', '')
            })
            result_map[url] = result
    
    logger.info(f"📊 Siti validi per AI: {len(sites_for_ai)}/{len(initial_results)}")
    
    if sites_for_ai:
        # Semaphore per limitare chiamate concorrenti
        semaphore = asyncio.Semaphore(batch_size)
        
        async def classify_one(site: Dict) -> None:
            async with semaphore:
                try:
                    ai_result = await classify_competitor_with_ai(
                        client_keywords=target_keywords,
                        competitor_content=site['content'],
                        competitor_url=site['url']
                    )
                    url = site['url']
                    if url in result_map:
                        result_map[url]['match_score']    = ai_result['score']
                        result_map[url]['classification'] = ai_result['classification']
                        result_map[url]['ai_reason']      = ai_result['reason']
                        result_map[url]['competitor_sector'] = ai_result.get('competitor_sector', 'unknown')
                        logger.info(f"✅ {url}: {ai_result['score']}% [{ai_result['classification']}]")
                except Exception as e:
                    logger.warning(f"⚠️ AI fallback per {site['url']}: {e}")
        
        tasks = [classify_one(s) for s in sites_for_ai]
        await asyncio.gather(*tasks)
        
        logger.info(f"✅ AI batch classification completata: {len(sites_for_ai)} siti")
    
    # Sort by match score
    initial_results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    logger.info(f"🎉 Batch Bulk Analysis completata!")
    logger.info(f"   📊 Totale siti: {len(initial_results)}")
    logger.info(f"   🤖 AI classificati: {len(sites_for_ai)}")
    
    return initial_results
