#!/usr/bin/env python3
"""
High-level API tests for the NAMASTE-ICD-11 Integration service
Tests the FHIR ConceptMap endpoints and functionality
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestConceptMapAPI:
    """Test the ConceptMap FHIR API endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns service information"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "AYUSH ICD-11 Terminology Microservice"
        assert data["version"] == "0.1.0"
        assert "endpoints" in data
        assert "/ConceptMap" in data["endpoints"]["concept_maps"]
    
    def test_list_concept_maps(self):
        """Test listing all available concept mappings"""
        response = client.get("/ConceptMap")
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert "total" in data
        assert "available_codes" in data
        assert isinstance(data["available_codes"], list)
        assert len(data["available_codes"]) > 0
    
    def test_get_concept_map_success(self):
        """Test retrieving a valid concept map"""
        # First get available codes
        list_response = client.get("/ConceptMap")
        available_codes = list_response.json()["available_codes"]
        
        # Test with the first available code
        test_code = available_codes[0]
        response = client.get(f"/ConceptMap/{test_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["resourceType"] == "ConceptMap"
        assert data["status"] == "active"
        assert "group" in data
        assert len(data["group"]) > 0
        
        # Validate group structure
        group = data["group"][0]
        assert "source" in group
        assert "target" in group
        assert "element" in group
        assert len(group["element"]) > 0
        
        # Validate element structure
        element = group["element"][0]
        assert "code" in element
        assert "target" in element
        assert len(element["target"]) > 0
        
        # Validate target structure
        target = element["target"][0]
        assert "code" in target
        assert "relationship" in target
        assert target["relationship"] == "equivalent"
    
    def test_get_concept_map_not_found(self):
        """Test retrieving a non-existent concept map"""
        response = client.get("/ConceptMap/INVALID_CODE_123")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_concept_map_fhir_compliance(self):
        """Test that returned ConceptMap is FHIR R4 compliant"""
        # Get any available concept map
        list_response = client.get("/ConceptMap")
        available_codes = list_response.json()["available_codes"]
        test_code = available_codes[0]
        
        response = client.get(f"/ConceptMap/{test_code}")
        data = response.json()
        
        # Required FHIR ConceptMap fields
        required_fields = ["resourceType", "status"]
        for field in required_fields:
            assert field in data
        
        # ConceptMap specific validation
        assert data["resourceType"] == "ConceptMap"
        assert data["status"] in ["active", "inactive", "draft"]
        
        # Group validation
        assert "group" in data
        for group in data["group"]:
            assert "source" in group
            assert "target" in group
            assert "element" in group
            
            for element in group["element"]:
                assert "code" in element
                assert "target" in element
                
                for target in element["target"]:
                    assert "code" in target
                    assert "relationship" in target
                    # Valid FHIR relationship codes
                    valid_relationships = [
                        "related-to", "equivalent", "source-is-narrower-than-target",
                        "source-is-broader-than-target", "not-related-to"
                    ]
                    assert target["relationship"] in valid_relationships
    
    def test_url_encoding_handling(self):
        """Test that URL-encoded codes are handled properly"""
        # Test with a code that has special characters (parentheses)
        list_response = client.get("/ConceptMap")
        available_codes = list_response.json()["available_codes"]
        
        # Find a code with parentheses
        test_code = None
        for code in available_codes:
            if "(" in code:
                test_code = code
                break
        
        if test_code:
            # Test URL-encoded version
            import urllib.parse
            encoded_code = urllib.parse.quote(test_code)
            
            response = client.get(f"/ConceptMap/{encoded_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["resourceType"] == "ConceptMap"
    
    def test_api_performance(self):
        """Test that API responds within reasonable time"""
        import time
        
        start_time = time.time()
        response = client.get("/ConceptMap")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds
    
    def test_consistent_mappings(self):
        """Test that mappings are consistent across requests"""
        # Get a concept map twice and ensure results are identical
        list_response = client.get("/ConceptMap")
        available_codes = list_response.json()["available_codes"]
        test_code = available_codes[0]
        
        response1 = client.get(f"/ConceptMap/{test_code}")
        response2 = client.get(f"/ConceptMap/{test_code}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Compare the core mapping data (excluding dynamic fields like timestamps)
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["resourceType"] == data2["resourceType"]
        assert data1["status"] == data2["status"]
        assert len(data1["group"]) == len(data2["group"])
        
        # Compare mappings
        group1 = data1["group"][0]
        group2 = data2["group"][0]
        assert len(group1["element"]) == len(group2["element"])

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])