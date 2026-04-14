# Student Management System - Frontend Setup

## Overview
This is a pure HTML/JavaScript/CSS frontend for the Student Management System that communicates with a backend API at `http://localhost:5000`.

## Quick Start

1. **Ensure your backend is running** on `http://localhost:5000`

2. **The application is already running** - just visit:
   - http://localhost:3000/ (redirects to login or dashboard based on session)
   - http://localhost:3000/login.html (login page)
   - http://localhost:3000/dashboard.html (admin dashboard - requires authentication)
   - http://localhost:3000/student-dashboard.html (student dashboard - requires authentication)

## Features

### Login Page (`/login.html`)
- Username and password authentication
- Connects to backend API at `/api/login`
- Stores JWT token and user role in session storage
- Automatically redirects based on user role (admin → admin dashboard, others → student dashboard)

### Admin Dashboard (`/dashboard.html`)
- 8 main sections: Students, Courses, Departments, Instructors, Enrollment, Grades, Attendance, Reports
- Tab-based navigation between sections
- Each section displays data from the backend API
- Logout button in the top-right corner
- Session-based authentication (never expires)

### Student Dashboard (`/student-dashboard.html`)
- Placeholder layout for future extension
- Shows student-specific information
- Logout functionality

## Session Management

- JWT tokens are stored in **sessionStorage** (not localStorage)
- Sessions persist as long as the browser window/tab is open
- Closing the browser or tab clears the session
- Use the Logout button to manually clear the session

## API Integration

The frontend makes requests to your backend at `http://localhost:5000`. It expects the following endpoints:

### Authentication
- `POST /api/login` - Login with username and password
  - Request: `{ username: string, password: string }`
  - Response: `{ token: string, role: string, username: string }`

### Data Endpoints (require JWT token in Authorization header)
- `GET /api/students` - List all students
- `GET /api/courses` - List all courses
- `GET /api/departments` - List all departments
- `GET /api/instructors` - List all instructors
- `GET /api/enrollments` - List enrollments
- `GET /api/grades` - List grades
- `GET /api/attendance` - List attendance records
- `GET /api/reports` - Get reports data

## Files Structure

```
public/
├── index.html              # Entry point (redirects based on session)
├── login.html              # Login page
├── dashboard.html          # Admin dashboard
└── student-dashboard.html  # Student dashboard
```

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Uses Tailwind CSS v4 for styling (via CDN)
- Pure vanilla JavaScript (no frameworks)

## Development Notes

- All HTML files are served from the Next.js backend as static files
- JavaScript handles all client-side logic
- Session storage is cleared on logout
- CORS should be configured on your backend to allow requests from the frontend URL
