#schemas.py
import psycopg
from pymongo import MongoClient
from src.config.settings import POSTGRES_DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, MONGO_URL, MONGO_DB_NAME
from src.config.logging import setup_logging
from pymongo.errors import CollectionInvalid

# Initialize logger
logger = setup_logging()

# PostgreSQL Schema Initialization
def init_postgres():
    try:
        # Connect to PostgreSQL
        conn = psycopg.connect(
            dbname=POSTGRES_DB_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )

        conn.autocommit = True
        cur = conn.cursor()

        # ENUMS -----------------------------------------------------------
        cur.execute(""" 
        DO $$ BEGIN 
            CREATE TYPE question_type_enum AS ENUM ('MCQ', 'CODING'); 
        EXCEPTION WHEN duplicate_object THEN null; 
        END $$;

        DO $$ BEGIN 
            CREATE TYPE test_status_enum AS ENUM ('DRAFT', 'ACTIVE', 'ARCHIVED'); 
        EXCEPTION WHEN duplicate_object THEN null; 
        END $$;

        DO $$ BEGIN 
            CREATE TYPE assignment_status_enum AS ENUM ('ASSIGNED', 'STARTED', 'COMPLETED', 'EXPIRED'); 
        EXCEPTION WHEN duplicate_object THEN null; 
        END $$;

        DO $$ BEGIN 
            CREATE TYPE completion_status_enum AS ENUM ('PASSED', 'FAILED', 'INCOMPLETE'); 
        EXCEPTION WHEN duplicate_object THEN null; 
        END $$;

        DO $$ BEGIN 
            CREATE TYPE role_name_enum AS ENUM ('ADMIN', 'RECRUITER', 'CANDIDATE'); 
        EXCEPTION WHEN duplicate_object THEN null; 
        END $$;
        """)

        # TABLES ----------------------------------------------------------
        cur.execute("""
        CREATE TABLE IF NOT EXISTS mcq_questions (
            mcq_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            question_text TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer VARCHAR,
            difficulty_level VARCHAR,
            language VARCHAR  
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS unified_questions (
            question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source_id UUID,
            question_text TEXT,
            difficulty_level VARCHAR,
            language VARCHAR,
            type question_type_enum,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            full_name VARCHAR,
            email VARCHAR UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            test_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            test_name VARCHAR,
            created_by UUID REFERENCES users(user_id),
            duration_minutes INT,
            status test_status_enum,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS test_questions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            test_id UUID REFERENCES tests(test_id) ON DELETE CASCADE,
            question_id UUID REFERENCES unified_questions(question_id) ON DELETE CASCADE,
            question_type question_type_enum,
            order_index INT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            full_name VARCHAR,
            email VARCHAR UNIQUE,
            phone VARCHAR UNIQUE,
            experience_years INT,
            skills TEXT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS test_assignments (
            assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            test_id UUID REFERENCES tests(test_id) ON DELETE CASCADE,
            candidate_id UUID REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status assignment_status_enum,
            scheduled_start_time TIMESTAMP,
            scheduled_end_time TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS test_answers (
            answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            assignment_id UUID REFERENCES test_assignments(assignment_id) ON DELETE CASCADE,
            question_id UUID REFERENCES unified_questions(question_id),
            question_type question_type_enum,
            selected_option VARCHAR,
            code_submission TEXT,
            code_output TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_correct BOOLEAN,
            score NUMERIC,
            time_spent_seconds INT,
            code_analysis TEXT,
            code_quality_score NUMERIC,
            ai_review_notes TEXT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            assignment_id UUID UNIQUE REFERENCES test_assignments(assignment_id) ON DELETE CASCADE,
            total_score NUMERIC,
            section_scores JSONB,
            time_taken_seconds INT,
            completion_status completion_status_enum,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS test_autosave (
            autosave_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            assignment_id UUID REFERENCES test_assignments(assignment_id) ON DELETE CASCADE,
            question_id UUID REFERENCES unified_questions(question_id),
            draft_answer JSONB,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            role_name role_name_enum
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            user_role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
            role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE
        );
        """)

        # Indexing foreign key columns for optimization
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_test_id ON test_questions(test_id);
        CREATE INDEX IF NOT EXISTS idx_question_id ON test_questions(question_id);
        CREATE INDEX IF NOT EXISTS idx_candidate_id ON test_assignments(candidate_id);
        CREATE INDEX IF NOT EXISTS idx_test_id_assignments ON test_assignments(test_id);
        CREATE INDEX IF NOT EXISTS idx_question_id_answers ON test_answers(question_id);
        """)

        conn.commit()
        cur.close()
        conn.close()

        logger.info("PostgreSQL tables created successfully.")

    except Exception as e:
        logger.error(f"Error initializing PostgreSQL: {e}")
        raise

# MongoDB Schema Initialization
def init_mongo():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URL)
        db = client[MONGO_DB_NAME]

        # Coding Questions Collection
        coding_questions = db["coding_questions"]

        try:
            # Insert a dummy document to initialize the collection if needed
            coding_questions.insert_one({
                "id": 1, 
                "title": "Find the Maximum Element in an Array",
                "description": "Given an array of integers, return the maximum element present in the array.",
                "difficulty": "Easy",
                "labels": ["array", "linear-scan", "basic-logic"],
                "sample_input": [3, 1, 7, 4, 2],
                "sample_output": 7,
                "constraints": "1 <= array length <= 10^5; -10^9 <= array[i] <= 10^9"
            })
            logger.info("Collection 'coding_questions' created successfully.")
        except CollectionInvalid:
            logger.info("Collection 'coding_questions' already exists.")

        # Create indexes
        coding_questions.create_index("difficulty", unique=False)  # Index on difficulty for fast queries
        coding_questions.create_index("labels", unique=False)  # Index on labels to speed up searching by tags
        coding_questions.create_index("title", unique=False)  # Index on title for fast search by title
        coding_questions.create_index([("difficulty", 1), ("labels", 1)], unique=False)  # Compound index on difficulty and labels

        logger.info("MongoDB initialized with coding_questions collection & indexes.")

    except Exception as e:
        logger.error(f"Error initializing MongoDB: {e}")
        raise

# Main Execution Logic
if __name__ == "__main__":
    try:
        # Initialize both MongoDB and PostgreSQL
        init_mongo()  # Initialize MongoDB
        init_postgres()  # Initialize PostgreSQL
        logger.info("Hybrid Database Initialization Completed.")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
