#!/usr/bin/env python3
"""
Database and business logic tests for the NAMASTE-ICD-11 Integration service
Tests the core functionality without HTTP layer
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from app.conceptmap import fetch_concept_map, fetch_namaste_term, fetch_icd11_title

DB_PATH = "db/ayush_icd11_combined.db"

class TestConceptMapLogic:
    """Test the core concept mapping business logic"""
    
    def test_database_connection(self):
        """Test that database is accessible and has expected tables"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check that concept_map table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='concept_map'")
        result = cur.fetchone()
        assert result is not None, "concept_map table should exist"
        
        # Check table structure
        cur.execute("PRAGMA table_info(concept_map)")
        columns = [row[1] for row in cur.fetchall()]
        expected_columns = ["id", "source_system", "source_code", "target_system", "target_code", "equivalence"]
        for col in expected_columns:
            assert col in columns, f"Column {col} should exist in concept_map table"
        
        conn.close()
    
    def test_concept_map_data_quality(self):
        """Test that concept map data meets quality standards"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check that we have mappings
        cur.execute("SELECT COUNT(*) FROM concept_map")
        count = cur.fetchone()[0]
        assert count > 0, "Should have concept mappings in database"
        
        # Check for required fields
        cur.execute("SELECT COUNT(*) FROM concept_map WHERE source_code IS NULL OR target_code IS NULL")
        null_count = cur.fetchone()[0]
        assert null_count == 0, "No mappings should have null source or target codes"
        
        # Check for consistent systems
        cur.execute("SELECT DISTINCT source_system FROM concept_map")
        source_systems = [row[0] for row in cur.fetchall()]
        assert "NAMASTE" in source_systems, "Should have NAMASTE as source system"
        
        cur.execute("SELECT DISTINCT target_system FROM concept_map")
        target_systems = [row[0] for row in cur.fetchall()]
        assert "ICD-11 TM2" in target_systems, "Should have ICD-11 TM2 as target system"
        
        conn.close()
    
    def test_fetch_concept_map_function(self):
        """Test the fetch_concept_map function with various inputs"""
        # Get a valid code to test with
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT source_code FROM concept_map LIMIT 1")
        valid_code = cur.fetchone()[0]
        conn.close()
        
        # Test with valid code
        result = fetch_concept_map(valid_code)
        assert len(result) > 0, "Should find mappings for valid code"
        
        # Validate result structure
        for mapping in result:
            assert len(mapping) == 3, "Each mapping should have 3 elements (source, target, equivalence)"
            source_code, target_code, equivalence = mapping
            assert source_code is not None, "Source code should not be None"
            assert target_code is not None, "Target code should not be None"
            assert equivalence is not None, "Equivalence should not be None"
        
        # Test with invalid code
        invalid_result = fetch_concept_map("INVALID_CODE_XYZ")
        assert len(invalid_result) == 0, "Should return empty list for invalid code"
    
    def test_namaste_icd11_mapping_consistency(self):
        """Test that NAMASTE to ICD-11 mappings are consistent"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Get equivalence counts and validate relationship mix
        cur.execute("SELECT equivalence, COUNT(*) FROM concept_map GROUP BY equivalence")
        equivalence_rows = cur.fetchall()
        equivalence_counts = {equiv: count for equiv, count in equivalence_rows}

        allowed_equivalences = {"equivalent", "relatedto"}
        assert set(equivalence_counts.keys()).issubset(allowed_equivalences), (
            f"Unexpected equivalence values present: {set(equivalence_counts.keys()) - allowed_equivalences}"
        )

        total_mappings = sum(equivalence_counts.values())
        assert total_mappings == 468, f"Concept map should contain 468 rows, found {total_mappings}"
        assert equivalence_counts.get("equivalent", 0) == 218, (
            f"Expected 218 equivalent mappings, found {equivalence_counts.get('equivalent', 0)}"
        )
        assert equivalence_counts.get("relatedto", 0) == 250, (
            f"Expected 250 related mappings, found {equivalence_counts.get('relatedto', 0)}"
        )
        
        # Check that we have the expected SR code patterns
        cur.execute("SELECT DISTINCT source_code FROM concept_map WHERE source_code LIKE 'SR%'")
        sr_codes = [row[0] for row in cur.fetchall()]
        assert len(sr_codes) > 0, "Should have SR codes in mappings"
        
        # Check that target codes are also SR codes
        cur.execute("SELECT DISTINCT target_code FROM concept_map WHERE target_code LIKE 'SR%'")
        target_sr_codes = [row[0] for row in cur.fetchall()]
        assert len(target_sr_codes) > 0, "Should have SR target codes"
        
        conn.close()
    
    def test_code_normalization(self):
        """Test that code spaces are properly normalized"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check that codes don't have excessive whitespace
        cur.execute("SELECT source_code FROM concept_map")
        codes = [row[0] for row in cur.fetchall()]
        
        for code in codes:
            # Should not have leading/trailing spaces
            assert code == code.strip(), f"Code should not have leading/trailing spaces: '{code}'"
            
            # Should not have multiple consecutive spaces
            import re
            normalized = re.sub(r'\s+', ' ', code)
            assert code == normalized, f"Code should not have multiple spaces: '{code}'"

            # Should not contain non-breaking spaces
            assert '\u00A0' not in code, f"Code should not contain non-breaking spaces: '{code}'"
        
        conn.close()
    
    def test_ayurveda_pattern_mapping(self):
        """Test that Ayurveda vāta patterns are properly mapped"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check for vāta pattern mappings (contains AAA)
        cur.execute("""
            SELECT source_code, target_code 
            FROM concept_map 
            WHERE source_code LIKE '%AAA%'
        """)
        vata_mappings = cur.fetchall()
        
        assert len(vata_mappings) > 0, "Should have vāta pattern mappings"
        
        # Check that these map to valid ICD-11 TM2 codes (can be SR or AA prefixes)
        for source, target in vata_mappings:
            assert target.startswith(("SR", "AA")), f"vāta patterns should map to SR or AA codes, got: {target}"
        
        conn.close()

def run_tests():
    """Run all tests manually (for environments without pytest)"""
    test_class = TestConceptMapLogic()
    
    tests = [
        ("Database Connection", test_class.test_database_connection),
        ("Data Quality", test_class.test_concept_map_data_quality),
        ("Fetch Function", test_class.test_fetch_concept_map_function),
        ("Mapping Consistency", test_class.test_namaste_icd11_mapping_consistency),
        ("Code Normalization", test_class.test_code_normalization),
        ("Ayurveda Patterns", test_class.test_ayurveda_pattern_mapping),
    ]
    
    print("RUNNING CONCEPT MAP LOGIC TESTS")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)