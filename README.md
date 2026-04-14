# Student Management System API

A Flask REST API for managing students, courses, grades, attendance, and more.

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=yourpassword
export MYSQL_DB=student_management
export JWT_SECRET_KEY=change-this-in-production
```

### 3. Run the DB migration
Run your original schema SQL, then:
```sql
-- migration_add_users.sql
CREATE TABLE IF NOT EXISTS `users` (
  `user_id`       INT PRIMARY KEY AUTO_INCREMENT,
  `username`      VARCHAR(100) UNIQUE NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role`          VARCHAR(50) DEFAULT 'staff',
  `created_at`    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Start the server
```bash
python app.py
```

---

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require a JWT Bearer token.

Include in every request:
```
Authorization: Bearer <your_token>
```

---

## Endpoints

### Auth
| Method | Endpoint         | Description              |
|--------|-----------------|--------------------------|
| POST   | /auth/register   | Register a new user      |
| POST   | /auth/login      | Login and get JWT token  |

**Register body:**
```json
{ "username": "admin", "password": "secret", "role": "admin" }
```

**Login body:**
```json
{ "username": "admin", "password": "secret" }
```

---

### Students
| Method | Endpoint                          | Description                      |
|--------|----------------------------------|----------------------------------|
| GET    | /students                         | List all students (filters: ?department_id, ?enrollment_year) |
| GET    | /students/<id>                    | Get student by ID                |
| POST   | /students                         | Add new student                  |
| PUT    | /students/<id>                    | Update student                   |
| DELETE | /students/<id>                    | Delete student                   |
| GET    | /students/<id>/enrollments        | Student's course enrollments     |
| GET    | /students/<id>/grades             | Student's grades                 |
| GET    | /students/<id>/attendance         | Student's attendance summary     |

**Add/Update Student body:**
```json
{
  "first_name": "Rahul",
  "last_name": "Sharma",
  "email": "rahul@example.com",
  "phone": "9876543210",
  "date_of_birth": "2002-05-15",
  "gender": "Male",
  "address": "123 Main St, Delhi",
  "enrollment_year": 2023,
  "department_id": 1
}
```

---

### Courses
| Method | Endpoint               | Description                            |
|--------|------------------------|----------------------------------------|
| GET    | /courses               | List all courses (?department_id)      |
| GET    | /courses/<id>          | Course details with instructors        |
| POST   | /courses               | Add new course                         |
| PUT    | /courses/<id>          | Update course                          |
| DELETE | /courses/<id>          | Delete course                          |
| GET    | /courses/<id>/stats    | Average marks, pass rate, enrollment count |

---

### Departments
| Method | Endpoint                      | Description                      |
|--------|------------------------------|----------------------------------|
| GET    | /departments                  | List all departments             |
| GET    | /departments/<id>             | Department by ID                 |
| POST   | /departments                  | Add department                   |
| PUT    | /departments/<id>             | Update department                |
| GET    | /departments/<id>/students    | Students in a department         |
| GET    | /departments/<id>/courses     | Courses in a department          |

---

### Instructors
| Method | Endpoint                                  | Description                        |
|--------|------------------------------------------|------------------------------------|
| GET    | /instructors                              | List all instructors               |
| GET    | /instructors/<id>                         | Instructor with assigned courses   |
| POST   | /instructors                              | Add instructor                     |
| PUT    | /instructors/<id>                         | Update instructor                  |
| DELETE | /instructors/<id>                         | Delete instructor                  |
| POST   | /instructors/<id>/assign-course           | Assign instructor to a course      |

---

### Enrollment
| Method | Endpoint                  | Description                                         |
|--------|--------------------------|-----------------------------------------------------|
| GET    | /enrollment               | List enrollments (?course_id, ?semester, ?year)     |
| POST   | /enrollment               | Enroll a student in a course                        |
| DELETE | /enrollment/<id>          | Drop an enrollment                                  |

**Enroll body:**
```json
{ "student_id": 1, "course_id": 2, "semester": "Fall", "year": 2024 }
```

---

### Grades
| Method | Endpoint        | Description                                        |
|--------|-----------------|----------------------------------------------------|
| GET    | /grades          | List grades (?course_id, ?semester, ?year)         |
| POST   | /grades          | Add/update a grade (upsert)                        |
| PUT    | /grades/<id>     | Update specific grade record                       |

**Grade body:**
```json
{ "enrollment_id": 5, "course_id": 2, "marks": 87.5, "grade": "A" }
```

---

### Attendance
| Method | Endpoint              | Description                                       |
|--------|-----------------------|---------------------------------------------------|
| GET    | /attendance           | Get records (?enrollment_id, ?date, ?status)      |
| POST   | /attendance           | Mark attendance (single or bulk)                  |
| PUT    | /attendance/<id>      | Update attendance status                          |

**Bulk attendance body:**
```json
{
  "records": [
    { "enrollment_id": 1, "date": "2024-11-01", "status": "present" },
    { "enrollment_id": 2, "date": "2024-11-01", "status": "absent" }
  ]
}
```

---

### Reports & Analytics
| Method | Endpoint                          | Description                                     |
|--------|----------------------------------|-------------------------------------------------|
| GET    | /reports/students/<id>           | Full report: profile + grades + attendance      |
| GET    | /reports/departments/<id>        | Department summary stats                        |
| GET    | /reports/top-students            | Top N students by avg marks (?limit, ?department_id) |
