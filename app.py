from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "app.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"]) 
def users():
    # Secure implementation using parameterized queries to prevent SQL injection
    user_id = request.args.get("id")
    name = request.args.get("name")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if user_id is not None:
            # Before: f"SELECT * FROM users WHERE id = {user_id}"  (vulnerable)
            # After: parameterized query
            cur.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({"error": "User not found"}), 404
            return jsonify(dict(row))
        elif name is not None:
            # Before: "... WHERE name LIKE '%" + name + "%'" (vulnerable)
            cur.execute("SELECT id, name, email FROM users WHERE name LIKE ?", (f"%{name}%",))
            rows = cur.fetchall()
            return jsonify([dict(r) for r in rows])
        else:
            # List all users safely
            cur.execute("SELECT id, name, email FROM users")
            rows = cur.fetchall()
            return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

