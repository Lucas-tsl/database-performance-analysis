
SELECT * FROM students WHERE email = 'student150000@school.com';


SELECT * FROM access_logs WHERE ip_address = '192.168.10.15';


SELECT * FROM access_logs WHERE student_id = 500 ORDER BY access_time DESC LIMIT 10;


SELECT * FROM students ORDER BY last_name ASC, first_name ASC LIMIT 50;

SELECT count(*) FROM access_logs WHERE access_time > NOW() - interval '7 days';

SELECT * FROM enrollments WHERE enrollment_date < NOW() - interval '6 months' LIMIT 100;

SELECT c.title, AVG(e.grade) as average_grade FROM courses c JOIN enrollments e ON c.course_id = e.course_id GROUP BY c.title ORDER BY average_grade DESC;

SELECT s.first_name, s.last_name, c.title FROM students s JOIN enrollments e ON s.student_id = e.student_id JOIN courses c ON e.course_id = c.course_id WHERE c.category = 'Informatique' AND e.grade = 100;

SELECT * FROM access_logs WHERE url_accessed LIKE '%/module/5';

SELECT * FROM enrollments WHERE enrollment_date > NOW() - interval '30 days' AND grade < 50;



EXPLAIN (ANALYZE, BUFFERS)
SELECT s.first_name, s.last_name, c.title FROM students s JOIN enrollments e ON s.student_id = e.student_id JOIN courses c ON e.course_id = c.course_id WHERE c.category = 'Informatique' AND e.grade = 100;


EXPLAIN (ANALYZE, BUFFERS)
SELECT count(*) FROM access_logs WHERE access_time > NOW() - interval '7 days';


EXPLAIN (ANALYZE, BUFFERS)

SELECT * FROM access_logs WHERE ip_address = '192.168.10.15';
