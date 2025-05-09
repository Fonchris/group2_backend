from flask import Flask, jsonify, request
from flask_cors import CORS  # Make sure this import exists
from fuzzywuzzy import process
import logging
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime
from combined_dictionaries import TEMPORARY_DICTIONARIES

# Initialize Flask app with CORS
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:5500", "http://127.0.0.1:5501", 
                   "http://localhost:5500", "http://localhost:5501"],
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5501'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Firebase
def initialize_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate('translatingapp-7f27b-firebase-adminsdk-fbsvc-331e37860b.json')
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        raise

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'dictionary_languages': list(TEMPORARY_DICTIONARIES.keys())}), 200

@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        logger.info(f"Translation request: {data}")
        
        # Normalize language names
        source_lang = data.get('sourceLang', '').lower().strip()
        target_lang = data.get('targetLang', '').lower().strip()
        text = data.get('text', '').lower().strip()
        
        # Validate input
        if not text:
            return jsonify({'error': 'No text provided for translation'}), 400
            
        if not source_lang or not target_lang:
            return jsonify({'error': 'Source or target language not specified'}), 400
        
        # Determine which dictionary to use
        dict_key = f"{source_lang}-{target_lang}"
        
        if dict_key not in TEMPORARY_DICTIONARIES:
            return jsonify({
                'translation': f"Translation between {source_lang} and {target_lang} is not currently supported",
                'matchType': 'none',
                'supportedPairs': list(TEMPORARY_DICTIONARIES.keys())
            }), 404
        
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
            
            # If score is above threshold
            if score >= 70:  # Increased threshold for better matches
                return jsonify({
                    'originalText': text,
                    'translation': dictionary[best_match],
                    'matchType': 'fuzzy',
                    'fuzzyMatchScore': score,
                    'matchedWord': best_match,
                    'sourceLang': source_lang,
                    'targetLang': target_lang
                }), 200
        
        # No match found - check Firebase for pending contributions
        db = initialize_firebase()
        pending_translation = db.collection('contributions').where('source_text', '==', text)\
            .where('source_language', '==', source_lang)\
            .where('target_language', '==', target_lang)\
            .where('status', '==', 'pending')\
            .limit(1).get()
        
        if pending_translation:
            pending_data = pending_translation[0].to_dict()
            return jsonify({
                'originalText': text,
                'translation': pending_data['target_text'],
                'matchType': 'pending',
                'note': 'This is a pending contribution awaiting review',
                'sourceLang': source_lang,
                'targetLang': target_lang
            }), 200
        
        # No matches found anywhere
        return jsonify({
            'originalText': text,
            'translation': f"No translation found for '{text}'",
            'matchType': 'none',
            'sourceLang': source_lang,
            'targetLang': target_lang,
            'suggestion': 'Consider contributing a translation'
        }), 404
        
    except Exception as e:
        logger.error(f"Error processing translation request: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@app.route('/api/contribute', methods=['POST'])
def contribute():
    try:
        # Get database reference
        db = initialize_firebase()
        
        # Parse and validate input data
        data = request.json
        logger.info(f"Received contribution data: {data}")
        
        # Extract required fields
        source_text = data.get('source_text', '').strip().lower()
        target_text = data.get('target_text', '').strip()
        source_language = data.get('source_language', '').lower().strip()
        target_language = data.get('target_language', '').lower().strip()
        
        # Extract optional fields
        source_example = data.get('source_example', '').strip()
        target_example = data.get('target_example', '').strip()
        
        # Validate required fields
        if not source_text or not target_text:
            return jsonify({'error': 'Source text and target text are required'}), 400
        
        if not source_language or not target_language:
            return jsonify({'error': 'Source language and target language are required'}), 400
        
        # Create dictionary key for the language pair
        dict_key = f"{source_language}-{target_language}"
        
        # Check if this exact translation already exists in either dictionaries or Firebase
        existing_translation = None
        
        # Check in TEMPORARY_DICTIONARIES first
        if dict_key in TEMPORARY_DICTIONARIES:
            if source_text in TEMPORARY_DICTIONARIES[dict_key]:
                existing_translation = TEMPORARY_DICTIONARIES[dict_key][source_text]
        
        # If not found, check approved translations in Firebase
        if not existing_translation:
            approved_translation = db.collection('contributions')\
                .where('source_text', '==', source_text)\
                .where('source_language', '==', source_language)\
                .where('target_language', '==', target_language)\
                .where('status', '==', 'validated')\
                .limit(1).get()
            
            if approved_translation:
                existing_translation = approved_translation[0].to_dict().get('target_text')
        
        if existing_translation:
            return jsonify({
                'error': 'This translation already exists',
                'existing_translation': existing_translation,
                'status': 'duplicate'
            }), 409
        
        # Create a unique ID for the contribution
        contribution_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Create contribution object
        contribution = {
            'id': contribution_id,
            'source_text': source_text,
            'target_text': target_text,
            'source_language': source_language,
            'target_language': target_language,
            'source_example': source_example,
            'target_example': target_example,
            'status': 'pending',
            'created_at': timestamp,
            'updated_at': timestamp,
            'votes': 0,
            'reviewed': False
        }
        
        # Save to Firebase in multiple places for different query patterns
        
        # 1. Main contributions collection
        db.collection('contributions').document(contribution_id).set(contribution)
        
        # 2. Language pair specific collection
        lang_pair_ref = db.collection('language_pairs').document(dict_key)
        
        # Initialize language pair document if it doesn't exist
        if not lang_pair_ref.get().exists:
            lang_pair_ref.set({
                'source_language': source_language,
                'target_language': target_language,
                'total_contributions': 0,
                'pending_contributions': 0,
                'validated_contributions': 0,
                'last_updated': timestamp
            })
        
        # Update counters
        lang_pair_ref.update({
            'total_contributions': firestore.Increment(1),
            'pending_contributions': firestore.Increment(1),
            'last_updated': timestamp
        })
        
        # Add to translations subcollection
        lang_pair_ref.collection('translations').document(contribution_id).set(contribution)
        
        # 3. User contributions collection (if you have user auth)
        # This would require user authentication to be implemented
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Contribution received and pending review',
            'contribution_id': contribution_id,
            'status': 'pending',
            'language_pair': dict_key
        }), 201
        
    except Exception as e:
        logger.error(f"Error processing contribution: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

if __name__ == "__main__":
    # Initialize Firebase connection
    db = initialize_firebase()
    logger.info("Server starting with initialized Firebase connection")
    
    # Log loaded dictionaries
    logger.info(f"Loaded dictionaries for language pairs: {list(TEMPORARY_DICTIONARIES.keys())}")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)