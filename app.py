from flask import Flask, render_template, request, redirect, url_for, session, flash
import joblib
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load the stroke prediction model    
model = joblib.load("stroke_model.pkl")

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect("predictions.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database tables
with get_db_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gender TEXT,
            age REAL,
            hypertension INTEGER,
            heart_disease INTEGER,
            work_type TEXT,
            avg_glucose_level REAL,
            bmi REAL,
            smoking_status TEXT,
            age_glucose_interaction REAL,
            prediction INTEGER
        )
    """)
    conn.commit()

# Add new column to existing predictions table if it doesn't exist
with get_db_connection() as conn:
    try:
        conn.execute("ALTER TABLE predictions ADD COLUMN age_glucose_interaction REAL")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists

# Welcome page
@app.route("/")
def welcome():
    return render_template("home.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with get_db_connection() as conn:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash("Registration successful. Please log in.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username already exists.")
    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
            if user:
                session["user"] = username
                return redirect(url_for("instructions"))
            else:
                flash("Invalid credentials.")
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))

# Redirect forgot password to register
@app.route("/forgot_password")
def forgot_password():
    return redirect(url_for("register"))

# Form page
@app.route("/form")
def form():
    if "user" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    return render_template("form.html")

# Prediction route
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    data = {
        "gender": request.form["gender"],
        "age": float(request.form["age"]),
        "hypertension": int(request.form["hypertension"]),
        "heart_disease": int(request.form["heart_disease"]),
        "work_type": request.form["work_type"],
        "avg_glucose_level": float(request.form["avg_glucose_level"]),
        "bmi": float(request.form["bmi"]),
        "smoking_status": request.form["smoking_status"]
    }

    age_glucose_interaction = data["age"] * data["avg_glucose_level"]
    input_features = list(data.values()) + [age_glucose_interaction]

    # Make prediction
    prediction = model.predict([input_features])[0]
    probability = model.predict_proba([input_features])[0][prediction]

    label = "High Stroke Risk" if prediction == 1 else "Low Stroke Risk"
    confidence = round(probability * 100, 2)

    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO predictions (
                gender, age, hypertension, heart_disease,
                work_type, avg_glucose_level, bmi,
                smoking_status, age_glucose_interaction, prediction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(input_features + [prediction]))
        conn.commit()

    return render_template("result.html", prediction=prediction, label=label, confidence=confidence)

# Instructions page
@app.route("/instructions")
def instructions():
    return render_template("instructions.html")

if __name__ == "__main__":
    app.run(debug=True)

