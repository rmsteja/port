from flask import Flask, request, jsonify
import sqlite3
from typing import List, Dict, Any

app = Flask(__name__)

DB_PATH = 'app.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dicts
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/users', methods=['GET'])
def users():
    """
    Securely fetch users from the database.
    Prevent SQL injection by using parameterized queries and whitelisting sortable columns.
    Query params:
      - name: optional, filters by exact user name
      - sort: optional, one of ['id', 'name', 'email']
    """
    name = request.args.get('name')
    sort = request.args.get('sort', 'id')

    # Whitelist allowed sort columns to avoid injection via ORDER BY
    allowed_sort_columns = {'id', 'name', 'email'}
    if sort not in allowed_sort_columns:
        sort = 'id'

    conn = get_db()
    try:
        cur = conn.cursor()
        if name:
            # Use parameterized query to avoid SQL injection
            cur.execute(
                f"SELECT id, name, email FROM users WHERE name = ? ORDER BY {sort} ASC",
                (name,)
            )
        else:
            # No concatenation; ORDER BY column name is whitelisted above
            cur.execute(f"SELECT id, name, email FROM users ORDER BY {sort} ASC")

        rows = cur.fetchall()
        users: List[Dict[str, Any]] = [dict(row) for row in rows]
        return jsonify({"users": users}), 200
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

