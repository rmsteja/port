from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "users.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])  # Fixed: use parameterized query to prevent SQL injection
def users():
    name = request.args.get("name")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if name is None or name == "":
            # Return all users safely
            cur.execute("SELECT id, name, email FROM users")
            rows = cur.fetchall()
        else:
            # Parameterized query prevents SQL injection
            cur.execute(
                "SELECT id, name, email FROM users WHERE name = ?",
                (name,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    users_list = [dict(row) for row in rows]
    return jsonify(users_list)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

