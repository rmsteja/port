from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing

app = Flask(__name__)

DB_PATH = 'app.db'

# Helper to get DB connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/users', methods=['GET'])
def users():
    # Previously vulnerable: direct string concatenation in SQL query using user input
    # Fix: use parameterized queries and validate inputs
    username = request.args.get('username')

    try:
        with closing(get_db_connection()) as conn:
            cur = conn.cursor()
            if username:
                # Parameterized query prevents SQL injection
                cur.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
            else:
                cur.execute("SELECT id, username, email FROM users")
            rows = cur.fetchall()
    except sqlite3.Error as e:
        return jsonify({"error": "database_error", "message": str(e)}), 500

    users_list = [
        {"id": row["id"], "username": row["username"], "email": row["email"]}
        for row in rows
    ]
    return jsonify({"users": users_list}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

