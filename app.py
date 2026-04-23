from flask import Flask, render_template, request, jsonify
from predict import HockeyPredictor
import os

app = Flask(__name__)
predictor = HockeyPredictor()

@app.route('/')
def index():
    # Get unique teams for the dropdowns
    teams = sorted(predictor.encoder.classes_)
    return render_template('index.html', teams=teams)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    team_a = data.get('team_a')
    team_b = data.get('team_b')
    
    if not team_a or not team_b:
        return jsonify({"error": "Chybí název týmu"}), 400
        
    result = predictor.predict_winner(team_a, team_b)
    
    if isinstance(result, str):
        return jsonify({"error": result}), 400
        
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
