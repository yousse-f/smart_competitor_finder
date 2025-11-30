#!/usr/bin/env python3
"""
Test script per verificare timeout 60s e batch processing
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

async def test_timeout_single_site():
    """Test timeout 60s su singolo sito problematico"""
    print("=" * 60)
    print("TEST 1: Timeout 60s per singolo sito")
    print("=" * 60)
    
    # Crea file temporaneo con URL noto per timeout
    test_file = "test_timeout_site.txt"
    with open(test_file, "w") as f:
        f.write("https://euroventilatori-int.com\n")  # Sito che ha causato freeze 7 ore
        f.write("https://www.ikea.com\n")  # Sito veloce come controllo
    
    print(f"✅ Creato {test_file} con 2 URLs")
    print("📤 Inviando al backend...")
    
    start_time = datetime.now()
    
    try:
        # Upload file
        data = aiohttp.FormData()
        data.add_field('file',
                      open(test_file, 'rb'),
                      filename='test_timeout.txt',
                      content_type='text/plain')
        data.add_field('keywords', 'test,refrigerazione')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/upload-and-analyze-stream",
                data=data
            ) as response:
                print(f"📊 Status: {response.status}")
                
                # Read SSE stream
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        event_data = json.loads(line_str[6:])
                        event_type = event_data.get('event')
                        
                        if event_type == 'started':
                            print(f"🚀 Analysis started (ID: {event_data.get('analysis_id')})")
                        elif event_type == 'progress':
                            print(f"📊 Progress: {event_data.get('percentage')}% - {event_data.get('url')}")
                        elif event_type == 'site_failed':
                            print(f"⚠️ SITE FAILED: {event_data.get('url')} (reason: {event_data.get('reason')})")
                        elif event_type == 'result':
                            print(f"✅ Result: {event_data.get('url')} → {event_data.get('score')}%")
                        elif event_type == 'complete':
                            duration = (datetime.now() - start_time).total_seconds()
                            print(f"🎉 Complete! Duration: {duration:.1f}s")
                            print(f"   Failed sites: {event_data.get('failed_count', 0)}")
                            if event_data.get('failed_sites'):
                                for failed in event_data['failed_sites']:
                                    print(f"   ❌ {failed['url']}: {failed['error']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

async def test_batch_processing():
    """Test batch automatico con 250 URLs fake"""
    print("=" * 60)
    print("TEST 2: Batch processing (250 sites)")
    print("=" * 60)
    
    # Crea file con 250 URLs fake
    test_file = "test_250_sites.txt"
    with open(test_file, "w") as f:
        for i in range(250):
            f.write(f"https://example{i}.com\n")
    
    print(f"✅ Creato {test_file} con 250 URLs")
    print("📤 Inviando al backend...")
    
    start_time = datetime.now()
    batches_seen = set()
    
    try:
        data = aiohttp.FormData()
        data.add_field('file',
                      open(test_file, 'rb'),
                      filename='test_250.txt',
                      content_type='text/plain')
        data.add_field('keywords', 'test,example')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/upload-and-analyze-stream",
                data=data,
                timeout=aiohttp.ClientTimeout(total=600)  # 10 min timeout
            ) as response:
                print(f"📊 Status: {response.status}")
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        event_data = json.loads(line_str[6:])
                        event_type = event_data.get('event')
                        
                        if event_type == 'batch_info':
                            print(f"📦 BATCH MODE: {event_data.get('total_sites')} sites in {event_data.get('num_batches')} batches")
                        elif event_type == 'batch_start':
                            batch_num = event_data.get('batch_num')
                            batches_seen.add(batch_num)
                            print(f"🔄 BATCH {batch_num}/{event_data.get('total_batches')} started ({event_data.get('batch_size')} sites)")
                        elif event_type == 'batch_complete':
                            print(f"✅ BATCH {event_data.get('batch_num')} completed ({event_data.get('sites_processed')} sites)")
                        elif event_type == 'complete':
                            duration = (datetime.now() - start_time).total_seconds()
                            print(f"🎉 Complete! Duration: {duration:.1f}s")
                            print(f"   Total batches processed: {len(batches_seen)}")
                            print(f"   Expected batches: 3 (250 / 100)")
                            
                            if len(batches_seen) == 3:
                                print("   ✅ BATCH TEST PASSED")
                            else:
                                print(f"   ❌ BATCH TEST FAILED: Expected 3 batches, got {len(batches_seen)}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

async def main():
    print("\n" + "=" * 60)
    print("🧪 TEST SUITE: Timeout 60s + Batch Processing")
    print("=" * 60)
    print()
    
    print("⚠️  PREREQUISITI:")
    print("   1. Backend deve essere in esecuzione su http://localhost:8000")
    print("   2. Playwright deve essere installato")
    print("   3. OpenAI API key configurata (per semantic analysis)")
    print()
    input("Press ENTER per iniziare i test...")
    print()
    
    # Test 1: Timeout
    await test_timeout_single_site()
    
    # Test 2: Batch processing
    await test_batch_processing()
    
    print("=" * 60)
    print("✅ TEST SUITE COMPLETATA")
    print("=" * 60)
    print()
    print("📋 Checklist validazione:")
    print("   [ ] Test 1: euroventilatori-int.com ha timeout dopo ~60s?")
    print("   [ ] Test 1: ikea.com è stato analizzato con successo?")
    print("   [ ] Test 1: failed_sites contiene euroventilatori?")
    print("   [ ] Test 2: Batch info evento ricevuto?")
    print("   [ ] Test 2: 3 batch_start events?")
    print("   [ ] Test 2: 3 batch_complete events?")
    print("   [ ] Test 2: Progress da 0% → 100%?")
    print()

if __name__ == "__main__":
    asyncio.run(main())
