#!/usr/bin/env python3
"""
Test runner - Runs all tests in the test suite
"""
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_logic import run_tests as run_logic_tests
from tests.test_fhir import run_fhir_tests

def run_all_tests():
    """Run the complete test suite"""
    print("🧪 NAMASTE-ICD-11 INTEGRATION TEST SUITE")
    print("="*60)
    print("Testing FHIR-compliant terminology service for Ayurveda-ICD-11 mappings")
    print()
    
    all_passed = True
    
    # Run logic tests
    print("🔧 BUSINESS LOGIC TESTS")
    print("-" * 30)
    logic_passed = run_logic_tests()
    all_passed = all_passed and logic_passed
    print()
    
    # Run FHIR compliance tests
    print("📋 FHIR COMPLIANCE TESTS")
    print("-" * 30)
    fhir_passed = run_fhir_tests()
    all_passed = all_passed and fhir_passed
    print()
    
    # Summary
    print("="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The NAMASTE-ICD-11 service is working correctly.")
        print("✅ Database mappings are valid")
        print("✅ FHIR ConceptMap resources are compliant")
        print("✅ API endpoints are functioning")
    else:
        print("❌ SOME TESTS FAILED! Please review the errors above.")
    
    print("="*60)
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)