from flask import Flask, jsonify
import sqlite3
import threading

app = Flask(__name__)

@app.route("/users")
def get_users():
    conn = sqlite3.connect("SQLite&Python.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]
    return jsonify(users)

