-- PostgreSQL Initialization Script for CodePlay
-- Creates test_answer table for storing candidate test submissions

-- Create test_answer table
CREATE TABLE IF NOT EXISTS test_answer (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(255) NOT NULL,
    problem_id VARCHAR(255) NOT NULL,
    language VARCHAR(50) NOT NULL,
    code TEXT NOT NULL,
    stdin TEXT DEFAULT '',
    stdout TEXT DEFAULT '',
    output TEXT DEFAULT '',
    status VARCHAR(50) DEFAULT 'pending',
    is_passed BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_candidate_id ON test_answer(candidate_id);
CREATE INDEX idx_problem_id ON test_answer(problem_id);
CREATE INDEX idx_candidate_problem ON test_answer(candidate_id, problem_id);
CREATE INDEX idx_timestamp ON test_answer(timestamp);
CREATE INDEX idx_status ON test_answer(status);

-- Add comments
COMMENT ON TABLE test_answer IS 'Stores test submissions from candidates with code, execution results, and pass/fail status';
COMMENT ON COLUMN test_answer.candidate_id IS 'ID of the candidate taking the test';
COMMENT ON COLUMN test_answer.problem_id IS 'ID of the coding problem';
COMMENT ON COLUMN test_answer.language IS 'Programming language used (python, java, sql, pyspark)';
COMMENT ON COLUMN test_answer.code IS 'The code submitted by candidate';
COMMENT ON COLUMN test_answer.stdin IS 'Input provided to the code (from sample_input or manual)';
COMMENT ON COLUMN test_answer.stdout IS 'Raw output from code execution';
COMMENT ON COLUMN test_answer.output IS 'Processed output for comparison';
COMMENT ON COLUMN test_answer.status IS 'Execution status: pending, success, error, timeout';
COMMENT ON COLUMN test_answer.is_passed IS 'Whether output matches expected sample_output';
