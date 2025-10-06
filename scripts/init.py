#!/usr/bin/env python3
"""
Complete NAMASTE-ICD-11 Integration Setup Script
This script performs all necessary initialization steps:
1. Downloads datasets
2. Creates database and indexes
3. Normalizes data
4. Generates comprehensive concept mappings
"""

import os
import sys
from datetime import datetime

def print_step(step_num, description):
    """Print a formatted step indicator"""
    print(f"\n🔧 STEP {step_num}: {description}")
    print("=" * 60)

def run_step(description, func, *args, **kwargs):
    """Run a step with error handling"""
    try:
        print(f"▶️  {description}...")
        result = func(*args, **kwargs)
        print(f"✅ {description} completed successfully")
        return result
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        sys.exit(1)

def main():
    """Main initialization workflow"""
    print("🚀 NAMASTE-ICD-11 INTEGRATION SETUP")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This script will set up the complete NAMASTE-ICD-11 integration system.")
    
    # Import required modules
    from download_icd11 import download_icd11
    from download_namaste import download_namaste
    from create_database import index_csv_to_sqlite
    from normalize_database import normalize_spaces_in_database
    from create_concept_map import create_concept_map_table, create_precise_mappings
    
    DB_PATH = "db/ayush_icd11_combined.db"
    
    # Step 1: Download datasets
    print_step(1, "DOWNLOADING DATASETS")
    run_step("Downloading ICD-11 TM2 dataset", download_icd11)
    run_step("Downloading NAMASTE datasets", download_namaste)
    
    # Step 2: Create database and indexes
    print_step(2, "CREATING DATABASE AND INDEXES")
    
    # Create database directory
    os.makedirs("db", exist_ok=True)
    
    # Index ICD-11 TM2
    run_step(
        "Indexing ICD-11 TM2 data",
        index_csv_to_sqlite,
        csv_path="data/ICD-11.csv",
        db_path=DB_PATH,
        table_name="icd11",
        fts_table_name="icd11_fts",
        fts_columns=["code", "title"]
    )
    
    # Index NAMASTE Ayurveda Morbidity (primary focus)
    run_step(
        "Indexing NAMASTE Ayurveda Morbidity data",
        index_csv_to_sqlite,
        csv_path="data/namaste_ayurveda_morbidity.csv",
        db_path=DB_PATH,
        table_name="nam",
        fts_table_name="nam_fts",
        fts_columns=["namc_code","namc_term", "long_definition"]
    )
    
    # Index NAMASTE Siddha Morbidity
    run_step(
        "Indexing NAMASTE Siddha Morbidity data",
        index_csv_to_sqlite,
        csv_path="data/namaste_siddha_morbidity.csv",
        db_path=DB_PATH,
        table_name="nsm",
        fts_table_name="nsm_fts",
        fts_columns=["namc_code", "namc_term", "short_definition"]
    )
    
    # Index NAMASTE Unani Morbidity
    run_step(
        "Indexing NAMASTE Unani Morbidity data",
        index_csv_to_sqlite,
        csv_path="data/namaste_unani_morbidity.csv",
        db_path=DB_PATH,
        table_name="num",
        fts_table_name="num_fts",
        fts_columns=["numc_code", "short_definition"]
    )
    
    # Index Ayurveda Standard Terminology
    run_step(
        "Indexing Ayurveda Standard Terminology data",
        index_csv_to_sqlite,
        csv_path="data/ayurveda_standard_terminology.csv",
        db_path=DB_PATH,
        table_name="ast",
        fts_table_name="ast_fts",
        fts_columns=["code","parent_id","word","short_defination"]
    )
    
    # Step 3: Normalize database
    print_step(3, "NORMALIZING DATABASE")
    run_step("Normalizing spacing and formatting", normalize_spaces_in_database)
    
    # Step 4: Generate concept mappings
    print_step(4, "GENERATING COMPREHENSIVE CONCEPT MAPPINGS")
    run_step("Creating concept mapping table", create_concept_map_table)
    mapping_count = run_step("Generating mappings", create_precise_mappings)
    print(f"✅ Generated {mapping_count:,} concept mappings")
    
    # Step 5: Verify setup
    print_step(5, "VERIFYING SETUP")
    
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    expected_tables = ["icd11", "nam", "nsm", "num", "ast", "concept_map", 
                      "icd11_fts", "nam_fts", "nsm_fts", "num_fts", "ast_fts"]
    
    for table in expected_tables:
        if table in tables:
            print(f"✅ Table '{table}' created successfully")
        else:
            print(f"❌ Table '{table}' missing")
    
    # Check concept mappings
    cur.execute("SELECT COUNT(*) FROM concept_map")
    mapping_count = cur.fetchone()[0]
    print(f"✅ Generated {mapping_count:,} concept mappings")
    
    # Check unique codes
    cur.execute("SELECT COUNT(DISTINCT source_code) FROM concept_map")
    unique_namaste = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT target_code) FROM concept_map")
    unique_icd11 = cur.fetchone()[0]
    
    print(f"✅ Mapped {unique_namaste:,} unique NAMASTE codes")
    print(f"✅ Targeting {unique_icd11:,} unique ICD-11 codes")
    
    conn.close()
    
    # Final success message
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("✅ All datasets downloaded and indexed")
    print("✅ Database normalized and optimized") 
    print("✅ Comprehensive concept mappings generated")
    print("✅ FHIR-compliant API ready to start")
    print("\n📋 NEXT STEPS:")
    print("1. Run tests: python tests/run_tests.py")
    print("2. Start API: uvicorn app.main:app --reload")
    print("3. View API docs: http://localhost:8000/docs")
    print("4. Export mappings: python scripts/export_mappings.py")
    print(f"\n⏱️  Setup completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
from download_icd11 import download_icd11
from download_namaste import download_namaste
from create_database import index_csv_to_sqlite

DB_PATH = "db/ayush_icd11_combined.db"

# Downloading datasets
download_icd11()
download_namaste()

# Indexing ICD-11
index_csv_to_sqlite(
    csv_path="data/ICD-11.csv",
    db_path=DB_PATH,
    table_name="icd11",
    fts_table_name="icd11_fts",
    fts_columns=["code", "title"]
)

# Indexing NAMASTE Siddha Morbidity
index_csv_to_sqlite(
    csv_path="data/namaste_siddha_morbidity.csv",
    db_path=DB_PATH,
    table_name="nsm",
    fts_table_name="nsm_fts",
    fts_columns=["namc_code", "namc_term", "short_definition"]
)

#Indexing NAMASTE Unani Morbidity
index_csv_to_sqlite(
    csv_path="data/namaste_unani_morbidity.csv",
    db_path=DB_PATH,
    table_name="num",
    fts_table_name="num_fts",
    fts_columns=["numc_code", "short_definition"]
)

#Indexing NAMASTE Ayurveda Morbidity
index_csv_to_sqlite(
    csv_path="data/namaste_ayurveda_morbidity.csv",
    db_path=DB_PATH,
    table_name="nam",
    fts_table_name="nam_fts",
    fts_columns=["namc_code","namc_term", "short_definition"]
)


#Indexing Ayurveda Standard terminology
index_csv_to_sqlite(
    csv_path="data/ayurveda_standard_terminology.csv",
    db_path=DB_PATH,
    table_name="ast",
    fts_table_name="ast_fts",
    fts_columns=["code","parent_id","word","short_defination"]
)
#indexing  siddha Standard Terminology
index_csv_to_sqlite(
    csv_path="data/siddha_standard_terminology.csv",
    db_path=DB_PATH,
    table_name="sst",
    fts_table_name="sst_fts",
    fts_columns=["code_no.","terminology in the original Language - Siddha Term","Transliteration (Diacritic code)","DESCRIPTION"]
)
#indexing  siddha Standard Terminology index 
index_csv_to_sqlite(
    csv_path="data/siddha_standard_terminology_index.csv",
    db_path=DB_PATH,
    table_name="isst",
    fts_table_name="isst_fts",
    fts_columns=["english_term","code_no.","page._no."]
)
#indexing  unani Standard Terminology 
index_csv_to_sqlite(
    csv_path="data/unani_standard_terminology.csv",
    db_path=DB_PATH,
    table_name="ust",
    fts_table_name="ust_fts",
    fts_columns=["CODE","TERM","TRANSLITERATION","DESCRIPTION"]
)
#indexing  unani Standard Terminology index
index_csv_to_sqlite(
    csv_path="data/unani_standard_terminology_index.csv",
    db_path=DB_PATH,
    table_name="iust",
    fts_table_name="iust_fts",
    fts_columns=[""]
)