#!/usr/bin/env python3
"""
Test Task 3: Verifica nuove soglie 65%/50%
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from api.upload_analyze import classify_competitor_status

def test_new_thresholds():
    """Testa le nuove soglie di classificazione"""
    print("\n🧪 Testing Task 3: New Thresholds (65%/50%)")
    print("=" * 60)
    
    test_cases = [
        (70, "DIRECT", "Above 65% threshold"),
        (65, "DIRECT", "Exactly at 65% threshold"),
        (64, "POTENTIAL", "Just below 65% threshold"),
        (55, "POTENTIAL", "Above 50% threshold"),
        (50, "POTENTIAL", "Exactly at 50% threshold"),
        (49, "NON_COMPETITOR", "Just below 50% threshold"),
        (30, "NON_COMPETITOR", "Well below 50% threshold"),
    ]
    
    all_passed = True
    
    for score, expected_category, description in test_cases:
        result = classify_competitor_status(score)
        actual_category = result['category']
        passed = actual_category == expected_category
        
        status_icon = "✅" if passed else "❌"
        print(f"{status_icon} Score {score}%: {actual_category:15} (expected: {expected_category}) - {description}")
        
        if not passed:
            all_passed = False
            print(f"   ERROR: Got {actual_category}, expected {expected_category}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All threshold tests PASSED!")
        print("\n📊 New Classification:")
        print("   🟢 DIRECT Competitor:    score >= 65% (was 60%)")
        print("   🟡 POTENTIAL Competitor: 50% <= score < 65% (was 40%)")
        print("   ⚪ NON Competitor:       score < 50% (was 40%)")
        return True
    else:
        print("❌ Some threshold tests FAILED!")
        return False

if __name__ == "__main__":
    success = test_new_thresholds()
    sys.exit(0 if success else 1)
