import sqlite3

DB_PATH = "db/ayush_icd11_combined.db"

def examine_data_closer():
    """Look at the actual data more closely"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("DETAILED DATA EXAMINATION")
    print("="*80)
    
    # Look for any English-like terms in NAMASTE
    print("\n1. Looking for English-like terms in NAMASTE data:")
    cur.execute("""
        SELECT namc_code, namc_term 
        FROM nam 
        WHERE namc_term NOT LIKE '%~%' 
        AND namc_term NOT LIKE '%H'
        AND LENGTH(namc_term) > 3
        ORDER BY namc_term
        LIMIT 20
    """)
    
    rows = cur.fetchall()
    print(f"Found {len(rows)} potentially English-like terms:")
    for code, term in rows:
        if code and term:
            print(f"  {code}: {term}")
    
    # Look for common medical terms
    print(f"\n2. Looking for common medical terms in NAMASTE:")
    common_terms = ['fever', 'pain', 'infection', 'disease', 'disorder', 'syndrome']
    
    for term in common_terms:
        cur.execute("""
            SELECT namc_code, namc_term 
            FROM nam 
            WHERE LOWER(namc_term) LIKE ?
        """, (f'%{term}%',))
        
        matches = cur.fetchall()
        if matches:
            print(f"  Terms containing '{term}': {len(matches)}")
            for code, match_term in matches[:3]:
                if code and match_term:
                    print(f"    {code}: {match_term}")
    
    # Look at ICD-11 structure
    print(f"\n3. ICD-11 data structure:")
    cur.execute("SELECT code, title FROM icd11 WHERE code IS NOT NULL LIMIT 15")
    icd_rows = cur.fetchall()
    print("Sample ICD-11 entries:")
    for code, title in icd_rows:
        if code and title:
            print(f"  {code}: {title}")
    
    # Check if there are any partial matches
    print(f"\n4. Looking for partial word matches:")
    cur.execute("""
        SELECT n.namc_code, n.namc_term, i.code, i.title
        FROM nam n
        CROSS JOIN icd11 i
        WHERE i.title IS NOT NULL 
        AND n.namc_term IS NOT NULL
        AND (
            LOWER(i.title) LIKE '%' || LOWER(n.namc_term) || '%'
            OR LOWER(n.namc_term) LIKE '%' || LOWER(i.title) || '%'
        )
        LIMIT 10
    """)
    
    partial_matches = cur.fetchall()
    if partial_matches:
        print(f"Found {len(partial_matches)} partial matches:")
        for namc_code, namc_term, icd_code, icd_title in partial_matches:
            print(f"  NAMASTE: {namc_code} - {namc_term}")
            print(f"  ICD-11:  {icd_code} - {icd_title}")
            print()
    else:
        print("No partial matches found either.")
    
    conn.close()

if __name__ == "__main__":
    examine_data_closer()