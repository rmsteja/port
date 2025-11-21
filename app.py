from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Helper to get a DB connection (example using SQLite)
# In a real app, replace with your actual DB connector/pool
DB_PATH = 'app.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/users', methods=['GET'])
def get_users():
    """
    Secure implementation of /users endpoint using parameterized queries to prevent SQL injection.
    Supports optional filtering by username via query param `username`.
    """
    username = request.args.get('username')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if username:
            # Use a parameterized query rather than string concatenation
            cur.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
        else:
            # No filter provided; return all users safely
            cur.execute("SELECT id, username, email FROM users")

        rows = cur.fetchall()
        users = [dict(row) for row in rows]
        return jsonify(users), 200
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

