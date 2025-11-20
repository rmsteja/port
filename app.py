from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import sqlite3
import os

app = FastAPI(title="Simple API with Vulnerability")

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES ('admin', 'admin@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES ('user1', 'user1@example.com')")
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to the vulnerable API"}

@app.get("/users")
def get_users(username: str = Query(None)):
    """
    Get user information by username.
    VULNERABILITY: SQL Injection - username parameter is directly concatenated into SQL query
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    if username:
        # VULNERABLE: Direct string concatenation - SQL Injection vulnerability
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(query)
    else:
        cursor.execute("SELECT * FROM users")
    
    results = cursor.fetchall()
    conn.close()
    
    users = [{"id": r[0], "username": r[1], "email": r[2]} for r in results]
    return {"users": users}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

