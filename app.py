from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Load the trained model
model = joblib.load('stroke_model.pkl')

@app.route('/', methods=['GET', 'POST'])
def home_or_predict():
    if request.method == 'GET':
        return "<h1>Welcome to Stroke Predictor App 🚀</h1><p>App is running successfully on Render!</p>"

    if request.method == 'POST':
        data = request.get_json()
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
        prediction = model.predict(input_data)
        return jsonify({'prediction': int(prediction[0])})

if __name__ == '__main__':
    app.run(debug=True)
