from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing

app = Flask(__name__)

DB_PATH = "app.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"]) 
def get_users():
    """
    Securely returns users, optionally filtered by the "name" query parameter.
    Fix: Replace vulnerable string-concatenated SQL with parameterized queries to prevent SQL injection.
    """
    name = request.args.get("name")

    with closing(get_db_connection()) as conn, closing(conn.cursor()) as cur:
        if name is not None and name != "":
            # Use a parameterized query instead of string concatenation to prevent SQL injection
            cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
        else:
            cur.execute("SELECT id, name, email FROM users")

        rows = cur.fetchall()
        users = [dict(row) for row in rows]
        return jsonify(users), 200


if __name__ == "__main__":
    # Simple dev server run
    app.run(host="0.0.0.0", port=5000, debug=False)

