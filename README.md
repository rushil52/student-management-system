## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
/frontend > npm install
```

### 2. Configure environment variables
```bash
set MYSQL_HOST=localhost
set MYSQL_USER=root
set MYSQL_PASSWORD=yourpassword
set MYSQL_DB=student_mgmt
set JWT_SECRET_KEY=keykeykekyekykeykekyekykeyk
```

### 3. Run the DB file, if not already

### 4. Start the server
```bash
python app.py
frontend> npm run dev
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


### Courses
| Method | Endpoint               | Description                            |
|--------|------------------------|----------------------------------------|
| GET    | /courses               | List all courses (?department_id)      |
| GET    | /courses/<id>          | Course details with instructors        |
| POST   | /courses               | Add new course                         |
| PUT    | /courses/<id>          | Update course                          |
| DELETE | /courses/<id>          | Delete course                          |
| GET    | /courses/<id>/stats    | Average marks, pass rate, enrollment count |


### Departments
| Method | Endpoint                      | Description                      |
|--------|------------------------------|----------------------------------|
| GET    | /departments                  | List all departments             |
| GET    | /departments/<id>             | Department by ID                 |
| POST   | /departments                  | Add department                   |
| PUT    | /departments/<id>             | Update department                |
| GET    | /departments/<id>/students    | Students in a department         |
| GET    | /departments/<id>/courses     | Courses in a department          |


### Instructors
| Method | Endpoint                                  | Description                        |
|--------|------------------------------------------|------------------------------------|
| GET    | /instructors                              | List all instructors               |
| GET    | /instructors/<id>                         | Instructor with assigned courses   |
| POST   | /instructors                              | Add instructor                     |
| PUT    | /instructors/<id>                         | Update instructor                  |
| DELETE | /instructors/<id>                         | Delete instructor                  |
| POST   | /instructors/<id>/assign-course           | Assign instructor to a course      |


### Enrollment
| Method | Endpoint                  | Description                                         |
|--------|--------------------------|-----------------------------------------------------|
| GET    | /enrollment               | List enrollments (?course_id, ?semester, ?year)     |
| POST   | /enrollment               | Enroll a student in a course                        |
| DELETE | /enrollment/<id>          | Drop an enrollment                                  |

### Grades
| Method | Endpoint        | Description                                        |
|--------|-----------------|----------------------------------------------------|
| GET    | /grades          | List grades (?course_id, ?semester, ?year)         |
| POST   | /grades          | Add/update a grade (upsert)                        |
| PUT    | /grades/<id>     | Update specific grade record                       |

### Attendance
| Method | Endpoint              | Description                                       |
|--------|-----------------------|---------------------------------------------------|
| GET    | /attendance           | Get records (?enrollment_id, ?date, ?status)      |
| POST   | /attendance           | Mark attendance (single or bulk)                  |
| PUT    | /attendance/<id>      | Update attendance status                          |


### Reports & Analytics
| Method | Endpoint                          | Description                                     |
|--------|----------------------------------|-------------------------------------------------|
| GET    | /reports/students/<id>           | Full report: profile + grades + attendance      |
| GET    | /reports/departments/<id>        | Department summary stats                        |
| GET    | /reports/top-students            | Top N students by avg marks (?limit, ?department_id) |
