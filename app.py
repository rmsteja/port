from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database helper

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Secure /users endpoint using parameterized queries to prevent SQL Injection
@app.route('/users')
def get_users():
    username = request.args.get('username')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if username:
            # FIX: use parameterized query instead of string concatenation
            cur.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
        else:
            cur.execute("SELECT id, username, email FROM users")

        rows = cur.fetchall()
        users = [dict(row) for row in rows]
        return jsonify(users)
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

