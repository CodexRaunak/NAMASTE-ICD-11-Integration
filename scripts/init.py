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

#Indexing NAMASTE ayurveda Morbidity
index_csv_to_sqlite(
    csv_path="data/namaste_ayurveda_morbidity.csv",
    db_path=DB_PATH,
    table_name="nam",
    fts_table_name="nam_fts",
    fts_columns=["namc_code", "namc_term", "long_definition"]

)