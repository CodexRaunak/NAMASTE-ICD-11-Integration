import sqlite3
import os

DB_PATH = 'db/ICD11.db'

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print("Connection error:", e)
        return None

def search_icd11(query_text):
    """
    Search the ICD11 FTS5 index using a full-text query.

    Parameters:
    - query_text: Text to search in the FTS5 index.

    Returns:
    - List of matching (code, title) tuples.
    """
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Please run 'createdatabase.py' first.")
        return []

    conn = create_connection(DB_PATH)
    if conn is None:
        return []

    cursor = conn.cursor()

    try:
        sql_query = "SELECT code, title FROM icd11_fts WHERE icd11_fts MATCH ?;"
        cursor.execute(sql_query, (query_text,))
        results = cursor.fetchall()
        print(f"\nSearch results for '{query_text}':")
        for row in results:
            print(row)
        return results
    except sqlite3.Error as e:
        print("An error occurred during the search:", e)
        return []
    finally:
        conn.close()

user_query = "insomnia*"
search_icd11(user_query)
