from flask import Flask, render_template, request, redirect, url_for, jsonify
import joblib
import sqlite3
import os

app = Flask(__name__)

# Load the stroke prediction model
model = joblib.load("stroke_model.pkl")

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect("predictions.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create predictions table if it doesn't exist
with get_db_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gender TEXT,
            age REAL,
            hypertension INTEGER,
            heart_disease INTEGER,
            ever_married TEXT,
            work_type TEXT,
            Residence_type TEXT,
            avg_glucose_level REAL,
            bmi REAL,
            smoking_status TEXT,
            prediction INTEGER
        )
    """)
    conn.commit()

# Home route (newly modified)
@app.route("/")
def home():
    return """
        <h1>Welcome to the Stroke Predictor App</h1>
        <p><a href="/predict">Make a Prediction</a></p>
        <p><a href="/instructions">Instructions</a></p>
    """

# Prediction form route
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        data = {
            "gender": request.form["gender"],
            "age": float(request.form["age"]),
            "hypertension": int(request.form["hypertension"]),
            "heart_disease": int(request.form["heart_disease"]),
            "ever_married": request.form["ever_married"],
            "work_type": request.form["work_type"],
            "Residence_type": request.form["Residence_type"],
            "avg_glucose_level": float(request.form["avg_glucose_level"]),
            "bmi": float(request.form["bmi"]),
            "smoking_status": request.form["smoking_status"]
        }

        input_features = [
            data["gender"], data["age"], data["hypertension"], data["heart_disease"],
            data["ever_married"], data["work_type"], data["Residence_type"],
            data["avg_glucose_level"], data["bmi"], data["smoking_status"]
        ]

        # Make prediction (encode if needed)
        prediction = model.predict([input_features])[0]

        # Save to DB
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO predictions (
                    gender, age, hypertension, heart_disease, ever_married,
                    work_type, Residence_type, avg_glucose_level, bmi,
                    smoking_status, prediction
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(input_features + [prediction]))
            conn.commit()

        return render_template("result.html", prediction=prediction)

    return render_template("predict.html")

# Instructions route
@app.route("/instructions")
def instructions():
    return render_template("instructions.html")

if __name__ == "__main__":
    app.run(debug=True)


