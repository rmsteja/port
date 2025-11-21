from flask import Flask, request, jsonify
import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("DB_PATH", "./app.db")

app = Flask(__name__)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/users", methods=["GET"])
def users() -> Any:
    """
    Securely return users. Prevent SQL injection by using parameterized queries, never string concatenation.

    Supported query params:
    - id: integer user id to fetch a single user
    - limit: integer max rows (default 100, max 1000)
    - offset: integer offset for pagination (default 0)
    """
    user_id = request.args.get("id")
    limit = request.args.get("limit", default="100")
    offset = request.args.get("offset", default="0")

    # Validate numeric inputs strictly
    def to_int(value: Optional[str], default: int, minimum: int = 0, maximum: Optional[int] = None) -> int:
        try:
            ivalue = int(value) if value is not None else default
        except (TypeError, ValueError):
            ivalue = default
        if ivalue < minimum:
            ivalue = minimum
        if maximum is not None and ivalue > maximum:
            ivalue = maximum
        return ivalue

    limit_i = to_int(limit, 100, minimum=1, maximum=1000)
    offset_i = to_int(offset, 0, minimum=0)

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            if user_id is not None:
                # Ensure id is integer to avoid type confusion
                try:
                    user_id_i = int(user_id)
                except ValueError:
                    return jsonify({"error": "Invalid id"}), 400
                # Parameterized query prevents SQL injection
                cur.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id_i,))
                row = cur.fetchone()
                if not row:
                    return jsonify({"error": "User not found"}), 404
                return jsonify({"id": row["id"], "name": row["name"], "email": row["email"]})
            else:
                # Use LIMIT/OFFSET as parameters when supported by driver; sqlite3 supports binding
                cur.execute(
                    "SELECT id, name, email FROM users ORDER BY id LIMIT ? OFFSET ?",
                    (limit_i, offset_i),
                )
                rows = cur.fetchall()
                users_list: List[Dict[str, Any]] = [
                    {"id": r["id"], "name": r["name"], "email": r["email"]} for r in rows
                ]
                return jsonify(users_list)
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "detail": str(e)}), 500


if __name__ == "__main__":
    # Simple dev server; in production use a proper WSGI server
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")), debug=False)

