from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "users.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])  # Secure against SQL injection
def users():
    """
    Secure implementation of the /users endpoint using parameterized queries.
    Accepts optional query parameter `name` to filter users by exact match.
    """
    name = request.args.get("name")

    conn = get_db_connection()
    try:
        if name is None or name.strip() == "":
            # No user input included in SQL; returns all users safely
            cursor = conn.execute(
                "SELECT id, name, email FROM users"
            )
            rows = cursor.fetchall()
        else:
            # Use parameterized query to prevent SQL injection
            cursor = conn.execute(
                "SELECT id, name, email FROM users WHERE name = ?",
                (name.strip(),),
            )
            rows = cursor.fetchall()

        users_list = [
            {"id": row["id"], "name": row["name"], "email": row["email"]}
            for row in rows
        ]
        return jsonify(users_list), 200
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

