from flask import Flask
from flask_cors import CORS

from flask_jwt_extended import JWTManager
from config import Config
from db import init_db
from routes.auth import auth_bp
from routes.students import students_bp
from routes.courses import courses_bp
from routes.departments import departments_bp
from routes.instructors import instructors_bp
from routes.enrollment import enrollment_bp
from routes.grades import grades_bp
from routes.attendance import attendance_bp
from routes.reports import reports_bp

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

jwt = JWTManager(app)
init_db(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(students_bp, url_prefix="/students")
app.register_blueprint(courses_bp, url_prefix="/courses")
app.register_blueprint(departments_bp, url_prefix="/departments")
app.register_blueprint(instructors_bp, url_prefix="/instructors")
app.register_blueprint(enrollment_bp, url_prefix="/enrollment")
app.register_blueprint(grades_bp, url_prefix="/grades")
app.register_blueprint(attendance_bp, url_prefix="/attendance")
app.register_blueprint(reports_bp, url_prefix="/reports")

if __name__ == "__main__":
    app.run(debug=True)
