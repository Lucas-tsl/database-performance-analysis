DROP TABLE IF EXISTS access_logs;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;


CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    signup_date TIMESTAMPTZ DEFAULT NOW() 
);


CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(student_id),
    course_id INT NOT NULL REFERENCES courses(course_id),
    enrollment_date TIMESTAMPTZ DEFAULT NOW(),
    grade INT CHECK (grade BETWEEN 0 AND 100),
    CONSTRAINT unique_enrollment UNIQUE (student_id, course_id)
);


CREATE TABLE access_logs (
    log_id BIGSERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    url_accessed TEXT NOT NULL,
    access_time TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET
);

// 10 requete + analyse des performances