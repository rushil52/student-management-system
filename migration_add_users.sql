-- Run this migration before starting the API
-- Adds a users table for authentication
use student_mgmt;

CREATE TABLE IF NOT EXISTS `users` (
  `user_id`       INT PRIMARY KEY AUTO_INCREMENT,
  `username`      VARCHAR(100) UNIQUE NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role`          VARCHAR(50) DEFAULT 'staff',
  `created_at`    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
