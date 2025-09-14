import pandas as pd
import sqlite3
import os

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def clean_column_names(columns):
    return [col.strip().replace(" ", "_").replace(":", "_").lower() for col in columns]

def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", 
        (table_name,)
    )
    return cursor.fetchone() is not None

def index_csv_to_sqlite(
    csv_path,
    db_path,
    table_name,
    fts_table_name=None,
    fts_columns=None
):
    """General-purpose function to index a CSV into SQLite with optional FTS5."""
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print(f"Importing {csv_path} into {db_path}...")

    df = pd.read_csv(csv_path)
    df.columns = clean_column_names(df.columns)

    conn = create_connection(db_path)
    if not conn:
        return
    cursor = conn.cursor()

    # Create main table if not exists, else append data
    if table_exists(cursor, table_name):
        print(f"Table '{table_name}' exists. Appending data...")
        df.to_sql(table_name, conn, if_exists="append", index=False)
    else:
        print(f"Creating table '{table_name}' and importing data...")
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    # Optional FTS5 indexing
    if fts_columns and fts_table_name:
        if table_exists(cursor, fts_table_name):
            print(f"FTS5 virtual table '{fts_table_name}' already exists. Skipping creation.")
        else:
            print(f"Creating FTS5 virtual table '{fts_table_name}' on columns: {fts_columns}")
            columns_sql = ", ".join(fts_columns)
            cursor.execute(f"""
                CREATE VIRTUAL TABLE {fts_table_name} USING fts5(
                    {columns_sql},
                    content='{table_name}',
                    content_rowid='rowid'
                )
            """)
            columns_select = ", ".join(fts_columns)
            cursor.execute(f"""
                INSERT INTO {fts_table_name}({columns_select})
                SELECT {columns_select} FROM {table_name}
            """)
            print(f"FTS5 index '{fts_table_name}' created and populated.")

    conn.commit()
    conn.close()
    print(f"Done importing {csv_path} into DB '{db_path}'🐬")
