from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import get_db

instructors_bp = Blueprint("instructors", __name__)


@instructors_bp.route("", methods=["GET"])
@jwt_required()
def get_instructors():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT i.*, d.name AS department_name
        FROM instructors i LEFT JOIN departments d ON i.department_id = d.department_id
        """
    )
    instructors = cur.fetchall()
    cur.close()
    return jsonify(instructors), 200


@instructors_bp.route("/<int:instructor_id>", methods=["GET"])
@jwt_required()
def get_instructor(instructor_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT i.*, d.name AS department_name
        FROM instructors i LEFT JOIN departments d ON i.department_id = d.department_id
        WHERE i.instructor_id = %s
        """,
        (instructor_id,),
    )
    instructor = cur.fetchone()
    if not instructor:
        cur.close()
        return jsonify({"error": "Instructor not found"}), 404

    # Fetch assigned courses
    cur.execute(
        """
        SELECT c.course_id, c.course_name, c.course_code
        FROM course_instructors ci
        JOIN courses c ON ci.course_id = c.course_id
        WHERE ci.instructor_id = %s
        """,
        (instructor_id,),
    )
    instructor["courses"] = cur.fetchall()
    cur.close()
    return jsonify(instructor), 200


@instructors_bp.route("", methods=["POST"])
@jwt_required()
def add_instructor():
    """Body: { first_name, last_name, email, phone, department_id }"""
    data = request.get_json()
    if not data.get("first_name") or not data.get("email"):
        return jsonify({"error": "first_name and email are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO instructors (first_name, last_name, email, phone, department_id) VALUES (%s, %s, %s, %s, %s)",
            (data["first_name"], data.get("last_name"), data["email"], data.get("phone"), data.get("department_id")),
        )
        conn.commit()
        return jsonify({"message": "Instructor added", "instructor_id": cur.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@instructors_bp.route("/<int:instructor_id>", methods=["PUT"])
@jwt_required()
def update_instructor(instructor_id):
    data = request.get_json()
    allowed = ["first_name", "last_name", "email", "phone", "department_id"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    set_clause = ", ".join(f"{k} = %s" for k in updates)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            f"UPDATE instructors SET {set_clause} WHERE instructor_id = %s",
            list(updates.values()) + [instructor_id],
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Instructor not found"}), 404
        return jsonify({"message": "Instructor updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@instructors_bp.route("/<int:instructor_id>", methods=["DELETE"])
@jwt_required()
def delete_instructor(instructor_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM instructors WHERE instructor_id = %s", (instructor_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Instructor not found"}), 404
        return jsonify({"message": "Instructor deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@instructors_bp.route("/<int:instructor_id>/assign-course", methods=["POST"])
@jwt_required()
def assign_course(instructor_id):
    """Assign an instructor to a course. Body: { course_id }"""
    data = request.get_json()
    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"error": "course_id is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO course_instructors (course_id, instructor_id) VALUES (%s, %s)",
            (course_id, instructor_id),
        )
        conn.commit()
        return jsonify({"message": "Instructor assigned to course"}), 201
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Already assigned"}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
