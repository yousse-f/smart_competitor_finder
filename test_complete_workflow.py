"""
Test script to verify the complete report generation system with mock data
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8002/api"

def test_report_with_cached_data():
    """Test report generation using cached analysis results"""
    
    print("🧪 Testing Report Generation with Mock Data")
    print("=" * 50)
    
    # Create mock analysis results
    mock_analysis_results = [
        {
            "url": "https://competitor1.com",
            "total_score": 0.85,
            "keyword_score": 0.80,
            "semantic_score": 0.90,
            "sector": "Digital Marketing",
            "is_relevant": True,
            "keywords_found": ["digital marketing", "web design"],
            "semantic_similarity": 0.90,
            "relevance_label": "Highly Relevant",
            "analysis_notes": "Strong competitor in digital marketing space",
            "content_summary": "Digital marketing agency offering web design, SEO, and branding services"
        },
        {
            "url": "https://competitor2.com",
            "total_score": 0.65,
            "keyword_score": 0.60,
            "semantic_score": 0.70,
            "sector": "Web Development",
            "is_relevant": True,
            "keywords_found": ["web design", "SEO"],
            "semantic_similarity": 0.70,
            "relevance_label": "Moderately Relevant",
            "analysis_notes": "Web development focus with some marketing services",
            "content_summary": "Web development company with SEO and design services"
        },
        {
            "url": "https://irrelevant-competitor.com",
            "total_score": 0.15,
            "keyword_score": 0.10,
            "semantic_score": 0.20,
            "sector": "Manufacturing",
            "is_relevant": False,
            "keywords_found": [],
            "semantic_similarity": 0.20,
            "relevance_label": "Not Relevant",
            "analysis_notes": "Different industry sector - manufacturing equipment",
            "content_summary": "Industrial manufacturing and equipment supplier"
        }
    ]
    
    try:
        # Step 1: Cache the mock analysis results
        print("\n📦 Step 1: Caching mock analysis results...")
        analysis_id = "test_analysis_001"
        
        response = requests.post(
            f"{BASE_URL}/cache-analysis",
            params={"analysis_id": analysis_id},
            json=mock_analysis_results
        )
        
        if response.status_code == 200:
            print(f"✅ Analysis results cached with ID: {analysis_id}")
        else:
            print(f"❌ Failed to cache analysis: {response.status_code} - {response.text}")
            return False
        
        # Step 2: Generate report using cached data
        print(f"\n📊 Step 2: Generating report using cached data...")
        
        report_request = {
            "client_url": "https://test-marketing-agency.com",
            "keywords": ["digital marketing", "web design", "SEO", "branding"],
            "analysis_id": analysis_id
        }
        
        response = requests.post(f"{BASE_URL}/generate-report", json=report_request)
        
        if response.status_code != 200:
            print(f"❌ Failed to start report generation: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        report_id = result["report_id"]
        print(f"✅ Report generation started with ID: {report_id}")
        
        # Step 3: Check final status
        import time
        print(f"\n⏳ Step 3: Waiting for report completion...")
        
        for i in range(20):  # Check for up to 1 minute
            time.sleep(3)
            response = requests.get(f"{BASE_URL}/report-status/{report_id}")
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"   Status: {status_data['status']} - {status_data['message']}")
                
                if status_data["status"] == "completed":
                    print("✅ Report generation completed!")
                    
                    # Step 4: Try to download the report
                    print(f"\n📥 Step 4: Testing report download...")
                    response = requests.get(f"{BASE_URL}/download-report/{report_id}")
                    
                    if response.status_code == 200:
                        # Save the report
                        download_dir = Path("test_downloads")
                        download_dir.mkdir(exist_ok=True)
                        
                        filename = f"test_report_{report_id}.xlsx"
                        filepath = download_dir / filename
                        
                        with open(filepath, "wb") as f:
                            f.write(response.content)
                        
                        print(f"✅ Report downloaded successfully!")
                        print(f"   File: {filepath}")
                        print(f"   Size: {len(response.content)} bytes")
                        return True
                    else:
                        print(f"❌ Failed to download report: {response.status_code}")
                        return False
                        
                elif status_data["status"] == "failed":
                    print(f"❌ Report generation failed: {status_data['message']}")
                    return False
            else:
                print(f"   Failed to get status: {response.status_code}")
        
        print("⏰ Report generation timed out")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_report_with_cached_data()
    if success:
        print(f"\n🏆 Complete workflow test PASSED!")
        print("   ✅ API endpoints working")
        print("   ✅ Report generation working") 
        print("   ✅ Excel file creation working")
        print("   ✅ File download working")
    else:
        print(f"\n❌ Complete workflow test FAILED!")