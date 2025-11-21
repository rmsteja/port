from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/users')
def users():
    name = request.args.get('name', '')
    conn = get_db()
    cur = conn.cursor()
    # Use a parameterized query to prevent SQL injection
    query = "SELECT id, name, email FROM users WHERE name LIKE ?"
    param = f"%{name}%"
    rows = cur.execute(query, (param,)).fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
