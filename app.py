from flask import Flask, request, jsonify
import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "app.db")

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])
def get_users():
    """
    Secure implementation of the /users endpoint.
    Fixes SQL injection by using parameterized queries instead of string concatenation.
    Supports optional filters by id or name.
    """
    user_id = request.args.get("id")
    name = request.args.get("name")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if user_id is not None:
            # Parameterized query protects against SQL injection
            cur.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        elif name is not None:
            # Parameterized query protects against SQL injection
            cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
        else:
            cur.execute("SELECT id, name, email FROM users")

        rows = cur.fetchall()
        users = [dict(row) for row in rows]
        return jsonify(users), 200
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)

