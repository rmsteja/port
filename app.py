from flask import Flask, request, jsonify
import os
import sqlite3
from contextlib import closing

# Minimal Flask app with safe, parameterized SQL access to prevent SQL Injection
# This file replaces unsafe string-concatenated SQL in the /users endpoint with parameterized queries.

DB_PATH = os.getenv("DB_PATH", "app.db")

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])
def users():
    """
    Safe /users endpoint.
    - Supports optional query parameters: id (int) and username (str).
    - Uses parameterized queries to avoid SQL injection.
    - If no filters are provided, returns all users (paginated via limit/offset to be safe by default).
    """
    user_id = request.args.get("id")
    username = request.args.get("username")

    # Basic pagination defaults to avoid returning unbounded data
    try:
        limit = int(request.args.get("limit", 100))
        limit = max(1, min(limit, 1000))
    except ValueError:
        limit = 100
    try:
        offset = int(request.args.get("offset", 0))
        offset = max(0, offset)
    except ValueError:
        offset = 0

    where_clauses = []
    params = []

    if user_id is not None:
        # Only accept numeric id; sqlite3 param binding handles typing safely
        try:
            user_id_int = int(user_id)
            where_clauses.append("id = ?")
            params.append(user_id_int)
        except ValueError:
            return jsonify({"error": "id must be an integer"}), 400

    if username is not None:
        # Use exact match; for partial matches switch to LIKE with escaped params
        where_clauses.append("username = ?")
        params.append(username)

    where_sql = ""
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)

    sql = f"SELECT id, username, email FROM users{where_sql} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with closing(get_db_connection()) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]

    return jsonify(rows), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))

