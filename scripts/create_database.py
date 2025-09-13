import pandas as pd
import sqlite3
import os

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}")
    except sqlite3.Error as e:
        print(e)
    return conn

# Define paths
DB_PATH = 'db/ICD11.db'
CSV_PATH = 'data/ICD-11.csv'

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

if not os.path.exists(DB_PATH):
    print("Creating SQLite DB and importing data...")

    # Load the CSV file into a DataFrame
    df = pd.read_csv(CSV_PATH)

    # Clean column names: replace spaces with underscores, remove colons
    df.columns = [col.strip().replace(" ", "_").replace(":", "_").lower() for col in df.columns]

    # Create DB connection
    conn = create_connection(DB_PATH)
    cursor = conn.cursor()

    # Save to base table
    df.to_sql("icd11", conn, if_exists="replace", index=False)
    print("Data imported into 'icd11' table.")

    # Drop FTS5 table if it already exists (for re-runs)
    cursor.execute("DROP TABLE IF EXISTS icd11_fts")

    # Create the FTS5 virtual table (indexing only code and title)
    cursor.execute("""
        CREATE VIRTUAL TABLE icd11_fts USING fts5(
            code, 
            title, 
            content='icd11', 
            content_rowid='rowid'
        )
    """)

    # Populate FTS5 index
    cursor.execute("""
        INSERT INTO icd11_fts(code, title)
        SELECT code, title FROM icd11
    """)
    conn.commit()
    print("FTS5 index created and populated.")

    # Close connection
    conn.close()
    print(f"Database created at {DB_PATH}")

else:
    print(f"Database already exists at {DB_PATH}. Skipping creation.")

    