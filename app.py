from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing

app = Flask(__name__)

DB_PATH = "./app.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])
def get_users():
    """
    Securely fetch users filtered by the optional 'name' query parameter.
    Fix: Use parameterized queries instead of string concatenation to prevent SQL Injection.
    """
    name = request.args.get("name")

    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        if name is None or name == "":
            # No filter, return limited safe fields for all users
            cur.execute("SELECT id, name, email FROM users")
        else:
            # Parameterized query prevents SQL injection
            cur.execute("SELECT id, name, email FROM users WHERE name = ?", (name,))
        rows = cur.fetchall()
        users = [dict(row) for row in rows]
    return jsonify(users), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

