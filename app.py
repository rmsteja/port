from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Assume there is a helper to get a DB connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/users', methods=['GET'])
def users():
    # Get optional filter by name from query params
    name = request.args.get('name')

    conn = get_db_connection()
    cur = conn.cursor()

    # FIX: use parameterized query to prevent SQL injection
    # Previously (vulnerable):
    # query = f"SELECT id, name, email FROM users WHERE name = '{name}'" if name else "SELECT id, name, email FROM users"
    if name:
        cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
    else:
        cur.execute("SELECT id, name, email FROM users")

    rows = cur.fetchall()
    conn.close()

    users_list = [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]
    return jsonify(users_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

