from flask import Flask, request, jsonify
import sqlite3
from contextlib import closing

app = Flask(__name__)

DB_PATH = "./app.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def escape_like(term: str) -> str:
    """Escape wildcard characters for SQL LIKE patterns."""
    return term.replace("%", "[%]").replace("_", "[_]")


@app.route("/users", methods=["GET"])
def users():
    # Support filtering by numeric id or by name fragment.
    user_id = request.args.get("id")
    name = request.args.get("name")

    with closing(get_db_connection()) as conn, closing(conn.cursor()) as cur:
        if user_id is not None:
            # Ensure id is an integer and use a parameterized query to prevent SQL injection.
            try:
                uid = int(user_id)
            except (TypeError, ValueError):
                return jsonify({"error": "id must be an integer"}), 400

            cur.execute("SELECT id, name, email FROM users WHERE id = ?", (uid,))
            row = cur.fetchone()
            if not row:
                return jsonify({"error": "user not found"}), 404
            return jsonify(dict(row)), 200

        # Name search using LIKE must be parameterized and escape wildcards provided by user
        if name is not None:
            safe = escape_like(name)
            # Use ESCAPE clause so our escaping works as intended
            pattern = f"%{safe}%"
            cur.execute("SELECT id, name, email FROM users WHERE name LIKE ? ESCAPE '|'", (pattern,))
            rows = cur.fetchall()
            return jsonify([dict(r) for r in rows]), 200

        # Default: return all users in a safe, parameterless query
        cur.execute("SELECT id, name, email FROM users")
        rows = cur.fetchall()
        return jsonify([dict(r) for r in rows]), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

