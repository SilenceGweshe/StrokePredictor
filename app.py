from flask import Flask, request, jsonify, render_template
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
    # Render the form.html template when the root URL is visited
    return render_template('form.html')  # form.html should be placed inside the 'templates' folder

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.form.to_dict()  # Get form data from the HTML form submission
        print("📦 Incoming data:", data)

        # Check for all required fields
        required_fields = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi', 'gender', 'work_type', 'smoking_status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Prepare the input data for prediction (including the interaction term)
        input_data = [[
            float(data['gender']),
            float(data['age']),
            float(data['hypertension']),
            float(data['heart_disease']),
            float(data['work_type']),
            float(data['avg_glucose_level']),
            float(data['bmi']),
            float(data['smoking_status']),
            float(data['age']) * float(data['avg_glucose_level'])  # Add the interaction term
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
