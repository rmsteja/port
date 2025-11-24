from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "./app.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])
def get_users():
    """
    Secure implementation of users lookup avoiding SQL Injection by using
    parameterized queries instead of string concatenation.
    Query params:
      - name (optional): filter by exact user name
    """
    name = request.args.get("name")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if name is not None and name != "":
            # Use parameterized query to prevent SQL injection
            cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
        else:
            cur.execute("SELECT id, name, email FROM users")
        rows = [dict(r) for r in cur.fetchall()]
        return jsonify(rows), 200
    except Exception as e:
        # Do not leak DB errors to clients
        return jsonify({"error": "Internal server error"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.route("/")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)

