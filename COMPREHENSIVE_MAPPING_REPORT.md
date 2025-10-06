# NAMASTE-ICD-11 Comprehensive Mapping Report

## 📊 Mapping Statistics (as of 2025-10-06)

- **Total concept map rows:** 468
  - 218 `equivalent`
  - 250 `relatedto`
- **Unique NAMASTE codes:** 296
- **Unique ICD-11 TM2 codes:** 437
- **Source data:** `db/ayush_icd11_combined.db` populated by `scripts/create_concept_map.py`

## 🔍 Mapping Strategy Implementation

The current pipeline favours high-confidence matches over breadth. `create_precise_mappings` executes a five-pass workflow:

1. **Exact code alignment** – joins `nam_fts` to `icd11_fts` where codes are identical.
2. **Bracket trimming** – matches canonical fragments such as `SR11` extracted from labels like `SR11 (AAA-1)`.
3. **Simple FTS lookups** – performs single-token searches on `icd11_fts.title` for short English nouns.
4. **Exact English title parity** – compares cleaned English titles between `nam` and `icd11` base tables.
5. **Bounded partial matches** – captures additional descriptive overlaps via `LIKE` while limiting volume (cap 150).

Example excerpt from the SQL-driven workflow:

```sql
-- Exact code alignment
INSERT INTO concept_map (...)
SELECT 'NAMASTE', n.namc_code, 'ICD-11 TM2', i.code, 'equivalent'
FROM nam_fts n
JOIN icd11_fts i ON n.namc_code = i.code;

-- Bracket trimming
JOIN icd11_fts i ON TRIM(SUBSTR(n.namc_code, 1, CASE
    WHEN INSTR(n.namc_code, ' (') > 0 THEN INSTR(n.namc_code, ' (') - 1
    ELSE LENGTH(n.namc_code)
END)) = TRIM(i.code);
```

Deduplication guards (`NOT EXISTS` checks) ensure each source/target pair is inserted once across all passes.

## 📈 Coverage Highlights

### Top NAMASTE prefixes by mapping volume

| Prefix | Total Mappings | Unique NAMASTE Codes |
| ------ | -------------- | -------------------- |
| ED     | 151            | 6                    |
| SM     | 82             | 80                   |
| SK     | 62             | 62                   |
| SN     | 40             | 40                   |
| SP     | 33             | 28                   |
| SR     | 24             | 24                   |
| SS     | 19             | 19                   |
| SL     | 19             | 17                   |
| EC     | 19             | 2                    |
| SQ     | 13             | 13                   |

### Relationship mix

- **Equivalent pairs (218):** Strong lexical/code agreement, ideal for automated dual coding.
- **Related pairs (250):** Useful anchors where ICD-11 descriptors contextualise Ayurvedic observations.

### Some mappings

| NAMASTE code | ICD-11 TM2 code | Relationship |
| ------------ | ---------------- | ------------ |
| `SR11 (AAA-1)` | `SR11` | equivalent |
| `SM33(EB-10)`  | `SM33` | relatedto |
| `ED-14`        | `EB01.1` | relatedto |
| `SK84 (AAB-15)`| `SK84` | equivalent |
| `EC-7`         | `6B80.0` | relatedto |

## 🔧 Technical Infrastructure

- **FTS5 indexes:** `nam_fts`, `icd11_fts`, and companions accelerate lookups.
- **Whitespace normalization:** `normalize_database.py` enforces consistent code formatting.
- **Export utilities:** `scripts/export_mappings.py` produces CSV + summary + sampled datasets for review.
- **Analytics:** Summary files report prefix breakdowns, unique counts, and top-mapped codes.

## 🧪 Quality Assurance

- Duplicate suppression via `NOT EXISTS` checks in each insertion block.
- Validation queries in `scripts/init.py` verify table availability and mapping counts after generation.
- Test suite (`tests/run_tests.py`) covers database connectivity, ConceptMap structure, and API surface behaviour.

## 🛠️ Reproducing Results

1. Run the initializer:
   ```bash
   python scripts/init.py
   ```
2. Regenerate mappings independently (optional):
   ```bash
   python scripts/create_concept_map.py
   ```
3. Export audit artefacts:
   ```bash
   python scripts/export_mappings.py
   ```

Outputs are written to `db/` and `output/` with timestamped filenames for traceability.

## 📣 Notes & Next Steps

- Expansion to additional prefixes can be layered on by adjusting pass five or adding bespoke passes.
- Manual review is recommended for the 250 `relatedto` records prior to strict clinical adoption.
- Performance: current pipeline completes in ~5 minutes on macOS (single-threaded SQLite processing).
- Supports bidirectional lookup and translation



## 🚀 Future Capabilities
