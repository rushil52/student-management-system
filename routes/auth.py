from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new admin/staff user.
    Body: { username, password, role }
    """
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "staff")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    hashed = generate_password_hash(password)
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hashed, role),
        )
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Username already exists"}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login and receive a JWT access token.
    Body: { username, password }
    """
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        identity=str(user["user_id"]),
        additional_claims={"role": user["role"], "username": user["username"]},
    )
    return jsonify({"access_token": token, "role": user["role"]}), 200
