-- Face Recognition Attendance System Database
-- Database: face_attendance

CREATE DATABASE IF NOT EXISTS face_attendance DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE face_attendance;

-- Department Table
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Department Name',
    description TEXT COMMENT 'Description',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Created At',
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT 'Username',
    password VARCHAR(255) NOT NULL COMMENT 'Password Hash',
    real_name VARCHAR(50) NOT NULL COMMENT 'Real Name',
    employee_no VARCHAR(50) NOT NULL UNIQUE COMMENT 'Employee No',
    department_id INT COMMENT 'Department ID',
    role VARCHAR(20) DEFAULT 'user' COMMENT 'Role: admin/user',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Is Active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Created At',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated At',
    INDEX idx_username (username),
    INDEX idx_employee_no (employee_no),
    INDEX idx_department (department_id),
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Face Encoding Table
CREATE TABLE IF NOT EXISTS face_encodings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'User ID',
    encoding_data TEXT NOT NULL COMMENT 'Face Encoding Data JSON',
    image_path VARCHAR(255) NOT NULL COMMENT 'Image Path',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Created At',
    INDEX idx_user (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'User ID',
    attendance_date DATE NOT NULL COMMENT 'Attendance Date',
    check_in_time DATETIME COMMENT 'Check In Time',
    check_out_time DATETIME COMMENT 'Check Out Time',
    check_in_image VARCHAR(255) COMMENT 'Check In Image',
    check_out_image VARCHAR(255) COMMENT 'Check Out Image',
    status VARCHAR(20) DEFAULT 'normal' COMMENT 'Status: normal/late/early/absent',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Created At',
    INDEX idx_user (user_id),
    INDEX idx_date (attendance_date),
    INDEX idx_user_date (user_id, attendance_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
