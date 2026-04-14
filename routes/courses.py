from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import get_db

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("", methods=["GET"])
@jwt_required()
def get_courses():
    """List all courses. Optional filter: ?department_id=1"""
    department_id = request.args.get("department_id")
    conn = get_db()
    cur = conn.cursor()
    if department_id:
        cur.execute(
            """
            SELECT c.*, d.name AS department_name
            FROM courses c LEFT JOIN departments d ON c.department_id = d.department_id
            WHERE c.department_id = %s
            """,
            (department_id,),
        )
    else:
        cur.execute(
            """
            SELECT c.*, d.name AS department_name
            FROM courses c LEFT JOIN departments d ON c.department_id = d.department_id
            """
        )
    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200


@courses_bp.route("/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course(course_id):
    """Get a single course with its instructors."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.*, d.name AS department_name
        FROM courses c LEFT JOIN departments d ON c.department_id = d.department_id
        WHERE c.course_id = %s
        """,
        (course_id,),
    )
    course = cur.fetchone()
    if not course:
        cur.close()
        return jsonify({"error": "Course not found"}), 404

    cur.execute(
        """
        SELECT i.instructor_id, i.first_name, i.last_name, i.email
        FROM course_instructors ci
        JOIN instructors i ON ci.instructor_id = i.instructor_id
        WHERE ci.course_id = %s
        """,
        (course_id,),
    )
    course["instructors"] = cur.fetchall()
    cur.close()
    return jsonify(course), 200


@courses_bp.route("", methods=["POST"])
@jwt_required()
def add_course():
    """
    Add a new course.
    Body: { course_name, course_code, credits, department_id }
    """
    data = request.get_json()
    if not data.get("course_name") or not data.get("course_code"):
        return jsonify({"error": "course_name and course_code are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO courses (course_name, course_code, credits, department_id) VALUES (%s, %s, %s, %s)",
            (data["course_name"], data["course_code"], data.get("credits"), data.get("department_id")),
        )
        conn.commit()
        return jsonify({"message": "Course added", "course_id": cur.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Course code already exists"}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@courses_bp.route("/<int:course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):
    data = request.get_json()
    allowed = ["course_name", "course_code", "credits", "department_id"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    set_clause = ", ".join(f"{k} = %s" for k in updates)
    values = list(updates.values()) + [course_id]

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(f"UPDATE courses SET {set_clause} WHERE course_id = %s", values)
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Course not found"}), 404
        return jsonify({"message": "Course updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@courses_bp.route("/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Course not found"}), 404
        return jsonify({"message": "Course deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@courses_bp.route("/<int:course_id>/stats", methods=["GET"])
@jwt_required()
def course_stats(course_id):
    """Average marks, pass rate, and enrollment count for a course."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            COUNT(DISTINCT e.student_id) AS enrolled_students,
            ROUND(AVG(g.marks), 2) AS average_marks,
            MAX(g.marks) AS highest_marks,
            MIN(g.marks) AS lowest_marks,
            ROUND(SUM(g.marks >= 40) * 100.0 / COUNT(*), 2) AS pass_rate_pct
        FROM enrollment e
        LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
        WHERE e.course_id = %s
        """,
        (course_id,),
    )
    stats = cur.fetchone()
    cur.close()
    return jsonify(stats), 200
