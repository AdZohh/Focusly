# src/reports/reports.py
import pandas as pd
import os
from ..data import database

def export_sessions_csv(path="focusly_sessions_export.csv"):
    # ejemplo simple que lee la DB y genera CSV
    conn = database.get_conn()
    df = pd.read_sql_query("SELECT * FROM sessions", conn)
    conn.close()
    df.to_csv(path, index=False)
    return path
