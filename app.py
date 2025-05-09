import joblib
from flask import Flask, jsonify, request
import sqlite3

# Load the model
model = joblib.load('stroke_model.pkl')

# Initialize the Flask app
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "<h1>Welcome to Stroke Predictor App 🚀</h1><p>App is running successfully on Render!</p>"

# Users route (SQLite)
@app.route("/users")
def get_users():
    conn = sqlite3.connect("SQLite&Python.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]
    return jsonify(users)

# Predict route (using the trained model)
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()  # Expecting JSON input
        input_data = [list(data.values())]  # Convert to list format if necessary
        prediction = model.predict(input_data)  # Get prediction from the model
        return jsonify({'prediction': int(prediction[0])})  # Send back the prediction as JSON
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
