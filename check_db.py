import sqlite3
import pandas as pd

try:
    conn = sqlite3.connect('app.db')
    df = pd.read_sql_query("SELECT * FROM repositories", conn)
    if df.empty:
        print("No repositories found in the database.")
    else:
        print(df.to_string())
    conn.close()
except Exception as e:
    print(f"Error: {e}")
