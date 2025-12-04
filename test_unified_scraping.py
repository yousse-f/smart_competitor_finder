#!/usr/bin/env python3
"""
🧪 Test Unified Scraping Method
Verifica che il nuovo metodo unificato (Basic HTTP → Browser Pool fallback) funzioni correttamente
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.hybrid_scraper_v2 import hybrid_scraper_v2
from core.browser_pool import browser_pool

async def test_unified_scraping():
    """Test del nuovo metodo unificato di scraping"""
    
    # Test URLs: mix di siti facili e difficili
    test_urls = [
        "https://www.publicissapient.com/",  # Sito client del log - dovrebbe funzionare
        "https://www.easycoop.com/",         # Sito che dava 403 - test fallback Browser Pool
        "https://www.studioinnovativo.it/", # Sito che funzionava - dovrebbe continuare
        "https://www.google.com/",           # Sito facile - test Basic HTTP
        "https://www.amazon.it/",            # Sito complesso - test fallback
    ]
    
    print("=" * 80)
    print("🧪 TEST UNIFIED SCRAPING METHOD")
    print("=" * 80)
    print(f"\n📋 Testing {len(test_urls)} URLs with unified fallback...\n")
    
    # Check Browser Pool status
    print(f"🏊 Browser Pool Status:")
    print(f"   - Initialized: {browser_pool.is_initialized}")
    if hasattr(browser_pool, 'session_pool'):
        print(f"   - Pool Size: {len(browser_pool.session_pool)}")
    print()
    
    results = {
        'success': [],
        'failed': [],
        'total_duration': 0.0
    }
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*80}")
        print(f"🎯 Test {i}/{len(test_urls)}: {url}")
        print(f"{'='*80}")
        
        try:
            import time
            start = time.time()
            
            # Usa il nuovo metodo unificato
            result = await hybrid_scraper_v2.scrape_intelligent(url, max_keywords=15)
            
            duration = time.time() - start
            results['total_duration'] += duration
            
            if result.get('status') == 'success':
                keywords_count = len(result.get('keywords', []))
                method = result.get('scraping_method', 'unknown')
                content_length = result.get('content_length', 0)
                
                print(f"\n✅ SUCCESS")
                print(f"   - Method: {method}")
                print(f"   - Duration: {duration:.2f}s")
                print(f"   - Keywords: {keywords_count}")
                print(f"   - Content: {content_length:,} chars")
                
                if keywords_count > 0:
                    print(f"   - Sample keywords: {', '.join([kw['keyword'] for kw in result['keywords'][:5]])}")
                
                results['success'].append({
                    'url': url,
                    'method': method,
                    'duration': duration,
                    'keywords': keywords_count
                })
            else:
                error = result.get('error', 'Unknown error')
                print(f"\n❌ FAILED")
                print(f"   - Error: {error}")
                print(f"   - Duration: {duration:.2f}s")
                
                results['failed'].append({
                    'url': url,
                    'error': error,
                    'duration': duration
                })
        
        except Exception as e:
            print(f"\n💥 EXCEPTION: {e}")
            results['failed'].append({
                'url': url,
                'error': str(e),
                'duration': 0
            })
    
    # Final Summary
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    
    total = len(test_urls)
    success_count = len(results['success'])
    failed_count = len(results['failed'])
    success_rate = (success_count / total * 100) if total > 0 else 0
    avg_duration = results['total_duration'] / total if total > 0 else 0
    
    print(f"\n✅ Successful: {success_count}/{total} ({success_rate:.1f}%)")
    print(f"❌ Failed: {failed_count}/{total} ({100-success_rate:.1f}%)")
    print(f"⏱️  Average Duration: {avg_duration:.2f}s")
    print(f"⏱️  Total Duration: {results['total_duration']:.2f}s")
    
    if results['success']:
        print(f"\n🎯 Successful Sites:")
        for r in results['success']:
            print(f"   ✅ {r['url']}")
            print(f"      Method: {r['method']}, Duration: {r['duration']:.2f}s, Keywords: {r['keywords']}")
    
    if results['failed']:
        print(f"\n❌ Failed Sites:")
        for r in results['failed']:
            print(f"   ❌ {r['url']}")
            print(f"      Error: {r['error'][:100]}")
    
    # Performance stats
    print(f"\n📈 Scraper Statistics:")
    stats = await hybrid_scraper_v2.get_enhanced_stats()
    print(f"   - Total Requests: {stats.get('total_requests', 0)}")
    print(f"   - Success Rate: {stats.get('success_rate', 0):.1f}%")
    print(f"   - Basic HTTP Success: {stats.get('basic_success', 0)}")
    print(f"   - Browser Pool Success: {stats.get('browser_pool_success', 0)}")
    
    print("\n" + "=" * 80)
    print("🏁 TEST COMPLETED")
    print("=" * 80)
    
    return success_rate >= 80.0  # Consider test passed if 80%+ success

if __name__ == "__main__":
    print("\n🚀 Starting Unified Scraping Test...\n")
    
    try:
        success = asyncio.run(test_unified_scraping())
        
        if success:
            print("\n✅ TEST PASSED - Success rate >= 80%")
            sys.exit(0)
        else:
            print("\n⚠️ TEST WARNING - Success rate < 80%")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)
