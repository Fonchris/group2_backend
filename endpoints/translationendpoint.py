from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from fuzzywuzzy import process

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load dictionaries from JSON files
try:
    with open('dictionaries/english_ghomala.json', 'r', encoding='utf-8') as f:
        english_ghomala = json.load(f)
    with open('dictionaries/english_fulfulde.json', 'r', encoding='utf-8') as f:
        english_fulfulde = json.load(f)
    with open('dictionaries/french_ghomala.json', 'r', encoding='utf-8') as f:
        french_ghomala = json.load(f)
    with open('dictionaries/french_fulfulde.json', 'r', encoding='utf-8') as f:
        french_fulfulde = json.load(f)
except FileNotFoundError:
    # Initialize with some sample data if files don't exist
    english_ghomala = {"hello": "mbʉ́ nà", "thank you": "pua' sʉn"}
    english_fulfulde = {"hello": "salaam aleykum", "thank you": "useko"}
    french_ghomala = {"bonjour": "mbʉ́ nà", "merci": "pua' sʉn"}
    french_fulfulde = {"bonjour": "salaam aleykum", "merci": "useko"}

# Dictionary mapping for easier access
dictionaries = {
    'english-ghomala': english_ghomala,
    'english-fulfulde': english_fulfulde,
    'french-ghomala': french_ghomala,
    'french-fulfulde': french_fulfulde
}

@app.route('/api/translate', methods=['POST'])
def translate():
        data = request.json
    
        # Extract data from request
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
    
        if dict_key not in dictionaries:
          return jsonify({'error': 'Unsupported language pair'}), 400
    
        dictionary = dictionaries[dict_key]
    
    # Exact match lookup
        if text in dictionary:
          return jsonify({
            'translation': dictionary[text],
            'matchType': 'exact'
        })
    
    # If no exact match, try fuzzy matching
        if dictionary:
          best_match, score = process.extractOne(text, dictionary.keys())
        
        # If score is above threshold (70%)
        if score >= 70:
            return jsonify({
                'translation': dictionary[best_match],
                'matchType': 'fuzzy',
                'fuzzyMatchScore': score,
                'matchedWord': best_match
            })
    
    # No match found
        return jsonify({
        'translation': 'Translation not found',
        'matchType': 'none'
    })

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Return available source and target languages"""
    return jsonify({
        'sourceLanguages': ['english', 'french'],
        'targetLanguages': ['ghomala', 'fulfulde']
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Return statistics about the dictionaries"""
    stats = {
        'english-ghomala': len(english_ghomala),
        'english-fulfulde': len(english_fulfulde),
        'french-ghomala': len(french_ghomala),
        'french-fulfulde': len(french_fulfulde)
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)