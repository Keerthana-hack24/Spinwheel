import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")

app = Flask(__name__)
CORS(app, origins=[CORS_ORIGIN])

@app.route("/check-flask")
def flask_check():
    return {"ok": True}

@app.route("/check-connection")
def check_connection():
    try:
        conn = psycopg.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT now();")
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify(ok=True, time=str(result))
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)