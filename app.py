from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import process
from translation_dictionaries import TEMPORARY_DICTIONARIES
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Temporary in-memory dictionaries

@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        logger.info(f"Raw received data: {data}")
        # Normalize language names (remove apostrophes and accents)
        source_lang = data.get('sourceLang', '').lower().replace("'", "").replace("á", "a")
        target_lang = data.get('targetLang', '').lower().replace("'", "").replace("á", "a")
        text = data.get('text', '').lower().strip()
        
        logger.info(f"Normalized translation request: {source_lang} -> {target_lang}: '{text}'")
        
        # Validate input
        if not text:
            return jsonify({'error': 'No text provided for translation'}), 400
            
        if not source_lang or not target_lang:
            return jsonify({'error': 'Source or target language not specified'}), 400
        
        # Determine which dictionary to use
        dict_key = f"{source_lang}-{target_lang}"
        
        if dict_key not in TEMPORARY_DICTIONARIES:
            return jsonify({'error': 'Unsupported language pair'}), 400
        
        dictionary = TEMPORARY_DICTIONARIES[dict_key]
        
        # Exact match lookup
        if text in dictionary:
            return jsonify({
                'originalText': text,
                'translation': dictionary[text],
                'matchType': 'exact',
                'sourceLang': source_lang,
                'targetLang': target_lang
            }), 200
        
        # If no exact match, try fuzzy matching
        if dictionary:
            best_match, score = process.extractOne(text, dictionary.keys())
            
            # If score is above threshold (70%)
            if score >= 30:
                return jsonify({
                    'originalText': text,
                    'translation': dictionary[best_match],
                    'matchType': 'fuzzy',
                    'fuzzyMatchScore': score,
                    'matchedWord': best_match,
                    'sourceLang': source_lang,
                    'targetLang': target_lang
                }),200
        
        # No match found
        return jsonify({
            'originalText': text,
            'translation': f"Sorry, no translation found for '{text}'",
            'matchType': 'none',
            'sourceLang': source_lang,
            'targetLang': target_lang
        }),404
    
    except Exception as e:
        logger.error(f"Error processing translation request: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Return available source and target languages"""
    return jsonify({
        'sourceLanguages': ['english', 'french'],
        'targetLanguages': ['ghomala', 'fulfulde']
    })





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)