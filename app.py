from flask import Flask, render_template, request, jsonify
from backend.expert_wrapper import ExpertWrapper
import os

app = Flask(__name__)

kb_path = os.path.join(os.path.dirname(__file__), 'backend', 'medical_knowledge.json')
expert = ExpertWrapper(kb_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    search = request.args.get('search', '')
    if search:
        symptoms = expert.search_symptoms(search)
    else:
        symptoms = expert.get_all_symptoms()
    return jsonify({'symptoms': symptoms})

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    diseases = expert.get_all_diseases()
    return jsonify({'diseases': diseases})

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    symptoms = request.json.get('symptoms', [])
    results = expert.diagnose(symptoms)
    diagnoses = []
    for disease, confidence, info in results:
        diagnoses.append({
            'name': disease,
            'confidence': min(int(confidence * 10), 100),
            'description': info.get('description', 'No description available.')
        })
    return jsonify({'diagnoses': diagnoses})

@app.route('/api/disease/<name>', methods=['GET'])
def disease_info(name):
    info = expert.get_disease_info(name)
    if not info:
        return jsonify({'error': 'Disease not found'}), 404
    return jsonify({
        'name': name,
        'description': info.get('description', 'No description available.'),
        'precautions': info.get('precautions', []),
        'symptom_patterns': [
            [expert.expert_system.format_symptom_for_display(s) for s in pattern] 
            for pattern in info.get('symptom_patterns', [])
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)
