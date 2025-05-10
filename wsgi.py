from app import app, initialize_firebase, logger, TEMPORARY_DICTIONARIES

# Initialize Firebase connection
db = initialize_firebase()
logger.info("Server starting with initialized Firebase connection")

# Log loaded dictionaries
logger.info(f"Loaded dictionaries for language pairs: {list(TEMPORARY_DICTIONARIES.keys())}")

if __name__ == "__main__":
    app.run()