
CREATE DATABASE IF NOT EXISTS lex_guardian;
USE lex_guardian;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    case_number VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    court_name VARCHAR(255),
    opposing_party VARCHAR(255),
    status ENUM('Active', 'Closed', 'Pending') DEFAULT 'Active',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS case_timeline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT,
    hearing_date DATE NOT NULL,
    proceedings TEXT,
    order_summary TEXT,
    next_action TEXT,
    deadline DATE,
    ai_summary TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT,
    file_name VARCHAR(255),
    file_path TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    reminder_date DATE NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id) REFERENCES cases(id) ON DELETE CASCADE
);
