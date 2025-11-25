from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing

app = Flask(__name__)

DB_PATH = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# Secure implementation of /users endpoint preventing SQL injection
@app.route("/users", methods=["GET"]) 
def get_users():
    # Optional filtering by name via query parameter, safely parameterized
    name = request.args.get("name")

    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        if name is None or name == "":
            # No filter - return all users
            cur.execute("SELECT id, name, email FROM users")
        else:
            # Parameterized query prevents SQL injection
            # Using placeholders and a parameter tuple is the recommended approach
            cur.execute(
                "SELECT id, name, email FROM users WHERE name = ?",
                (name,)
            )
        rows = cur.fetchall()

    users = [dict(row) for row in rows]
    return jsonify(users)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

