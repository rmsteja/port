from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "./app.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# FIX: Use parameterized queries and avoid string concatenation with user input
@app.route("/users")
def users():
    # Support optional search by username via query param `q`
    q = request.args.get("q", "")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if q:
            # Parameterized LIKE search to prevent SQL injection
            like_param = f"%{q}%"
            cur.execute("SELECT id, username, email FROM users WHERE username LIKE ?", (like_param,))
        else:
            cur.execute("SELECT id, username, email FROM users")

        rows = cur.fetchall()
        users_list = [dict(row) for row in rows]
        return jsonify(users_list)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

