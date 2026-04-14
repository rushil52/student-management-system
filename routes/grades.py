from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import get_db

grades_bp = Blueprint("grades", __name__)


@grades_bp.route("", methods=["POST"])
@jwt_required()
def add_grade():
    """
    Add or update a grade.
    Body: { enrollment_id, course_id, marks, grade }
    """
    data = request.get_json()
    enrollment_id = data.get("enrollment_id")
    course_id = data.get("course_id")
    marks = data.get("marks")
    grade = data.get("grade")

    if not all([enrollment_id, course_id, marks is not None]):
        return jsonify({"error": "enrollment_id, course_id, and marks are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        # Upsert: update if exists, insert if not
        cur.execute(
            """
            INSERT INTO grades (enrollment_id, course_id, marks, grade, updated_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE marks = VALUES(marks), grade = VALUES(grade), updated_at = NOW()
            """,
            (enrollment_id, course_id, marks, grade),
        )
        conn.commit()
        return jsonify({"message": "Grade saved", "grade_id": cur.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@grades_bp.route("/<int:grade_id>", methods=["PUT"])
@jwt_required()
def update_grade(grade_id):
    """Update marks and/or grade for an existing grade record."""
    data = request.get_json()
    allowed = ["marks", "grade"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    updates["updated_at"] = "NOW()"
    set_parts = []
    values = []
    for k, v in updates.items():
        if v == "NOW()":
            set_parts.append(f"{k} = NOW()")
        else:
            set_parts.append(f"{k} = %s")
            values.append(v)
    values.append(grade_id)

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            f"UPDATE grades SET {', '.join(set_parts)} WHERE grade_id = %s", values
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Grade record not found"}), 404
        return jsonify({"message": "Grade updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@grades_bp.route("", methods=["GET"])
@jwt_required()
def get_grades():
    """
    Fetch grades with filters: ?course_id=1&semester=Fall&year=2024
    """
    course_id = request.args.get("course_id")
    semester = request.args.get("semester")
    year = request.args.get("year")

    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT g.*, s.first_name, s.last_name, c.course_name, e.semester, e.year
        FROM grades g
        JOIN enrollment e ON g.enrollment_id = e.enrollment_id
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON g.course_id = c.course_id
        WHERE 1=1
    """
    params = []
    if course_id:
        query += " AND g.course_id = %s"
        params.append(course_id)
    if semester:
        query += " AND e.semester = %s"
        params.append(semester)
    if year:
        query += " AND e.year = %s"
        params.append(year)

    cur.execute(query, params)
    grades = cur.fetchall()
    cur.close()
    return jsonify(grades), 200
