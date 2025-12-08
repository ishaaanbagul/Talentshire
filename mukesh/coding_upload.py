import json
from pymongo import MongoClient
from config.settings import MONGO_URL, MONGO_DB_NAME
from config.logging import setup_logging

# initalize logger
logger = setup_logging()

def upload_coding_questions():
    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB_NAME]
    coding_questions = db["coding_questions"]
    
    try:
        # Load data from the JSON file
        with open("mukesh\coding_questions_clean.json", "r") as file:
            coding_data = json.load(file)
        
        # Prepare the data for insertion
        for question in coding_data:
            # Check if question already exists based on "_id"
            if not coding_questions.find_one({"_id": question["_id"]}):
                coding_questions.insert_one(question)
                logger.info(f"Question '{question['title']}' inserted successfully.")
            else:
                logger.info(f"Question '{question['title']}' already exists in MongoDB.")
        
        logger.info("Coding questions uploaded successfully.")

    except Exception as e:
        logger.error(f"Error uploading coding questions: {e}")

if __name__ == "__main__":
    upload_coding_questions()