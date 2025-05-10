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

        # Check for all required fields
        required_fields = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi', 'gender', 'work_type', 'smoking_status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Calculate the extra variable (interaction term)
        age_glucose_interaction = data['age'] * data['avg_glucose_level']

        # Prepare the input data for prediction (including the interaction term)
        input_data = [[
            data['gender'],
            data['age'],
            data['hypertension'],
            data['heart_disease'],
            data['work_type'],
            data['avg_glucose_level'],
            data['bmi'],
            data['smoking_status'],
            data['age'] * data['avg_glucose_level'] 
        ]]

        print("🔍 Input to model:", input_data)

        # Get the prediction probability (this gives the model's confidence level)
        proba = model.predict_proba(input_data)
        risk_score = proba[0][1]  # Probability of stroke risk (class 1)
        prediction = 1 if risk_score > 0.5 else 0  # Use the threshold to determine high or low risk

        print("📈 Risk Score:", risk_score)
        print("🔮 Prediction:", prediction)

        # Return the response with the risk score, prediction, and risk level
        return jsonify({
            'risk_score': round(risk_score, 4),
            'prediction': prediction,
            'risk_level': 'High' if prediction == 1 else 'Low'
        })

    except Exception as e:
        print("❌ Error during prediction:")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred during prediction.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
