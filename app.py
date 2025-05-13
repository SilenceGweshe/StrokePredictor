from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import joblib
import sqlite3
import traceback
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Load environment variables
load_dotenv()

# Use the secret key from the .env file
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Load the trained model
try:
    model = joblib.load('stroke_model.pkl')
    print("✅ Model loaded successfully.")
except Exception as e:
    print("❌ Failed to load model:")
    traceback.print_exc()
    model = None

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('stroke_predictions.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age REAL,
        hypertension INTEGER,
        heart_disease INTEGER,
        avg_glucose_level REAL,
        bmi REAL,
        gender TEXT,
        work_type TEXT,
        smoking_status TEXT,
        risk_score REAL,
        prediction INTEGER,
        risk_level TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# 🔐 Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        conn = sqlite3.connect('stroke_predictions.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return render_template('register.html', error="Username already exists")

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Store the new user in the database
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# 🔐 Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists in the database
        conn = sqlite3.connect('stroke_predictions.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # user[2] is the hashed password
            session['username'] = username
            return redirect(url_for('home'))  # Redirect to home page after login
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

# 🔓 Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# 🏠 Home page (after login)
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session['username'])

# 📄 Instructions Page
@app.route('/')
def instructions():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('instructions.html')

# 📋 Form page
@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('form.html')

# 🤖 Stroke Prediction API
@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        required_fields = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi', 'gender', 'work_type', 'smoking_status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        input_data = [[
            float(data['gender']),
            float(data['age']),
            float(data['hypertension']),
            float(data['heart_disease']),
            float(data['work_type']),
            float(data['avg_glucose_level']),
            float(data['bmi']),
            float(data['smoking_status']),
            float(data['age']) * float(data['avg_glucose_level'])
        ]]

        proba = model.predict_proba(input_data)
        risk_score = proba[0][1]
        prediction = 1 if risk_score > 0.7 else 0
        risk_level = 'High' if prediction == 1 else 'Low'

        conn = sqlite3.connect('stroke_predictions.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO predictions (
            age, hypertension, heart_disease, avg_glucose_level,
            bmi, gender, work_type, smoking_status, risk_score,
            prediction, risk_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            data['age'], data['hypertension'], data['heart_disease'], data['avg_glucose_level'],
            data['bmi'], data['gender'], data['work_type'], data['smoking_status'],
            risk_score, prediction, risk_level
        ))
        conn.commit()
        conn.close()

        return jsonify({
            'risk_score': round(risk_score, 4),
            'prediction': prediction,
            'risk_level': risk_level
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred during prediction.'}), 500

# 🚀 Run app
if __name__ == '__main__':
    app.run(debug=True)
