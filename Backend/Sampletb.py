import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg

ENV_PATH = Path(__file__).with_name(".env")  

load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL not set. Expected in {ENV_PATH}")

NAMES = ["Alice", "Ann", "Aria", "Amber"]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS participants (
    id      BIGSERIAL PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE,
    status  TEXT);
"""

INSERT_SQL = "INSERT INTO participants(name) VALUES (%s) ON CONFLICT (name) DO NOTHING;"
SELECT_SQL = "SELECT id, name, COALESCE(status, '') AS status FROM participants ORDER BY id;"

conn = None
cur = None
try:
    conn = psycopg.connect(DATABASE_URL) 
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)
    for n in NAMES:
        cur.execute(INSERT_SQL, (n,))
    conn.commit()
    cur.execute(SELECT_SQL)
    rows = cur.fetchall()

    print("Participants in DB:")
    for r in rows:
        print(f"  ID={r[0]:<3} NAME={r[1]:<10} STATUS={r[2]}")
    print("\n✅ Table ready")

except Exception as e:
    print("Error:", e)
    if conn is not None:
        try:
            conn.rollback()
        except Exception:
            pass
finally:
    if cur is not None:
        try:
            cur.close()
        except Exception:
            pass
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
