from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Initialize a simple SQLite connection (for demo purposes)
DB_PATH = os.environ.get("DB_PATH", "users.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row

@app.route('/users', methods=['GET'])
def get_users():
    """
    Secure implementation of /users that prevents SQL Injection by using
    parameterized queries.
    Accepts optional query parameter `name` to filter users by exact name.
    """
    name = request.args.get('name')

    try:
        cur = conn.cursor()
        if name is None or name == "":
            # No filter provided; return all users safely
            cur.execute("SELECT id, name, email FROM users")
        else:
            # Use parameterized query to prevent SQL injection
            cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))

        rows = cur.fetchall()
        users = [dict(row) for row in rows]
        return jsonify(users), 200
    except Exception as e:
        # In production, avoid leaking details; log instead
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

