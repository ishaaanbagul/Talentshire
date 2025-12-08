import csv
import psycopg
from config.settings import POSTGRES_DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
from config.logging import setup_logging

# initalize logger
logger = setup_logging()

def upload_mcq_questions():
    try:
        # Connect to PostgreSQL
        conn = psycopg.connect(
            dbname=POSTGRES_DB_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cur = conn.cursor()

        # Open and read the CSV file containing MCQ data
        with open(r"C:\Users\ishaan.bagul\OneDrive - Ampcus Tech Pvt Ltd\Desktop\AI driven technical assesment platform\Talentshire\mukesh\mcq_questions.csv", "r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Prepare the data for insertion into the table
                question_text = row['question_text']
                option_a = row['option_a']
                option_b = row['option_b']
                option_c = row['option_c']
                option_d = row['option_d']
                correct_answer = row['correct_answer']
                difficulty_level = row['difficulty_level']
                language = row['language']

                # Insert data into PostgreSQL mcq_questions table
                cur.execute("""
                    INSERT INTO mcq_questions (question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, language)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, language))

                logger.info(f"MCQ Question '{question_text}' inserted successfully.")

        # Commit changes and close the connection
        conn.commit()
        cur.close()
        conn.close()

        logger.info("MCQ questions uploaded successfully.")

    except Exception as e:
        logger.error(f"Error uploading MCQ questions: {e}")

if __name__ == "__main__":
    upload_mcq_questions()