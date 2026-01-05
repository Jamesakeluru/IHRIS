CREATE DATABASE IF NOT EXISTS yutees_ihris_db;

USE yutees_ihris_db;

CREATE TABLE IF NOT EXISTS employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    hire_date DATE,
    contact VARCHAR(100),
    status ENUM('Active', 'Inactive') DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    date DATE NOT NULL,
    check_in TIME,
    check_out TIME,
    hours_worked DECIMAL(5,2),
    logged_by VARCHAR(100),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS leave_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    leave_type ENUM('Annual', 'Sick', 'Emergency') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100) NOT NULL,
    item_type ENUM('Uniform', 'Radio', 'Boots', 'Other') NOT NULL,
    serial_number VARCHAR(100) UNIQUE,
    assigned_to INT,
    date_assigned DATE,
    condition ENUM('New', 'Good', 'Fair', 'Poor') DEFAULT 'New',
    FOREIGN KEY (assigned_to) REFERENCES employees(id)
);