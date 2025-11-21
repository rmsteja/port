from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing

app = Flask(__name__)

DB_PATH = 'db.sqlite'

# Secure implementation of the /users endpoint using parameterized queries
@app.get('/users')
def get_users():
    # Read optional query parameter safely
    name = request.args.get('name')

    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row
            with closing(conn.cursor()) as cur:
                if name is None or name == '':
                    # Return all users when no filter is provided (safe query)
                    cur.execute('SELECT id, name, email FROM users')
                else:
                    # Use parameterized query to prevent SQL injection
                    cur.execute('SELECT id, name, email FROM users WHERE name = ?', (name,))
                rows = cur.fetchall()

        users = [dict(row) for row in rows]
        return jsonify(users), 200
    except sqlite3.Error as e:
        # Return a generic error without leaking DB details
        return jsonify({'error': 'Database error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

