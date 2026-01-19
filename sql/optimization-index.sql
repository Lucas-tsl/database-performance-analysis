CREATE INDEX idx_access_logs_ip ON access_logs(ip_address);

CREATE INDEX idx_access_logs_time ON access_logs(access_time);

CREATE INDEX idx_students_email ON students(email);

CREATE INDEX idx_enrollments_grade ON enrollments(grade);

CREATE INDEX idx_courses_category ON courses(category);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);

