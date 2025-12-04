#!/usr/bin/env python3
"""
Quick test to verify 'Criteri Match' column is added to Excel report
"""
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.report_generator import ReportGenerator

# Mock analysis results with match_criteria field
mock_results = [
    {
        'url': 'https://example-competitor1.com',
        'score': 85.5,
        'keywords_found': ['ventilatori', 'industriali', 'centrifughi', 'hvac'],
        'title': 'Ventilatori Industriali - Example 1',
        'match_criteria': 'Keywords: Ventilatori(3x), Industriali(2x), Centrifughi(2x) | Semantic: 85% | Quality: ⭐⭐⭐ OTTIMO',
        'competitor_status': {
            'category': 'DIRECT',
            'label': 'Competitor Diretto',
            'emoji': '🔴',
            'action': 'Monitorare attivamente',
            'color': 'green'
        }
    },
    {
        'url': 'https://example-competitor2.com',
        'score': 45.2,
        'keywords_found': ['hvac', 'impianti'],
        'title': 'HVAC Systems - Example 2',
        'match_criteria': 'Keywords: hvac(1x) [GENERICO], impianti(1x) [GENERICO] | Semantic: 30% | Quality: ⚠️ BASSO (solo keyword generiche)',
        'competitor_status': {
            'category': 'NON_COMPETITOR',
            'label': 'Non Competitor',
            'emoji': '⚪',
            'action': 'Escludere',
            'color': 'red'
        }
    },
    {
        'url': 'https://example-competitor3.com',
        'score': 62.8,
        'keywords_found': ['ventilatori', 'centrifughi', 'hvac', 'industriali'],
        'title': 'Industrial Fans & HVAC - Example 3',
        'match_criteria': 'Keywords: Ventilatori(2x), Centrifughi(1x), hvac(1x) [GENERICO] | Semantic: 65% | Quality: ⭐⭐ BUONO',
        'competitor_status': {
            'category': 'POTENTIAL',
            'label': 'Competitor Potenziale',
            'emoji': '🟡',
            'action': 'Valutare periodicamente',
            'color': 'yellow'
        }
    }
]

mock_client_keywords = ['ventilatori', 'industriali', 'centrifughi', 'hvac', 'aria']

def main():
    print("🧪 Testing Excel Report with 'Criteri Match' Column")
    print("=" * 60)
    
    try:
        # Initialize report generator
        generator = ReportGenerator()
        
        # Generate report
        print("📊 Generating report with mock data...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_match_criteria_{timestamp}.xlsx"
        
        filepath = generator.generate_comprehensive_report(
            client_url="https://test-client.com",
            client_keywords=mock_client_keywords,
            analysis_results=mock_results,
            output_path=f"backend/reports/{filename}"
        )
        
        print(f"✅ Report generated successfully!")
        print(f"📁 Location: {filepath}")
        print("\n🔍 Expected columns in 'Summary' sheet:")
        print("   1. Rank")
        print("   2. Website")
        print("   3. Score")
        print("   4. Criteri Match  ← NEW!")
        print("   5. Categoria KPI")
        print("   6. Azione Consigliata")
        print("\n🔍 Expected columns in 'Detailed Results' sheet:")
        print("   1. URL")
        print("   2. Criteri Match  ← NEW!")
        print("   3. Categoria KPI")
        print("   4. Azione")
        print("   5. Keywords Found")
        print("   6. Keyword Count")
        print("   7. Title")
        print(f"\n📂 Open the file to verify: {filepath}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
