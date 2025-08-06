from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
from ner import MedicalNER
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the NER system
ner_system = MedicalNER()

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text and return extracted medical entities."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'No text provided',
                'message': 'Please provide text to analyze'
            }), 400
        
        text = data['text'].strip()
        
        if not text:
            return jsonify({
                'error': 'Empty text',
                'message': 'Please provide non-empty text to analyze'
            }), 400
        
        # Extract entities
        entities = ner_system.extract_entities(text)
        
        # Convert entities to dictionary format
        entities_data = []
        for entity in entities:
            entities_data.append({
                'text': entity.text,
                'label': entity.label,
                'start': entity.start,
                'end': entity.end,
                'confidence': entity.confidence
            })
        
        # Get annotated text
        annotated_text = ner_system.annotate_text(text)
        
        # Get entity summary
        summary = ner_system.get_entity_summary(text)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'entities': entities_data,
            'annotated_text': annotated_text,
            'summary': summary,
            'total_entities': len(entities_data)
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Processing error',
            'message': str(e)
        }), 500

@app.route('/api/entity_types', methods=['GET'])
def get_entity_types():
    """Get available entity types and their descriptions."""
    entity_descriptions = {
        'DISEASE': 'Medical conditions and diseases',
        'MEDICATION': 'Drugs and medications',
        'SYMPTOM': 'Signs and symptoms',
        'BODY_PART': 'Anatomical parts',
        'PROCEDURE': 'Medical procedures',
        'TEST': 'Medical tests and examinations',
        'DOSAGE': 'Medication dosages and frequencies'
    }
    
    return jsonify({
        'success': True,
        'entity_types': entity_descriptions
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Medical NER API is running'
    })

if __name__ == '__main__':
    print("Starting Medical NER Flask API...")
    print("Navigate to http://localhost:5000 to use the application")
    app.run(debug=True, host='0.0.0.0', port=5000)