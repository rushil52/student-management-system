use student_mgmt;

CREATE TABLE IF NOT EXISTS `departments` (
  `department_id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(100),
  `head_of_department` varchar(100)
);

CREATE TABLE IF NOT EXISTS `students` (
  `student_id` int PRIMARY KEY AUTO_INCREMENT,
  `first_name` varchar(100),
  `last_name` varchar(100),
  `email` varchar(150) UNIQUE,
  `phone` varchar(20),
  `date_of_birth` date,
  `gender` varchar(10),
  `address` varchar(255),
  `enrollment_year` int,
  `department_id` int
);

CREATE TABLE IF NOT EXISTS `courses` (
  `course_id` int PRIMARY KEY AUTO_INCREMENT,
  `course_name` varchar(150),
  `course_code` varchar(50) UNIQUE,
  `credits` int,
  `department_id` int
);

CREATE TABLE IF NOT EXISTS `instructors` (
  `instructor_id` int PRIMARY KEY AUTO_INCREMENT,
  `first_name` varchar(100),
  `last_name` varchar(100),
  `email` varchar(150) UNIQUE,
  `phone` varchar(20),
  `department_id` int
);

CREATE TABLE IF NOT EXISTS `course_instructors` (
  `course_id` int,
  `instructor_id` int,
  `primary` key(course_id,instructor_id)
);

CREATE TABLE IF NOT EXISTS `enrollment` (
  `enrollment_id` int PRIMARY KEY AUTO_INCREMENT,
  `student_id` int,
  `course_id` int,
  `semester` varchar(20),
  `year` int
);

CREATE TABLE IF NOT EXISTS `grades` (
  `grade_id` int PRIMARY KEY AUTO_INCREMENT,
  `enrollment_id` int,
  `course_id` int,
  `marks` decimal(5,2),
  `grade` varchar(5),
  `updated_at` timestamp
);

CREATE TABLE IF NOT EXISTS `attendance` (
  `attendance_id` int PRIMARY KEY AUTO_INCREMENT,
  `enrollment_id` int,
  `date` date,
  `status` varchar(20)
);

CREATE TABLE `student_updates_log` (
  `log_id` int PRIMARY KEY AUTO_INCREMENT,
  `student_id` int,
  `updated_at` timestamp
);

ALTER TABLE `students` ADD FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`);

ALTER TABLE `courses` ADD FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`);

ALTER TABLE `instructors` ADD FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`);

ALTER TABLE `enrollment` ADD FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`);

ALTER TABLE `enrollment` ADD FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`);

ALTER TABLE `grades` ADD FOREIGN KEY (`enrollment_id`) REFERENCES `enrollment` (`enrollment_id`);

ALTER TABLE `attendance` ADD FOREIGN KEY (`enrollment_id`) REFERENCES `enrollment` (`enrollment_id`);

ALTER TABLE `course_instructors` ADD FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`);

ALTER TABLE `course_instructors` ADD FOREIGN KEY (`instructor_id`) REFERENCES `instructors` (`instructor_id`);

ALTER TABLE `grades` ADD FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`);


CREATE TABLE IF NOT EXISTS `users` (
  `user_id`       INT PRIMARY KEY AUTO_INCREMENT,
  `username`      VARCHAR(100) UNIQUE NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role`          VARCHAR(50) DEFAULT 'staff',
  `created_at`    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
