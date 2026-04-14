from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import get_db

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("", methods=["POST"])
@jwt_required()
def mark_attendance():
    """
    Mark attendance for one or multiple students.
    Body: { records: [{ enrollment_id, date, status }] }
    OR single: { enrollment_id, date, status }
    """
    data = request.get_json()
    records = data.get("records")

    if not records:
        # Single record fallback
        enrollment_id = data.get("enrollment_id")
        date = data.get("date")
        status = data.get("status", "present")
        if not enrollment_id or not date:
            return jsonify({"error": "enrollment_id and date are required"}), 400
        records = [{"enrollment_id": enrollment_id, "date": date, "status": status}]

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.executemany(
            "INSERT INTO attendance (enrollment_id, date, status) VALUES (%s, %s, %s)",
            [(r["enrollment_id"], r["date"], r.get("status", "present")) for r in records],
        )
        conn.commit()
        return jsonify({"message": f"{len(records)} attendance record(s) marked"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@attendance_bp.route("/<int:attendance_id>", methods=["PUT"])
@jwt_required()
def update_attendance(attendance_id):
    """Update attendance status. Body: { status }"""
    data = request.get_json()
    status = data.get("status")
    if not status:
        return jsonify({"error": "status is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE attendance SET status = %s WHERE attendance_id = %s",
            (status, attendance_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Attendance record not found"}), 404
        return jsonify({"message": "Attendance updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@attendance_bp.route("", methods=["GET"])
@jwt_required()
def get_attendance():
    """
    Get attendance records.
    Filters: ?enrollment_id=1&date=2024-01-15&status=absent
    """
    enrollment_id = request.args.get("enrollment_id")
    date = request.args.get("date")
    status = request.args.get("status")

    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT a.*, s.first_name, s.last_name, c.course_name
        FROM attendance a
        JOIN enrollment e ON a.enrollment_id = e.enrollment_id
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
        WHERE 1=1
    """
    params = []
    if enrollment_id:
        query += " AND a.enrollment_id = %s"
        params.append(enrollment_id)
    if date:
        query += " AND a.date = %s"
        params.append(date)
    if status:
        query += " AND a.status = %s"
        params.append(status)

    cur.execute(query, params)
    records = cur.fetchall()
    cur.close()
    return jsonify(records), 200
