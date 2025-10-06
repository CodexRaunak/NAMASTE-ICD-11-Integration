import sqlite3
from typing import List, Tuple


def _normalize_code_text(value: str) -> str:
    """Collapse whitespace (including NBSP) to single ASCII spaces."""
    if value is None:
        return value
    # Replace non-breaking spaces, collapse runs, and trim
    normalized = " ".join(value.replace("\u00A0", " ").split())
    return normalized

DB_PATH = "db/ayush_icd11_combined.db"

def create_concept_map_table(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS concept_map (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_system TEXT NOT NULL,
        source_code TEXT NOT NULL,
        target_system TEXT NOT NULL,
        target_code TEXT NOT NULL,
        equivalence TEXT DEFAULT 'equivalent'
    )
    """)
    conn.commit()
    conn.close()

def create_precise_mappings(db_path: str = DB_PATH):
    """Create precise 1-to-1 mappings using code matching and English titles with FTS indexes"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Clear existing mappings to prevent duplicates
    print("Clearing existing concept mappings...")
    cur.execute("DELETE FROM concept_map")
    
    print("Creating precise NAMASTE to ICD-11 mappings using FTS indexes...")
    
    # Strategy 1: Exact code matches using FTS indexes (fastest and most reliable)
    print("Step 1: Finding exact code matches using FTS indexes...")
    cur.execute("""
    INSERT INTO concept_map (source_system, source_code, target_system, target_code, equivalence)
    SELECT DISTINCT 'NAMASTE', n.namc_code, 'ICD-11 TM2', i.code, 'equivalent'
    FROM nam_fts n
    JOIN icd11_fts i ON n.namc_code = i.code
    WHERE n.namc_code IS NOT NULL 
      AND i.code IS NOT NULL
      AND i.code != ''
    """)
    exact_code_matches = cur.rowcount
    
    # Strategy 2: Code matching before brackets using FTS indexes
    print("Step 2: Finding code matches before brackets using FTS indexes...")
    cur.execute("""
    INSERT INTO concept_map (source_system, source_code, target_system, target_code, equivalence)
    SELECT DISTINCT 'NAMASTE', n.namc_code, 'ICD-11 TM2', i.code, 'equivalent'
    FROM nam_fts n
    JOIN icd11_fts i ON TRIM(SUBSTR(n.namc_code, 1, CASE 
        WHEN INSTR(n.namc_code, ' (') > 0 THEN INSTR(n.namc_code, ' (') - 1
        ELSE LENGTH(n.namc_code)
    END)) = TRIM(i.code)
    WHERE n.namc_code IS NOT NULL 
      AND i.code IS NOT NULL
      AND i.code != ''
      AND INSTR(n.namc_code, ' (') > 0
      AND NOT EXISTS (
        SELECT 1 FROM concept_map cm 
        WHERE cm.source_code = n.namc_code AND cm.target_code = i.code
    )
    """)
    bracket_code_matches = cur.rowcount
    
    # Strategy 3: Simple FTS search for single-word English terms
    print("Step 3: Finding simple English word matches using FTS...")
    cur.execute("""
    INSERT INTO concept_map (source_system, source_code, target_system, target_code, equivalence)
    SELECT DISTINCT 'NAMASTE', n.namc_code, 'ICD-11 TM2', i.code, 'relatedto'
    FROM nam n
    JOIN icd11_fts i ON i.title MATCH n.name_english
    WHERE n.name_english IS NOT NULL 
      AND n.name_english != ''
      AND LENGTH(TRIM(n.name_english)) > 3
      AND LENGTH(TRIM(n.name_english)) < 20  -- Simple terms only
      AND INSTR(n.name_english, ' ') = 0     -- Single words only
      AND INSTR(n.name_english, '/') = 0     -- No special chars
      AND INSTR(n.name_english, '-') = 0     -- No special chars
      AND i.code IS NOT NULL
      AND i.code != ''
      AND NOT EXISTS (
        SELECT 1 FROM concept_map cm 
        WHERE cm.source_code = n.namc_code AND cm.target_code = i.code
    )
    LIMIT 100
    """)
    fts_simple_matches = cur.rowcount
    
    # Strategy 4: Direct English title comparison (no FTS to avoid syntax issues)
    print("Step 4: Finding direct English title matches...")
    cur.execute("""
    INSERT INTO concept_map (source_system, source_code, target_system, target_code, equivalence)
    SELECT DISTINCT 'NAMASTE', n.namc_code, 'ICD-11 TM2', i.code, 'equivalent'
    FROM nam n
    JOIN icd11 i ON (
        (n.name_english IS NOT NULL AND LOWER(TRIM(n.name_english)) = LOWER(TRIM(i.title)))
        OR (n.name_english_under_index IS NOT NULL AND LOWER(TRIM(n.name_english_under_index)) = LOWER(TRIM(i.title)))
    )
    WHERE ((n.name_english IS NOT NULL AND n.name_english != '') 
           OR (n.name_english_under_index IS NOT NULL AND n.name_english_under_index != ''))
      AND i.title IS NOT NULL
      AND i.code IS NOT NULL
      AND i.code != ''
      AND NOT EXISTS (
        SELECT 1 FROM concept_map cm 
        WHERE cm.source_code = n.namc_code AND cm.target_code = i.code
    )
    """)
    direct_english_matches = cur.rowcount
    
    # Strategy 5: Partial English matching (limited to avoid performance issues)
    print("Step 5: Finding partial English matches...")
    cur.execute("""
    INSERT INTO concept_map (source_system, source_code, target_system, target_code, equivalence)
    SELECT DISTINCT 'NAMASTE', n.namc_code, 'ICD-11 TM2', i.code, 'relatedto'
    FROM nam n
    JOIN icd11 i ON (
        n.name_english IS NOT NULL 
        AND LENGTH(TRIM(n.name_english)) > 5 
        AND LENGTH(TRIM(n.name_english)) < 30
        AND LOWER(i.title) LIKE '%' || LOWER(TRIM(n.name_english)) || '%'
    )
    WHERE n.name_english IS NOT NULL 
      AND n.name_english != ''
      AND i.title IS NOT NULL
      AND i.code IS NOT NULL
      AND i.code != ''
      AND NOT EXISTS (
        SELECT 1 FROM concept_map cm 
        WHERE cm.source_code = n.namc_code AND cm.target_code = i.code
    )
    LIMIT 150
    """)
    partial_english_matches = cur.rowcount

    # Normalize whitespace artifacts introduced during insertion
    print("Normalizing whitespace artifacts in concept_map codes...")
    cur.execute("SELECT id, source_code, target_code FROM concept_map")
    updated_rows = 0
    for row_id, source_code, target_code in cur.fetchall():
        normalized_source = _normalize_code_text(source_code)
        normalized_target = _normalize_code_text(target_code)
        if normalized_source != source_code or normalized_target != target_code:
            cur.execute(
                "UPDATE concept_map SET source_code = ?, target_code = ? WHERE id = ?",
                (normalized_source, normalized_target, row_id),
            )
            updated_rows += 1
    if updated_rows:
        print(f"  - Normalized whitespace on {updated_rows} rows")
    
    # Get final counts
    cur.execute("SELECT COUNT(*) FROM concept_map WHERE equivalence = 'equivalent'")
    equivalent_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM concept_map WHERE equivalence = 'relatedto'")
    related_count = cur.fetchone()[0]
    
    total_mappings = equivalent_count + related_count
    
    print(f"  - Exact code matches (FTS): {exact_code_matches}")
    print(f"  - Code matches before brackets (FTS): {bracket_code_matches}")
    print(f"  - Simple FTS word matches: {fts_simple_matches}")
    print(f"  - Direct English matches: {direct_english_matches}")
    print(f"  - Partial English matches: {partial_english_matches}")
    print(f"  - Total equivalent mappings: {equivalent_count}")
    print(f"  - Total related mappings: {related_count}")
    print(f"Created {total_mappings} total concept mappings using FTS indexes.")
    
    conn.commit()
    conn.close()
    return total_mappings

if __name__ == "__main__":
    create_concept_map_table()
    mappings_count = create_precise_mappings()
    print(f"concept_map table created and populated with {mappings_count} mappings.")
    
    # Print sample mappings (not all to avoid overwhelming output)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("SAMPLE CONCEPT MAPPINGS (by equivalence type)")
    print("="*80)
    
    for equiv_type in ['equivalent', 'relatedto', 'wider']:
        cur.execute("""
        SELECT source_code, target_code, equivalence 
        FROM concept_map 
        WHERE equivalence = ? 
        LIMIT 5
        """, (equiv_type,))
        
        samples = cur.fetchall()
        if samples:
            print(f"\n{equiv_type.upper()} mappings:")
            for source_code, target_code, equivalence in samples:
                print(f"  {source_code} -> {target_code} ({equivalence})")
    
    conn.close()
