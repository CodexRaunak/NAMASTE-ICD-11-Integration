#!/usr/bin/env python3
"""
Normalize spaces in the concept_map source_code field
"""
import sqlite3
import re

DB_PATH = "db/ayush_icd11_combined.db"

def normalize_spaces_in_database():
    """Clean up inconsistent spacing in source_code field"""
    print("NORMALIZING SPACES IN CONCEPT_MAP DATABASE")
    print("="*50)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # First, show current spacing issues
    print("\n1. Current spacing patterns:")
    cur.execute("SELECT DISTINCT source_code FROM concept_map ORDER BY source_code")
    codes = [row[0] for row in cur.fetchall()]
    for code in codes:
        print(f"  '{code}' (length: {len(code)})")
    
    # Normalize the spacing using Python
    print(f"\n2. Normalizing spaces...")
    
    # Get all records
    cur.execute("SELECT id, source_code FROM concept_map")
    all_records = cur.fetchall()
    
    updated_count = 0
    for record_id, source_code in all_records:
        # Normalize: replace multiple spaces with single space, trim
        normalized = re.sub(r'\s+', ' ', source_code.strip())
        
        if normalized != source_code:
            cur.execute("UPDATE concept_map SET source_code = ? WHERE id = ?", (normalized, record_id))
            updated_count += 1
            print(f"  Updated: '{source_code}' → '{normalized}'")
    
    print(f"Updated {updated_count} rows")
    
    # Show results
    print(f"\n3. After normalization:")
    cur.execute("SELECT DISTINCT source_code FROM concept_map ORDER BY source_code")
    codes = [row[0] for row in cur.fetchall()]
    for code in codes:
        print(f"  '{code}' (length: {len(code)})")
    
    # Test SR10 specifically
    print(f"\n4. Testing SR10 after normalization:")
    cur.execute("SELECT source_code, target_code FROM concept_map WHERE source_code LIKE '%SR10%'")
    sr10_rows = cur.fetchall()
    for row in sr10_rows[:3]:  # Show first 3
        print(f"  {row[0]} → {row[1]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database normalization complete!")
    print(f"💡 All codes should now have consistent single-space formatting")

if __name__ == "__main__":
    normalize_spaces_in_database()