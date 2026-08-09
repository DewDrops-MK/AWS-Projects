CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    job_title VARCHAR(100),
    department VARCHAR(100),
    location VARCHAR(100),
    joining_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO employees (first_name, last_name, email, phone, job_title, department, location, joining_date) VALUES
('John', 'Smith', 'john.smith@company.com', '555-0101', 'Software Engineer', 'Engineering', 'New York', '2024-01-15'),
('Sarah', 'Johnson', 'sarah.johnson@company.com', '555-0102', 'Product Manager', 'Product', 'San Francisco', '2024-02-01'),
('Michael', 'Chen', 'michael.chen@company.com', '555-0103', 'Data Analyst', 'Analytics', 'Chicago', '2024-02-15'),
('Emily', 'Davis', 'emily.davis@company.com', '555-0104', 'HR Specialist', 'Human Resources', 'Boston', '2024-03-01'),
('David', 'Wilson', 'david.wilson@company.com', '555-0105', 'DevOps Engineer', 'Engineering', 'Seattle', '2024-03-15');