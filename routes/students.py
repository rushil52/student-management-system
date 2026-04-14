from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import get_db

students_bp = Blueprint("students", __name__)


def _student_fields(data):
    return (
        data.get("first_name"),
        data.get("last_name"),
        data.get("email"),
        data.get("phone"),
        data.get("date_of_birth"),   # expected: YYYY-MM-DD
        data.get("gender"),
        data.get("address"),
        data.get("enrollment_year"),
        data.get("department_id"),
    )


@students_bp.route("", methods=["GET"])
@jwt_required()
def get_students():
    """List all students with optional filters: ?department_id=1&year=2023"""
    department_id = request.args.get("department_id")
    year = request.args.get("enrollment_year")

    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT s.*, d.name AS department_name
        FROM students s
        LEFT JOIN departments d ON s.department_id = d.department_id
        WHERE 1=1
    """
    params = []
    if department_id:
        query += " AND s.department_id = %s"
        params.append(department_id)
    if year:
        query += " AND s.enrollment_year = %s"
        params.append(year)

    cur.execute(query, params)
    students = cur.fetchall()
    cur.close()
    return jsonify(students), 200


@students_bp.route("/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):
    """Get a single student by ID."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.*, d.name AS department_name
        FROM students s
        LEFT JOIN departments d ON s.department_id = d.department_id
        WHERE s.student_id = %s
        """,
        (student_id,),
    )
    student = cur.fetchone()
    cur.close()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student), 200


@students_bp.route("", methods=["POST"])
@jwt_required()
def add_student():
    """
    Add a new student.
    Body: { first_name, last_name, email, phone, date_of_birth, gender, address, enrollment_year, department_id }
    """
    data = request.get_json()
    fields = _student_fields(data)

    if not fields[0] or not fields[1] or not fields[2]:
        return jsonify({"error": "first_name, last_name, and email are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO students
                (first_name, last_name, email, phone, date_of_birth, gender, address, enrollment_year, department_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            fields,
        )
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"message": "Student added", "student_id": new_id}), 201
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@students_bp.route("/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):
    """
    Update student details.
    Body: any subset of student fields.
    """
    data = request.get_json()
    allowed = [
        "first_name", "last_name", "email", "phone",
        "date_of_birth", "gender", "address", "enrollment_year", "department_id",
    ]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    set_clause = ", ".join(f"{k} = %s" for k in updates)
    values = list(updates.values()) + [student_id]

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            f"UPDATE students SET {set_clause} WHERE student_id = %s", values
        )
        conn.commit()
        # Log the update
        cur.execute(
            "INSERT INTO student_updates_log (student_id, updated_at) VALUES (%s, NOW())",
            (student_id,),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
        return jsonify({"message": "Student updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@students_bp.route("/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    """Delete a student by ID."""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
        return jsonify({"message": "Student deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@students_bp.route("/<int:student_id>/enrollments", methods=["GET"])
@jwt_required()
def student_enrollments(student_id):
    """Get all course enrollments for a student."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT e.enrollment_id, e.semester, e.year,
               c.course_id, c.course_name, c.course_code, c.credits
        FROM enrollment e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = %s
        ORDER BY e.year DESC, e.semester
        """,
        (student_id,),
    )
    enrollments = cur.fetchall()
    cur.close()
    return jsonify(enrollments), 200


@students_bp.route("/<int:student_id>/grades", methods=["GET"])
@jwt_required()
def student_grades(student_id):
    """Get all grades for a student."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT g.grade_id, g.marks, g.grade, g.updated_at,
               c.course_name, c.course_code,
               e.semester, e.year
        FROM grades g
        JOIN enrollment e ON g.enrollment_id = e.enrollment_id
        JOIN courses c ON g.course_id = c.course_id
        WHERE e.student_id = %s
        ORDER BY e.year DESC, e.semester
        """,
        (student_id,),
    )
    grades = cur.fetchall()
    cur.close()
    return jsonify(grades), 200


@students_bp.route("/<int:student_id>/attendance", methods=["GET"])
@jwt_required()
def student_attendance(student_id):
    """Get attendance summary for a student."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.course_name, c.course_code,
               COUNT(*) AS total_classes,
               SUM(a.status = 'present') AS present,
               SUM(a.status = 'absent') AS absent,
               ROUND(SUM(a.status = 'present') * 100.0 / COUNT(*), 2) AS attendance_pct
        FROM attendance a
        JOIN enrollment e ON a.enrollment_id = e.enrollment_id
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = %s
        GROUP BY c.course_id
        """,
        (student_id,),
    )
    summary = cur.fetchall()
    cur.close()
    return jsonify(summary), 200
