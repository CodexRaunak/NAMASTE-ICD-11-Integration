# Tests Directory

This directory contains comprehensive tests for the NAMASTE-ICD-11 Integration service.

## Test Files

### `test_logic.py`
- **Business Logic Tests**: Tests core functionality, database operations, and concept mapping logic
- Tests database connectivity, data quality, mapping consistency
- Validates Ayurveda vāta pattern mappings and code normalization

### `test_fhir.py` 
- **FHIR Compliance Tests**: Ensures FHIR R4 ConceptMap specification compliance
- Tests ConceptMap structure, Bundle responses, and terminology service patterns
- Validates JSON serialization and FHIR resource metadata

### `test_api.py`
- **API Integration Tests**: Tests FastAPI endpoints using TestClient
- Tests HTTP responses, error handling, and URL encoding
- Validates API performance and consistency (requires pytest)

### `run_tests.py`
- **Test Runner**: Executes all tests and provides comprehensive reporting
- Runs both business logic and FHIR compliance test suites
- Provides summary of test results

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Individual Test Suites
```bash
# Business logic tests
python tests/test_logic.py

# FHIR compliance tests  
python tests/test_fhir.py

# API tests (requires pytest)
python tests/test_api.py
```

### With Pytest (if available)
```bash
pytest tests/ -v
```

## Test Coverage

The test suite covers:
- ✅ Database connectivity and schema validation
- ✅ Concept mapping data quality and consistency
- ✅ FHIR R4 ConceptMap specification compliance
- ✅ API endpoint functionality and error handling
- ✅ URL encoding and special character handling
- ✅ JSON serialization and deserialization
- ✅ Ayurveda terminology mapping accuracy
- ✅ Service performance and reliability

## Test Data

Tests use the actual database (`db/ayush_icd11_combined.db`) to ensure real-world functionality.
No test fixtures or mock data are used - tests validate the actual service behavior.