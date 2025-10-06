# app.py — initial version: GET names from database upon loading of the website, mark winner:
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg

ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL not set. Expected in {ENV_PATH}")

app = Flask(__name__)
CORS(app)  

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True)

@app.get("/check-flask")
def check_flask():
    return {"ok": True}

@app.get("/check-connection")  
def check_connection():
    try:
        with get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return jsonify(ok=True, db=True)
    except Exception as e:
        return jsonify(ok=False, db=False, error=str(e)), 500
    
# 1) Read names for the wheel from the Sampletb participants table
@app.get("/names")
def get_names():
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT name, COALESCE(status,'') FROM participants ORDER BY id;")
        rows = cur.fetchall()
        names = [r[0] for r in rows]  # just the names for the wheel
        return jsonify(ok=True, names=names, count=len(names))
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500
    finally:
        try:
            if cur: cur.close()
        except Exception: pass
        try:
            if conn: conn.close()
        except Exception: pass


# 2) Mark a winner - updates status in the participants table
@app.post("/winner")
def mark_winner():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(ok=False, error="Missing name"), 400
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE participants SET status = 'winner' WHERE name = %s;", (name,))
        return jsonify(ok=True, updated=cur.rowcount)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500
    finally:
        try:
            if cur: cur.close()
        except Exception: pass
        try:
            if conn: conn.close()
        except Exception: pass

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
