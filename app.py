from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Helper to get DB connection
def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/users', methods=['GET'])
def list_users():
    """
    Secure implementation of /users endpoint.
    Previously vulnerable to SQL injection due to string concatenation of user input.
    Now uses parameterized queries to prevent injection.
    """
    # Fetch optional filters safely
    name = request.args.get('name')
    email = request.args.get('email')

    conn = get_db_connection()
    cur = conn.cursor()

    # Build query dynamically but with placeholders for ALL user-controlled values
    query = "SELECT id, name, email FROM users"
    clauses = []
    params = []

    if name is not None and name != "":
        clauses.append("name LIKE ?")
        params.append(f"%{name}%")

    if email is not None and email != "":
        clauses.append("email LIKE ?")
        params.append(f"%{email}%")

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    # Optional ordering with strict allow-list to avoid injection via column names
    order_by = request.args.get('order_by', 'id')
    allowed_order_columns = {'id', 'name', 'email'}
    if order_by not in allowed_order_columns:
        order_by = 'id'

    order_dir = request.args.get('order_dir', 'asc').lower()
    order_dir = 'ASC' if order_dir == 'asc' else 'DESC'

    query += f" ORDER BY {order_by} {order_dir}"

    # Execute parameterized query
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

