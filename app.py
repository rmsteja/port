from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Simple SQLite connection for demo purposes. In production, manage connections per-request.
DB_PATH = os.environ.get("DB_PATH", "users.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row

@app.route('/users', methods=['GET'])
def get_users():
    """
    Securely fetch users. Previously, user input was concatenated into SQL, allowing injection.
    This version uses parameterized queries to prevent SQL injection.
    Supported filters:
      - name: exact match on user name
    """
    name = request.args.get('name')

    try:
        cur = conn.cursor()
        if name:
            # Use parameterized query instead of string concatenation to prevent SQL injection
            cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
        else:
            cur.execute("SELECT id, name, email FROM users")
        rows = cur.fetchall()
        users = [{"id": row["id"], "name": row["name"], "email": row["email"]} for row in rows]
        return jsonify(users), 200
    except Exception as e:
        # Avoid leaking internal errors; return a generic message
        return jsonify({"error": "Failed to fetch users"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

