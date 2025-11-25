from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/users', methods=['GET'])
def get_users():
    # Securely handle user-supplied input and use parameterized queries to prevent SQL injection
    name = request.args.get('name')

    conn = get_db_connection()
    cur = conn.cursor()

    users = []
    try:
        if name is None or name.strip() == "":
            # If no name filter provided, return all users in a safe manner
            cur.execute("SELECT id, name, email FROM users")
        else:
            # Use parameterized query instead of string concatenation
            # Support partial match safely using LIKE with bound parameter
            like_param = f"%{name.strip()}%"
            cur.execute(
                "SELECT id, name, email FROM users WHERE name LIKE ?",
                (like_param,)
            )
        rows = cur.fetchall()
        for r in rows:
            users.append({
                'id': r['id'],
                'name': r['name'],
                'email': r['email']
            })
    finally:
        cur.close()
        conn.close()

    return jsonify(users), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

