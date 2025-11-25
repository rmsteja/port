from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "app.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionaries for JSON response
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])  # Vulnerable endpoint fixed: use parameterized queries
def users():
    # Safely get the optional filter parameter
    name = request.args.get("name")

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if name:
            # FIX: Use parameterized query to prevent SQL injection
            cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
        else:
            cur.execute("SELECT id, name, email FROM users")
        rows = cur.fetchall()
        # Convert rows to list of dicts
        result = [dict(row) for row in rows]
        return jsonify(result), 200
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)

