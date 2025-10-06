import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg

load_dotenv(Path(__file__).with_name(".env"))
url = os.getenv("DATABASE_URL")

conn = None
cur = None
try:
    conn = psycopg.connect(url)   
    cur = conn.cursor()

    cur.execute("SELECT id, name, COALESCE(status,'') AS status FROM participants ORDER BY id;")
    rows = cur.fetchall()

    for i, name, status in rows:
        print(f"{i:>3}  {name:<20}  {status}")

except Exception as e:
    print("Error:", e)
finally:
    if cur is not None:
        try: cur.close()
        except Exception: pass
    if conn is not None:
        try: conn.close()
        except Exception: pass
