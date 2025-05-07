import firebase_admin
from firebase_admin import credentials, firestore
from flask import jsonify, request
from fuzzywuzzy import process
import logging
import uuid
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Firebase (should be done once at application startup)
# This assumes you've set up your Firebase credentials correctly
def initialize_firebase():
    try:
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate('path/to/your/firebase-credentials.json')
            firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        return db
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        raise

# Global variable to store pending contributions
PENDING_CONTRIBUTIONS = {
    'english-ghomala': {},
    'french-ghomala': {},
    'ghomala-english': {},
    'ghomala-french': {}
}

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

@app.route('/api/contribute', methods=['POST'])
def contribute():
    try:
        # Get database reference
        db = initialize_firebase()
        
        # Parse and validate input data
        data = request.json
        logger.info(f"Received contribution data: {data}")
        
        # Extract required fields
        source_text = data.get('source_text', '').strip()
        target_text = data.get('target_text', '').strip()
        source_language = data.get('source_language', '').lower().replace("'", "").replace("á", "a")
        target_language = data.get('target_language', '').lower().replace("'", "").replace("á", "a")
        
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
        
        # Check if the language pair is supported
        if dict_key not in PENDING_CONTRIBUTIONS:
            return jsonify({'error': f'Unsupported language pair: {dict_key}'}), 400
        
        # Create a unique ID for the contribution
        contribution_id = str(uuid.uuid4())
        
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
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add to pending contributions dictionary
        if dict_key not in PENDING_CONTRIBUTIONS:
            PENDING_CONTRIBUTIONS[dict_key] = {}
        
        PENDING_CONTRIBUTIONS[dict_key][source_text] = {
            'translation': target_text,
            'status': 'pending',
            'source_example': source_example,
            'target_example': target_example
        }
        
        # Save to Firebase
        contributions_ref = db.collection('contributions')
        
        # Using a structure that's scalable and queryable
        contributions_ref.document(contribution_id).set(contribution)
        
        # Also save in language-pair specific collection for easier querying
        lang_pair_ref = db.collection('language_pairs').document(dict_key)
        
        # Check if the document exists, create if it doesn't
        lang_pair_doc = lang_pair_ref.get()
        if not lang_pair_doc.exists:
            lang_pair_ref.set({
                'source_language': source_language,
                'target_language': target_language,
                'total_contributions': 0,
                'pending_contributions': 0,
                'validated_contributions': 0,
                'rejected_contributions': 0
            })
        
        # Update language pair statistics
        lang_pair_ref.update({
            'total_contributions': firestore.Increment(1),
            'pending_contributions': firestore.Increment(1)
        })
        
        # Add contribution to the language pair subcollection
        lang_pair_ref.collection('translations').document(contribution_id).set({
            'source_text': source_text,
            'target_text': target_text,
            'status': 'pending',
            'source_example': source_example,
            'target_example': target_example,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Contribution received and pending review',
            'contribution_id': contribution_id,
            'status': 'pending'
        }), 201
        
    except Exception as e:
        logger.error(f"Error processing contribution: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

# Optional: Adding an endpoint to retrieve pending contributions
@app.route('/api/contributions', methods=['GET'])
def list_contributions():
    try:
        # Get query parameters
        status = request.args.get('status', 'pending')
        source_language = request.args.get('source_language', '').lower().replace("'", "").replace("á", "a")
        target_language = request.args.get('target_language', '').lower().replace("'", "").replace("á", "a")
        
        # Initialize Firebase
        db = initialize_firebase()
        
        # Construct query
        query = db.collection('contributions').where('status', '==', status)
        
        if source_language:
            query = query.where('source_language', '==', source_language)
        
        if target_language:
            query = query.where('target_language', '==', target_language)
        
        # Execute query
        contributions = [doc.to_dict() for doc in query.get()]
        
        return jsonify({
            'contributions': contributions,
            'count': len(contributions)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving contributions: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

# Optional: Adding an endpoint to update contribution status (for admins)
@app.route('/api/contributions/<contribution_id>/status', methods=['PUT'])
def update_contribution_status(contribution_id):
    try:
        # Get request data
        data = request.json
        new_status = data.get('status')
        
        # Validate status
        if new_status not in ['pending', 'validated', 'rejected']:
            return jsonify({'error': 'Invalid status. Must be pending, validated, or rejected'}), 400
        
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get the contribution
        contribution_ref = db.collection('contributions').document(contribution_id)
        contribution_doc = contribution_ref.get()
        
        if not contribution_doc.exists:
            return jsonify({'error': 'Contribution not found'}), 404
            
        contribution_data = contribution_doc.to_dict()
        old_status = contribution_data.get('status')
        
        # If status is not changing, return early
        if old_status == new_status:
            return jsonify({'message': f'Status already set to {new_status}'}), 200
            
        # Update the contribution
        contribution_ref.update({
            'status': new_status,
            'updated_at': datetime.now().isoformat()
        })
        
        # Update the language pair statistics
        dict_key = f"{contribution_data.get('source_language')}-{contribution_data.get('target_language')}"
        lang_pair_ref = db.collection('language_pairs').document(dict_key)
        
        # Decrement the old status count and increment the new status count
        lang_pair_ref.update({
            f'{old_status}_contributions': firestore.Increment(-1),
            f'{new_status}_contributions': firestore.Increment(1)
        })
        
        # Update the translation in the language pair subcollection
        translation_ref = lang_pair_ref.collection('translations').document(contribution_id)
        translation_ref.update({
            'status': new_status,
            'updated_at': datetime.now().isoformat()
        })
        
        # If status is validated, add to the TEMPORARY_DICTIONARIES
        if new_status == 'validated':
            # Get source and target text
            source_text = contribution_data.get('source_text')
            target_text = contribution_data.get('target_text')
            
            # Add to dictionary
            if dict_key in TEMPORARY_DICTIONARIES:
                TEMPORARY_DICTIONARIES[dict_key][source_text] = target_text
        
        return jsonify({
            'success': True,
            'message': f'Contribution status updated to {new_status}',
            'contribution_id': contribution_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating contribution status: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500