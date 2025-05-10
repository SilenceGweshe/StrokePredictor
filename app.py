from flask import Flask, request, jsonify
import joblib
import traceback

app = Flask(__name__)

# Load the trained model
try:
    model = joblib.load('stroke_model.pkl')
    print("✅ Model loaded successfully.")
except Exception as e:
    print("❌ Failed to load model:")
    traceback.print_exc()
    model = None

@app.route('/')
def home():
    return "<h1>Welcome to Stroke Predictor App 🚀</h1><p>App is running successfully on Render!</p>"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("📦 Incoming data:", data)

        required_fields = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi', 'gender', 'work_type', 'smoking_status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        input_data = [[
            data['age'],
            data['hypertension'],
            data['heart_disease'],
            data['avg_glucose_level'],
            data['bmi'],
            data['gender'],
            data['work_type'],
            data['smoking_status']
        ]]

        print("🔍 Input to model:", input_data)

        prediction = model.predict(input_data)
        print("📈 Prediction result:", prediction)

        return jsonify({'prediction': int(prediction[0])})

    except Exception as e:
        print("❌ Error during prediction:")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred during prediction.'}), 500
