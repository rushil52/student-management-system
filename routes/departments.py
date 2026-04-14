from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import get_db

departments_bp = Blueprint("departments", __name__)


@departments_bp.route("", methods=["GET"])
@jwt_required()
def get_departments():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM departments")
    depts = cur.fetchall()
    cur.close()
    return jsonify(depts), 200


@departments_bp.route("/<int:dept_id>", methods=["GET"])
@jwt_required()
def get_department(dept_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM departments WHERE department_id = %s", (dept_id,))
    dept = cur.fetchone()
    if not dept:
        cur.close()
        return jsonify({"error": "Department not found"}), 404
    cur.close()
    return jsonify(dept), 200


@departments_bp.route("", methods=["POST"])
@jwt_required()
def add_department():
    """Body: { name, head_of_department }"""
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO departments (name, head_of_department) VALUES (%s, %s)",
            (data["name"], data.get("head_of_department")),
        )
        conn.commit()
        return jsonify({"message": "Department added", "department_id": cur.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@departments_bp.route("/<int:dept_id>", methods=["PUT"])
@jwt_required()
def update_department(dept_id):
    data = request.get_json()
    allowed = ["name", "head_of_department"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    set_clause = ", ".join(f"{k} = %s" for k in updates)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            f"UPDATE departments SET {set_clause} WHERE department_id = %s",
            list(updates.values()) + [dept_id],
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Department not found"}), 404
        return jsonify({"message": "Department updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@departments_bp.route("/<int:dept_id>/students", methods=["GET"])
@jwt_required()
def department_students(dept_id):
    """List all students in a department."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT student_id, first_name, last_name, email, enrollment_year FROM students WHERE department_id = %s",
        (dept_id,),
    )
    students = cur.fetchall()
    cur.close()
    return jsonify(students), 200


@departments_bp.route("/<int:dept_id>/courses", methods=["GET"])
@jwt_required()
def department_courses(dept_id):
    """List all courses in a department."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM courses WHERE department_id = %s", (dept_id,)
    )
    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200
