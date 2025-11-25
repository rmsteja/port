from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Assuming there is a SQLite database file named 'app.db' with a 'users' table.
# If your application uses a different DB driver, make sure to use its parameterized
# query placeholders (e.g., %s for psycopg2/MySQLdb). For sqlite3, use "?".

def get_db_connection():
    conn = sqlite3.connect('app.db')
    # Return rows as dict-like for easier JSON conversion
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/users', methods=['GET'])
def get_users():
    # Previously vulnerable: user input was concatenated directly into the SQL string.
    # Safe fix: use parameterized query with placeholders to prevent SQL injection.
    name = request.args.get('name')

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if name:
            # Use parameterized query instead of string concatenation
            cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
        else:
            cur.execute("SELECT id, name, email FROM users")
        rows = cur.fetchall()
        users = [dict(row) for row in rows]
        return jsonify(users), 200
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

