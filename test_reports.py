"""
Test script for Smart Competitor Finder Report Generation
Tests the complete report generation workflow
"""

import requests
import time
import json
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8002/api"

def test_report_generation():
    """Test the complete report generation workflow"""
    print("🚀 Testing Smart Competitor Finder Report Generation System")
    print("=" * 60)
    
    # Test data
    test_request = {
        "client_url": "https://marketing-agency.com",
        "keywords": ["digital marketing", "web design", "SEO", "branding"],
        "competitors": [
            "https://competitor1.com",
            "https://competitor2.com", 
            "https://another-agency.com"
        ]
    }
    
    try:
        # Step 1: Start report generation
        print("\n📊 Step 1: Starting report generation...")
        response = requests.post(f"{BASE_URL}/generate-report", json=test_request)
        
        if response.status_code != 200:
            print(f"❌ Failed to start report generation: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        report_id = result["report_id"]
        print(f"✅ Report generation started with ID: {report_id}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        
        # Step 2: Monitor report status
        print(f"\n📈 Step 2: Monitoring report status...")
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = requests.get(f"{BASE_URL}/report-status/{report_id}")
            
            if response.status_code != 200:
                print(f"❌ Failed to get report status: {response.status_code}")
                return
            
            status_data = response.json()
            print(f"   Status: {status_data['status']} - {status_data['message']}")
            
            if status_data["status"] == "completed":
                print("✅ Report generation completed!")
                break
            elif status_data["status"] == "failed":
                print(f"❌ Report generation failed: {status_data['message']}")
                return
            
            time.sleep(5)  # Wait 5 seconds before checking again
        else:
            print("⏰ Report generation timed out")
            return
        
        # Step 3: Download the report
        print(f"\n📥 Step 3: Downloading report...")
        response = requests.get(f"{BASE_URL}/download-report/{report_id}")
        
        if response.status_code != 200:
            print(f"❌ Failed to download report: {response.status_code}")
            print(response.text)
            return
        
        # Save the downloaded file
        downloads_dir = Path("test_downloads")
        downloads_dir.mkdir(exist_ok=True)
        
        filename = f"test_report_{report_id}.xlsx"
        filepath = downloads_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Report downloaded successfully: {filepath}")
        print(f"   File size: {len(response.content)} bytes")
        
        # Step 4: List all reports
        print(f"\n📝 Step 4: Listing all reports...")
        response = requests.get(f"{BASE_URL}/reports")
        
        if response.status_code == 200:
            reports_data = response.json()
            print(f"✅ Found {len(reports_data['reports'])} reports:")
            for report in reports_data['reports']:
                print(f"   - {report['report_id']}: {report['status']} ({report['created_at']})")
        
        print(f"\n🎉 All tests completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API server.")
        print("   Make sure the FastAPI server is running on port 8002")
        print("   Run: python backend/main.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_report_generator_directly():
    """Test the report generator directly without API"""
    print("\n🔧 Testing Report Generator directly...")
    
    try:
        from backend.core.report_generator import ReportGenerator
        
        # Sample test data
        client_url = "https://test-agency.com"
        client_keywords = ["marketing", "design", "branding"]
        
        sample_results = [
            {
                "url": "https://competitor1.com",
                "total_score": 0.85,
                "keyword_score": 0.80,
                "semantic_score": 0.90,
                "sector": "Digital Marketing",
                "is_relevant": True,
                "keywords_found": ["marketing", "design"],
                "semantic_similarity": 0.90,
                "relevance_label": "Highly Relevant",
                "analysis_notes": "Strong competitor",
                "content_summary": "Digital marketing and web design services"
            },
            {
                "url": "https://competitor2.com",
                "total_score": 0.45,
                "keyword_score": 0.40,
                "semantic_score": 0.50,
                "sector": "Technology",
                "is_relevant": True,
                "keywords_found": ["design"],
                "semantic_similarity": 0.50,
                "relevance_label": "Moderately Relevant",
                "analysis_notes": "Partial match",
                "content_summary": "Technology consulting with some design services"
            },
            {
                "url": "https://irrelevant-site.com",
                "total_score": 0.05,
                "keyword_score": 0.02,
                "semantic_score": 0.08,
                "sector": "Manufacturing",
                "is_relevant": False,
                "keywords_found": [],
                "semantic_similarity": 0.08,
                "relevance_label": "Not Relevant",
                "analysis_notes": "Different sector entirely",
                "content_summary": "Manufacturing equipment and industrial supplies"
            }
        ]
        
        # Generate report
        generator = ReportGenerator()
        
        # Create test output directory
        test_dir = Path("test_reports")
        test_dir.mkdir(exist_ok=True)
        
        output_path = test_dir / "direct_test_report.xlsx"
        
        final_path = generator.generate_comprehensive_report(
            client_url=client_url,
            client_keywords=client_keywords,
            analysis_results=sample_results,
            output_path=str(output_path)
        )
        
        if os.path.exists(final_path):
            file_size = os.path.getsize(final_path)
            print(f"✅ Direct report generation successful!")
            print(f"   File: {final_path}")
            print(f"   Size: {file_size} bytes")
            return True
        else:
            print("❌ Report file was not created")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        return False


if __name__ == "__main__":
    print("Smart Competitor Finder - Report Generation Tests")
    print("=" * 50)
    
    # Test 1: Direct report generator
    success1 = test_report_generator_directly()
    
    # Test 2: Full API workflow
    if success1:
        success2 = test_report_generation()
        
        if success1 and success2:
            print("\n🏆 All tests passed! Report generation system is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
    else:
        print("\n⚠️  Direct test failed. Skipping API test.")