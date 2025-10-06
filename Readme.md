# NAMASTE-ICD-11 Integration API

A **FHIR R4-compliant terminology micro-service** that integrates India's NAMASTE (National AYUSH Morbidity & Standardized Terminologies Electronic) codes with WHO's ICD-11 Traditional Medicine Module 2 (TM2), enabling seamless interoperability between traditional and modern healthcare systems.

## 🎯 Problem Statement

**ID:** 25026  
**Organization:** Ministry of Ayush  
**Department:** All India Institute of Ayurveda (AIIA)

Develop API code to integrate NAMASTE and the International Classification of Diseases (ICD-11) via the Traditional Medicine Module 2 (TM2) into existing EMR systems that comply with Electronic Health Record (EHR) Standards for India.

## 🚀 Key Features

- **468 curated concept mappings** — 218 high-confidence equivalent matches + 250 clinically helpful related associations
- **FHIR R4 compliant** ConceptMap resources with explicit equivalence flags
- **Targeted domain coverage** focusing on SR, ED, SM, SK, SN, SP, SL, SS, and EC prefixes in the NAMASTE corpus
- **FTS5-backed lookups** for fast crosswalk exploration across both terminologies
- **End-to-end automation** via `scripts/init.py`, exports, and regression tests

## 📊 Mapping Coverage

- **Total mappings:** 468 (218 equivalent, 250 related)
- **Unique NAMASTE codes represented:** 296
- **Unique ICD-11 TM2 codes linked:** 437
- **Top prefixes (by mapping volume):** ED, SM, SK, SN, SP, SR, SS, SL, EC, SQ
- **Curation philosophy:** Prefer precise 1:1 code & title agreements and limit broader fuzzy expansion to reviewable "related" links

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/CodexRaunak/NAMASTE-ICD-11-Integration.git
   cd NAMASTE-ICD-11-Integration
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the complete setup**
   ```bash
   python scripts/init.py
   ```

   This orchestrator will:
   - ✅ Download NAMASTE and ICD-11 TM2 datasets
   - ✅ Create the optimized SQLite database with FTS5 indexes
   - ✅ Normalize code formatting and spacing
   - ✅ Generate 468 curated concept mappings (218 equivalent + 250 related)
   - ✅ Verify the installation and print next steps

## 🧪 Verification & Testing

### Run the complete test suite
```bash
python tests/run_tests.py
```

This validates:
- Database connectivity, schema integrity, and FTS index availability
- Concept mapping precision and equivalence tagging
- FHIR R4 ConceptMap compliance and serialization
- REST API behaviour, URL encoding, and error handling

### Start the API server
```bash
uvicorn app.main:app --reload
```

Interactive docs: http://localhost:8000/docs

### Export mappings for review
```bash
python scripts/export_mappings.py
```

Generates:
- `output/namaste_icd11_mappings_[timestamp].csv` — Full export (468 rows as of 2025-10-06)
- `output/namaste_icd11_mappings_[timestamp]_summary.txt` — Snapshot statistics and prefix breakdown
- `output/namaste_icd11_sample_[timestamp].csv` — Sample set (up to 10 mappings per NAMASTE prefix)

## 🔗 API Endpoints

### ConceptMap resources
```http
GET /ConceptMap                    # List all concept maps
GET /ConceptMap/{code}             # Get mappings for a specific NAMASTE code
```

### Example usage
```bash
# Fetch mappings for an Ayurvedic vāta pattern
curl "http://localhost:8000/ConceptMap/SR10%20(AAA-2.1)"

# Fetch mappings for an examination finding
curl "http://localhost:8000/ConceptMap/ED-6.10"
```

### FHIR response structure
```json
{
  "resourceType": "ConceptMap",
  "id": "namaste-icd11-conceptmap",
  "url": "http://terminology.ayush.gov.in/ConceptMap/namaste-icd11",
  "version": "1.0.0",
  "name": "NAMASTE_ICD11_ConceptMap",
  "title": "NAMASTE to ICD-11 TM2 Concept Map",
  "status": "active",
  "group": [
    {
      "source": "http://terminology.ayush.gov.in/CodeSystem/namaste",
      "target": "http://id.who.int/icd/entity",
      "element": [
        {
          "code": "ED-6.10",
          "target": [
            {
              "code": "ED00",
              "equivalence": "equivalent"
            }
          ]
        }
      ]
    }
  ]
}
```

