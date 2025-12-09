-- ========================================
-- PostgreSQL Queries for test_answer Table
-- For Your Team's Use
-- ========================================

-- 1. View all submissions for a candidate
SELECT 
    id,
    candidate_id,
    problem_id,
    language,
    status,
    is_passed,
    timestamp
FROM test_answer
WHERE candidate_id = 'user_001'
ORDER BY timestamp DESC;

-- 2. View a specific submission with code
SELECT 
    id,
    candidate_id,
    problem_id,
    language,
    code,           -- FULL CODE STORED HERE
    stdin,
    stdout,
    output,
    status,
    is_passed,
    timestamp
FROM test_answer
WHERE id = 1;

-- 3. Count submissions by language
SELECT 
    language,
    COUNT(*) as submission_count,
    SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) as passed_count,
    SUM(CASE WHEN is_passed THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as pass_rate
FROM test_answer
GROUP BY language
ORDER BY submission_count DESC;

-- 4. View pass/fail statistics for each problem
SELECT 
    problem_id,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) as passed,
    SUM(CASE WHEN is_passed THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as pass_percentage
FROM test_answer
GROUP BY problem_id
ORDER BY problem_id;

-- 5. View all submissions for a specific problem
SELECT 
    id,
    candidate_id,
    language,
    status,
    is_passed,
    LENGTH(code) as code_length,
    timestamp
FROM test_answer
WHERE problem_id = '1'
ORDER BY timestamp DESC;

-- 6. View failed submissions
SELECT 
    id,
    candidate_id,
    problem_id,
    language,
    status,
    stdout,
    output,
    timestamp
FROM test_answer
WHERE is_passed = false
ORDER BY timestamp DESC;

-- 7. View recent submissions (last 10)
SELECT 
    id,
    candidate_id,
    problem_id,
    language,
    is_passed,
    timestamp
FROM test_answer
ORDER BY timestamp DESC
LIMIT 10;

-- 8. View code for a specific submission (to review)
SELECT 
    id,
    candidate_id,
    problem_id,
    language,
    code,                  -- RETRIEVE FULL CODE
    stdin,
    stdout,
    output,
    is_passed
FROM test_answer
WHERE id = 1;

-- 9. Search submissions by code content (e.g., find all submissions using print())
SELECT 
    id,
    candidate_id,
    problem_id,
    language,
    timestamp
FROM test_answer
WHERE code ILIKE '%print%'
ORDER BY timestamp DESC;

-- 10. Get statistics for a candidate
SELECT 
    candidate_id,
    COUNT(*) as total_submissions,
    COUNT(DISTINCT problem_id) as problems_attempted,
    SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) as problems_passed,
    COUNT(DISTINCT language) as languages_used,
    MAX(timestamp) as last_submission
FROM test_answer
GROUP BY candidate_id
ORDER BY total_submissions DESC;

-- 11. View execution timeline for a candidate
SELECT 
    timestamp,
    problem_id,
    language,
    status,
    is_passed
FROM test_answer
WHERE candidate_id = 'user_001'
ORDER BY timestamp ASC;

-- 12. Detailed report - All submissions with full info
SELECT 
    id,
    candidate_id,
    problem_id,
    language,
    code,
    stdin,
    stdout,
    output,
    status,
    is_passed,
    timestamp,
    created_at,
    updated_at
FROM test_answer
ORDER BY timestamp DESC
LIMIT 20;

-- 13. Check table statistics
SELECT 
    COUNT(*) as total_rows,
    COUNT(DISTINCT candidate_id) as total_candidates,
    COUNT(DISTINCT problem_id) as total_problems,
    COUNT(DISTINCT language) as languages_count,
    MIN(timestamp) as first_submission,
    MAX(timestamp) as last_submission,
    AVG(LENGTH(code)) as avg_code_length
FROM test_answer;

-- 14. Performance analysis - Language difficulty
SELECT 
    language,
    AVG(LENGTH(code)) as avg_code_length,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN is_passed THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as success_rate
FROM test_answer
GROUP BY language
ORDER BY success_rate DESC;

-- 15. Export all submissions to CSV format
-- Run in psql with: \copy (SELECT ...) TO 'file.csv' WITH CSV HEADER
COPY (
    SELECT 
        id,
        candidate_id,
        problem_id,
        language,
        SUBSTRING(code, 1, 100) as code_preview,
        SUBSTRING(stdin, 1, 50) as stdin_preview,
        SUBSTRING(stdout, 1, 50) as stdout_preview,
        status,
        is_passed,
        timestamp
    FROM test_answer
    ORDER BY timestamp DESC
) TO '/tmp/submissions.csv' WITH CSV HEADER;

-- ========================================
-- Data Validation Queries
-- ========================================

-- Check for submissions with empty code (should be 0)
SELECT COUNT(*) as empty_code_count
FROM test_answer
WHERE code IS NULL OR code = '';

-- Check for submissions with NULL is_passed (should be 0)
SELECT COUNT(*) as null_is_passed
FROM test_answer
WHERE is_passed IS NULL;

-- Verify all required columns have data
SELECT 
    COUNT(*) as total,
    COUNT(candidate_id) as with_candidate_id,
    COUNT(problem_id) as with_problem_id,
    COUNT(language) as with_language,
    COUNT(code) as with_code,
    COUNT(stdin) as with_stdin,
    COUNT(stdout) as with_stdout,
    COUNT(status) as with_status,
    COUNT(is_passed) as with_is_passed
FROM test_answer;

-- ========================================
-- End of Queries
-- ========================================
