from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing

app = Flask(__name__)

DB_PATH = 'users.db'


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/users', methods=['GET'])
def users():
    # Securely handle optional query parameters
    name = request.args.get('name')
    limit = request.args.get('limit', default=None)

    # Validate limit to avoid abuse; cast to int if provided
    if limit is not None:
        try:
            limit = int(limit)
            # enforce sane bounds
            if limit < 1:
                limit = 1
            if limit > 500:
                limit = 500
        except ValueError:
            # Fallback to a safe default if invalid
            limit = 100

    with closing(get_db_connection()) as conn:
        with closing(conn.cursor()) as cur:
            if name:
                # Use parameterized query to prevent SQL injection
                if limit:
                    cur.execute(
                        'SELECT id, name, email FROM users WHERE name = ? LIMIT ?',
                        (name, limit)
                    )
                else:
                    cur.execute(
                        'SELECT id, name, email FROM users WHERE name = ?',
                        (name,)
                    )
            else:
                if limit:
                    cur.execute(
                        'SELECT id, name, email FROM users LIMIT ?',
                        (limit,)
                    )
                else:
                    cur.execute('SELECT id, name, email FROM users')

            rows = cur.fetchall()
            users_list = [dict(row) for row in rows]

    return jsonify(users_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

