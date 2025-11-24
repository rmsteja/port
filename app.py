from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "./app.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])  # Fixed: prevent SQL injection by using parameterized queries
def get_users():
    name = request.args.get("name")

    # Basic input handling (optional but defensive)
    if name is not None and (not isinstance(name, str) or len(name) > 255):
        return jsonify({"error": "invalid 'name' parameter"}), 400

    conn = get_db()
    try:
        cur = conn.cursor()
        if name is None or name.strip() == "":
            # No filter provided: return all users safely
            cur.execute("SELECT id, name, email FROM users")
            rows = cur.fetchall()
        else:
            # SAFE: Use a parameterized query instead of string concatenation
            cur.execute(
                "SELECT id, name, email FROM users WHERE name = ?",
                (name.strip(),),
            )
            rows = cur.fetchall()

        users = [dict(row) for row in rows]
        return jsonify(users), 200
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