## Contribution Guide

- Create a virtual environment
- Install the dependencies from `requirements.txt`
- Run `python scripts/init.py`

## 🏗️ Project Architecture

### Directory structure
```
NAMASTE-ICD-11-Integration/
├── app/                    # FastAPI application
│   ├── main.py             # API entry point
│   └── conceptmap.py       # FHIR ConceptMap endpoints
├── data/                   # CSV datasets (auto-downloaded)
├── db/                     # SQLite database (auto-created)
├── output/                 # Generated mapping exports
├── scripts/                # Setup and utility scripts
├── tests/                  # Test suite
└── requirements.txt        # Python dependencies
```

### Database schema
- **`icd11`** — ICD-11 TM2 codes and titles
- **`nam`** — NAMASTE Ayurveda morbidity codes
- **`nsm` / `num` / `ast`** — Additional NAMASTE datasets with FTS mirrors
- **`concept_map`** — Curated NAMASTE ↔ ICD-11 mappings
- **`*_fts`** — FTS5 virtual tables supporting indexed lookups

## 🔬 Technical Details

### Mapping strategy
A five-pass curation workflow prioritizes precision:

1. **Exact code alignment** — Captures identical code pairs between NAMASTE and ICD-11.
2. **Bracket trimming** — Matches canonical codes inside labels such as `SR11 (AAA-1)`.
3. **Single-token FTS lookups** — Uses `icd11_fts` for safe English keyword matching on concise terms.
4. **Exact English title parity** — Links entries that publish identical English titles in both systems.
5. **Capped partial matches** — Adds a bounded number of related associations for overlapped language without diluting quality.

This produces 218 equivalent links and 250 related associations that remain human-auditable.

### Performance optimizations
- **FTS5 full-text search** for both NAMASTE and ICD-11 datasets
- **Code normalization and whitespace cleanup** to keep join keys deterministic
- **Deduplication guards** so later passes skip previously captured pairs
- **Automated CSV & summary exports** to streamline governance review cycles

### FHIR compliance
- Proper ConceptMap scaffolding with `equivalent` and `relatedto` designations
- URL-safe code handling across REST endpoints
- JSON serialization aligned with FHIR R4 expectations

## 🎯 Clinical Impact

- **Traditional medicine patterns (SR/SM/SK/SN/SP/SS)** enjoy direct equivalence with their ICD-11 complements where lexical agreement exists.
- **Examination findings (ED & EC)** surface rich related ICD-11 descriptors to contextualize Ayurvedic observations.
- **Transparent semantics:** Equivalence vs. related relationships are explicit so downstream systems can apply governance policies.

## 🔧 Advanced Usage

### Custom mapping regeneration
```bash
python scripts/create_concept_map.py
```

### Helpful SQL queries
```sql
-- Count mappings by NAMASTE prefix
SELECT SUBSTR(source_code, 1, 2) AS prefix, COUNT(*)
FROM concept_map
GROUP BY prefix
ORDER BY COUNT(*) DESC;

-- Inspect mappings for a specific code
SELECT *
FROM concept_map
WHERE source_code = 'SR11 (AAA-1)';
```

### Integration example: EMR lookup
```python
import requests

concept_map = requests.get(
    "http://localhost:8000/ConceptMap/SR10%20(AAA-2.1)"
).json()

icd11_codes = [
    target["code"]
    for group in concept_map["group"]
    for element in group["element"]
    for target in element["target"]
]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/name`
3. Implement changes and add tests where relevant
4. Run `python tests/run_tests.py`
5. Submit a pull request

## 📄 License

Developed for the Ministry of Ayush, All India Institute of Ayurveda (AIIA) as part of the digital health transformation initiative.

## 🆘 Troubleshooting

### Common issues
- **Database not found:** Run `python scripts/init.py`
- **Import errors:** Activate the virtual environment and reinstall requirements
- **Test failures:** Re-run the initializer to rebuild the SQLite database and refresh mappings
- **API errors:** Ensure FastAPI and Uvicorn are installed (`pip install fastapi uvicorn`)

### Support
Consult the test suite, summary exports, and this documentation for guidance when reviewing or extending the mapping set.
