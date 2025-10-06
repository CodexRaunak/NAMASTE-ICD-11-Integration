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