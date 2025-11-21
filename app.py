from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "./app.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/users', methods=['GET'])
def get_users():
    """
    Securely fetch users filtered by an optional 'username' query parameter.
    Prevent SQL injection by using parameterized queries.
    """
    username = request.args.get('username')

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if username:
            # Use parameterized query instead of string concatenation
            cur.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
        else:
            cur.execute("SELECT id, username, email FROM users")
        rows = cur.fetchall()
    finally:
        conn.close()

    users = [dict(row) for row in rows]
    return jsonify(users), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=False)

