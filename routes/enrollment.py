from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import get_db

enrollment_bp = Blueprint("enrollment", __name__)


@enrollment_bp.route("", methods=["POST"])
@jwt_required()
def enroll_student():
    """
    Enroll a student in a course.
    Body: { student_id, course_id, semester, year }
    """
    data = request.get_json()
    student_id = data.get("student_id")
    course_id = data.get("course_id")
    semester = data.get("semester")
    year = data.get("year")

    if not all([student_id, course_id, semester, year]):
        return jsonify({"error": "student_id, course_id, semester, and year are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO enrollment (student_id, course_id, semester, year) VALUES (%s, %s, %s, %s)",
            (student_id, course_id, semester, year),
        )
        conn.commit()
        return jsonify({"message": "Student enrolled", "enrollment_id": cur.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@enrollment_bp.route("/<int:enrollment_id>", methods=["DELETE"])
@jwt_required()
def drop_enrollment(enrollment_id):
    """Drop/remove an enrollment."""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM enrollment WHERE enrollment_id = %s", (enrollment_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Enrollment not found"}), 404
        return jsonify({"message": "Enrollment removed"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@enrollment_bp.route("", methods=["GET"])
@jwt_required()
def list_enrollments():
    """
    List enrollments with optional filters:
    ?course_id=1&semester=Fall&year=2024
    """
    course_id = request.args.get("course_id")
    semester = request.args.get("semester")
    year = request.args.get("year")

    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT e.*, s.first_name, s.last_name, s.email,
               c.course_name, c.course_code
        FROM enrollment e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
        WHERE 1=1
    """
    params = []
    if course_id:
        query += " AND e.course_id = %s"
        params.append(course_id)
    if semester:
        query += " AND e.semester = %s"
        params.append(semester)
    if year:
        query += " AND e.year = %s"
        params.append(year)

    cur.execute(query, params)
    enrollments = cur.fetchall()
    cur.close()
    return jsonify(enrollments), 200
