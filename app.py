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

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, your app is deployed successfully!"

    from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Welcome to Stroke Predictor App 🚀</h1><p>App is running successfully on Render!</p>"

if __name__ == "__main__":
    app.run(debug=True)


