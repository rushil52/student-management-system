from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import get_db

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/students/<int:student_id>", methods=["GET"])
@jwt_required()
def student_full_report(student_id):
    """
    Full academic report for a student:
    profile + grades per course + attendance summary.
    """
    conn = get_db()
    cur = conn.cursor()

    # Profile
    cur.execute(
        """
        SELECT s.*, d.name AS department_name
        FROM students s LEFT JOIN departments d ON s.department_id = d.department_id
        WHERE s.student_id = %s
        """,
        (student_id,),
    )
    profile = cur.fetchone()
    if not profile:
        cur.close()
        return jsonify({"error": "Student not found"}), 404

    # Grades
    cur.execute(
        """
        SELECT c.course_name, c.course_code, e.semester, e.year,
               g.marks, g.grade
        FROM enrollment e
        JOIN courses c ON e.course_id = c.course_id
        LEFT JOIN grades g ON g.enrollment_id = e.enrollment_id
        WHERE e.student_id = %s
        ORDER BY e.year DESC, e.semester
        """,
        (student_id,),
    )
    grades = cur.fetchall()

    # Attendance summary
    cur.execute(
        """
        SELECT c.course_name, c.course_code,
               COUNT(*) AS total,
               SUM(a.status = 'present') AS present,
               ROUND(SUM(a.status = 'present') * 100.0 / COUNT(*), 2) AS attendance_pct
        FROM attendance a
        JOIN enrollment e ON a.enrollment_id = e.enrollment_id
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = %s
        GROUP BY c.course_id
        """,
        (student_id,),
    )
    attendance = cur.fetchall()

    # GPA-style average
    cur.execute(
        """
        SELECT ROUND(AVG(g.marks), 2) AS overall_average
        FROM grades g
        JOIN enrollment e ON g.enrollment_id = e.enrollment_id
        WHERE e.student_id = %s
        """,
        (student_id,),
    )
    avg = cur.fetchone()
    cur.close()

    return jsonify({
        "profile": profile,
        "grades": grades,
        "attendance_summary": attendance,
        "overall_average": avg["overall_average"] if avg else None,
    }), 200


@reports_bp.route("/departments/<int:dept_id>", methods=["GET"])
@jwt_required()
def department_report(dept_id):
    """
    Department summary: student count, course count, average marks.
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM departments WHERE department_id = %s", (dept_id,))
    dept = cur.fetchone()
    if not dept:
        cur.close()
        return jsonify({"error": "Department not found"}), 404

    cur.execute(
        "SELECT COUNT(*) AS student_count FROM students WHERE department_id = %s", (dept_id,)
    )
    dept["student_count"] = cur.fetchone()["student_count"]

    cur.execute(
        "SELECT COUNT(*) AS course_count FROM courses WHERE department_id = %s", (dept_id,)
    )
    dept["course_count"] = cur.fetchone()["course_count"]

    cur.execute(
        """
        SELECT ROUND(AVG(g.marks), 2) AS avg_marks
        FROM grades g
        JOIN enrollment e ON g.enrollment_id = e.enrollment_id
        JOIN students s ON e.student_id = s.student_id
        WHERE s.department_id = %s
        """,
        (dept_id,),
    )
    dept["average_marks"] = cur.fetchone()["avg_marks"]
    cur.close()

    return jsonify(dept), 200


@reports_bp.route("/top-students", methods=["GET"])
@jwt_required()
def top_students():
    """
    Top N students by average marks.
    Query params: ?limit=10&department_id=1
    """
    limit = int(request.args.get("limit", 10))
    dept_id = request.args.get("department_id")

    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT s.student_id, s.first_name, s.last_name, s.email,
               d.name AS department_name,
               ROUND(AVG(g.marks), 2) AS average_marks
        FROM students s
        JOIN enrollment e ON s.student_id = e.student_id
        JOIN grades g ON e.enrollment_id = g.enrollment_id
        LEFT JOIN departments d ON s.department_id = d.department_id
        WHERE 1=1
    """
    params = []
    if dept_id:
        query += " AND s.department_id = %s"
        params.append(dept_id)
    query += " GROUP BY s.student_id ORDER BY average_marks DESC LIMIT %s"
    params.append(limit)

    cur.execute(query, params)
    top = cur.fetchall()
    cur.close()
    return jsonify(top), 200
