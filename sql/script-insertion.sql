BEGIN;

INSERT INTO students (first_name, last_name, email, signup_date)
SELECT 
    'Student' || id, 
    'Nom' || id, 
    'student' || id || '@school.com',
    NOW() - (random() * interval '365 days')
FROM generate_series(1, 200000) AS id;

INSERT INTO courses (title, description, category, created_at)
SELECT 
    'Cours ' || id, 
    'Description du cours ' || id, 
    CASE (floor(random() * 5))::int
        WHEN 0 THEN 'Mathématiques'
        WHEN 1 THEN 'Informatique'
        WHEN 2 THEN 'Histoire'
        WHEN 3 THEN 'Physique'
        ELSE 'Langues'
    END,
    NOW() - (random() * interval '730 days')
FROM generate_series(1, 1000) AS id;

INSERT INTO enrollments (student_id, course_id, enrollment_date, grade)
SELECT 
    (floor(random() * 200000) + 1)::int,
    (floor(random() * 1000) + 1)::int,
    NOW() - (random() * interval '300 days'),
    (floor(random() * 100))::int
FROM generate_series(1, 2200000) AS id
ON CONFLICT DO NOTHING; 

INSERT INTO access_logs (student_id, url_accessed, access_time, ip_address)
SELECT 
    (floor(random() * 200000) + 1)::int,
    '/course/' || (floor(random() * 1000) + 1)::int || '/module/' || (floor(random() * 10)::int),
    NOW() - (random() * interval '30 days'),
    ('192.168.' || (floor(random() * 255)::int) || '.' || (floor(random() * 255)::int))::inet
FROM generate_series(1, 5000000) AS id;

COMMIT;

ANALYZE;