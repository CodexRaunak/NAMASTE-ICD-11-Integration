#!/usr/bin/env python3
"""
FHIR compliance and integration tests
Tests the FHIR ConceptMap resource structure and standards compliance
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from app.conceptmap import get_concept_map, list_all_concept_maps

class TestFHIRCompliance:
    """Test FHIR R4 ConceptMap compliance"""
    
    def test_fhir_conceptmap_structure(self):
        """Test that ConceptMap follows FHIR R4 specification"""
        # Get available codes
        bundle = list_all_concept_maps()
        available_codes = bundle["available_codes"]
        assert len(available_codes) > 0, "Should have available concept maps"
        
        # Test with first available code
        test_code = available_codes[0]
        concept_map = get_concept_map(test_code)
        
        # Required FHIR ConceptMap elements
        assert concept_map["resourceType"] == "ConceptMap", "Must be ConceptMap resource"
        assert "status" in concept_map, "Status is required"
        assert concept_map["status"] in ["active", "inactive", "draft"], "Status must be valid"
        
        # Optional but expected elements
        expected_fields = ["id", "url", "version", "name", "title", "description", "publisher"]
        for field in expected_fields:
            assert field in concept_map, f"ConceptMap should have {field} field"
    
    def test_fhir_group_structure(self):
        """Test that ConceptMap groups follow FHIR specification"""
        bundle = list_all_concept_maps()
        test_code = bundle["available_codes"][0]
        concept_map = get_concept_map(test_code)
        
        assert "group" in concept_map, "ConceptMap must have group element"
        assert len(concept_map["group"]) > 0, "Must have at least one group"
        
        for group in concept_map["group"]:
            # Required group elements
            assert "source" in group, "Group must have source"
            assert "target" in group, "Group must have target"
            assert "element" in group, "Group must have elements"
            
            # Validate URIs
            assert group["source"].startswith("http"), "Source should be a URI"
            assert group["target"].startswith("http"), "Target should be a URI"
            
            # Test elements
            assert len(group["element"]) > 0, "Group must have at least one element"
    
    def test_fhir_element_structure(self):
        """Test that ConceptMap elements follow FHIR specification"""
        bundle = list_all_concept_maps()
        test_code = bundle["available_codes"][0]
        concept_map = get_concept_map(test_code)
        
        group = concept_map["group"][0]
        
        for element in group["element"]:
            # Required element fields
            assert "code" in element, "Element must have code"
            assert "target" in element, "Element must have target"
            
            # Validate code
            assert isinstance(element["code"], str), "Code must be string"
            assert len(element["code"]) > 0, "Code cannot be empty"
            
            # Test targets
            assert len(element["target"]) > 0, "Element must have at least one target"
            
            for target in element["target"]:
                assert "code" in target, "Target must have code"
                assert "relationship" in target, "Target must have relationship"
                
                # Validate relationship codes (FHIR R4)
                valid_relationships = [
                    "related-to", "equivalent", "source-is-narrower-than-target",
                    "source-is-broader-than-target", "not-related-to"
                ]
                assert target["relationship"] in valid_relationships, \
                    f"Invalid relationship: {target['relationship']}"
    
    def test_fhir_json_serialization(self):
        """Test that ConceptMap can be properly serialized to JSON"""
        bundle = list_all_concept_maps()
        test_code = bundle["available_codes"][0]
        concept_map = get_concept_map(test_code)
        
        # Should be serializable to JSON
        json_str = json.dumps(concept_map)
        assert len(json_str) > 0, "Should produce valid JSON"
        
        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["resourceType"] == "ConceptMap", "JSON round-trip should work"
    
    def test_bundle_structure(self):
        """Test that Bundle response follows FHIR specification"""
        bundle = list_all_concept_maps()
        
        # Required Bundle elements
        assert bundle["resourceType"] == "Bundle", "Must be Bundle resource"
        assert "type" in bundle, "Bundle must have type"
        assert bundle["type"] == "searchset", "Should be searchset bundle"
        assert "total" in bundle, "Bundle must have total"
        
        # Validate total
        assert isinstance(bundle["total"], int), "Total must be integer"
        assert bundle["total"] >= 0, "Total must be non-negative"
    
    def test_terminology_service_compliance(self):
        """Test compliance with FHIR Terminology Service patterns"""
        bundle = list_all_concept_maps()
        test_code = bundle["available_codes"][0]
        concept_map = get_concept_map(test_code)
        
        # Should have proper system URIs
        group = concept_map["group"][0]
        
        # Source should be NAMASTE system
        assert "namaste" in group["source"].lower(), "Source should reference NAMASTE"
        
        # Target should be ICD system
        assert "icd" in group["target"].lower() or "who.int" in group["target"], \
            "Target should reference ICD system"
        
        # Should have proper metadata for interoperability
        assert "publisher" in concept_map, "Should have publisher for trust"
        assert "description" in concept_map, "Should have description for understanding"

def run_fhir_tests():
    """Run all FHIR compliance tests"""
    test_class = TestFHIRCompliance()
    
    tests = [
        ("ConceptMap Structure", test_class.test_fhir_conceptmap_structure),
        ("Group Structure", test_class.test_fhir_group_structure),
        ("Element Structure", test_class.test_fhir_element_structure),
        ("JSON Serialization", test_class.test_fhir_json_serialization),
        ("Bundle Structure", test_class.test_bundle_structure),
        ("Terminology Service", test_class.test_terminology_service_compliance),
    ]
    
    print("RUNNING FHIR COMPLIANCE TESTS")
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
    
    print(f"\n📊 FHIR Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = run_fhir_tests()
    sys.exit(0 if success else 1)