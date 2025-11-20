-- create_tables.sql
-- Schema matched to the project's patient.py (tables: patients, doctors)
-- Drops and recreates database for a clean start.
DROP DATABASE IF EXISTS hospital_db;
CREATE DATABASE hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE hospital_db;

-- Users table (simple auth for login.py if present)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role ENUM('admin','doctor','staff') DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Doctors table (named "doctors" to match patient.py lookups)
CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(250) NOT NULL,
    specialization VARCHAR(150),
    phone VARCHAR(30),
    email VARCHAR(255),
    degree VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Patients table (named "patients" — matches INSERT and queries in patient.py)
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(250) NOT NULL,
    age INT,
    gender ENUM('Male','Female','Other') DEFAULT 'Male',
    disease VARCHAR(255),
    assigned_doctor_id INT NULL,   -- column updated by assign_doctor()
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_patients_doctor FOREIGN KEY (assigned_doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Optional: billing table (basic); keep if other modules expect it
CREATE TABLE billing (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT,
    bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12,2) DEFAULT 0.00,
    paid TINYINT(1) DEFAULT 0,
    notes VARCHAR(1000),
    CONSTRAINT fk_billing_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_billing_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Seed data: sample admin user, one doctor and one patient
INSERT INTO users (email, password, full_name, role) VALUES
('admin@hms.com', '1234', 'Administrator', 'admin');

INSERT INTO doctors (name, specialization, phone, email, degree) VALUES
('Dr John Doe', 'General Physician', '+911234567890', 'j.doe@example.com', 'MBBS');

INSERT INTO patients (name, age, gender, disease, assigned_doctor_id) VALUES
('Sara Khan', 29, 'Female', 'Fever', 1);
