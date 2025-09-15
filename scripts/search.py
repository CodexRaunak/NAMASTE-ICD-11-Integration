import sqlite3
import os

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print("Connection error:", e)
        return None

def search_fts(db_path, fts_table_name, query_text, columns, debug=False):
    """
    Search a SQLite FTS5 virtual table with a full-text query.

    Parameters:
    - db_path: Path to SQLite DB file.
    - fts_table_name: Name of the FTS5 virtual table.
    - query_text: Full-text search query string.
    - columns: List of columns to fetch from the FTS table.
    - debug: If True, prints results.

    Returns:
    - List of tuples with matching rows.
    """
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Please create it first.")
        return []

    conn = create_connection(db_path)
    if conn is None:
        return []

    cursor = conn.cursor()
    cols_sql = ", ".join(columns)

    try:
        sql_query = f"SELECT {cols_sql} FROM {fts_table_name} WHERE {fts_table_name} MATCH ?;"
        cursor.execute(sql_query, (query_text,))
        results = cursor.fetchall()
        if debug:
            print(f"\nSearch results for '{query_text}':")
            for row in results:
                print(row)
        return results
    except sqlite3.Error as e:
        print("An error occurred during the search:", e)
        return []
    finally:
        conn.close()


if __name__ == "__main__":
    DB_PATH = 'db/ayush_icd11_combined.db'  
    FTS_TABLE = 'icd11_fts'              
    QUERY = "insomnia*"

    results = search_fts(DB_PATH, FTS_TABLE, QUERY, columns=["code", "title"], debug=True)
