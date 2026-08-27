import logging
import time

from flask import Blueprint, current_app, jsonify, request

from .db import connection
from .services import ValidationError, validate_request, validate_resource

api = Blueprint("api", __name__)
logger = logging.getLogger(__name__)

request_count = 0


def row_to_dict(row):
    return dict(row) if row else None


@api.before_request
def start_timer():
    request.start_time = time.perf_counter()


@api.after_request
def record_request(response):
    global request_count
    request_count += 1
    elapsed_ms = (time.perf_counter() - request.start_time) * 1000
    logger.info(
        "method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@api.errorhandler(ValidationError)
def validation_error(error):
    return jsonify({"error": str(error)}), 400


@api.route("/health", methods=["GET"])
def health():
    try:
        with connection(current_app.config["DATABASE_PATH"]) as conn:
            conn.execute("SELECT 1")
        return jsonify({"status": "healthy", "database": "ok"})
    except Exception:
        logger.exception("health check failed")
        return jsonify({"status": "unhealthy", "database": "error"}), 503


@api.route("/ready", methods=["GET"])
def ready():
    response, status = health()
    if status == 503:
        return response, status
    return jsonify({"ready": True})


@api.route("/metrics", methods=["GET"])
def metrics():
    with connection(current_app.config["DATABASE_PATH"]) as conn:
        resources = conn.execute("SELECT COUNT(*) AS count FROM resources").fetchone()["count"]
        pending = conn.execute(
            "SELECT COUNT(*) AS count FROM requests WHERE status = 'pending'"
        ).fetchone()["count"]

    return jsonify({
        "http_requests_total": request_count,
        "resources_total": resources,
        "pending_requests": pending,
    })


@api.route("/api/resources", methods=["GET"])
def list_resources():
    with connection(current_app.config["DATABASE_PATH"]) as conn:
        rows = conn.execute(
            "SELECT * FROM resources ORDER BY created_at DESC"
        ).fetchall()

    return jsonify([row_to_dict(row) for row in rows])


@api.route("/api/resources/<int:resource_id>", methods=["GET"])
def get_resource(resource_id):
    with connection(current_app.config["DATABASE_PATH"]) as conn:
        row = conn.execute(
            "SELECT * FROM resources WHERE id = ?",
            (resource_id,),
        ).fetchone()

    if row is None:
        return jsonify({"error": "resource not found"}), 404

    return jsonify(row_to_dict(row))


@api.route("/api/resources", methods=["POST"])
def create_resource():
    name, category, quantity = validate_resource(request.get_json(silent=True))

    with connection(current_app.config["DATABASE_PATH"]) as conn:
        cursor = conn.execute(
            """
            INSERT INTO resources (name, category, quantity)
            VALUES (?, ?, ?)
            """,
            (name, category, quantity),
        )
        resource_id = cursor.lastrowid

        row = conn.execute(
            "SELECT * FROM resources WHERE id = ?",
            (resource_id,),
        ).fetchone()

    logger.info("resource_created id=%s name=%s", resource_id, name)
    return jsonify(row_to_dict(row)), 201


@api.route("/api/resources/<int:resource_id>", methods=["PATCH"])
def update_resource(resource_id):
    payload = request.get_json(silent=True)
    name, category, quantity = validate_resource(payload)

    with connection(current_app.config["DATABASE_PATH"]) as conn:
        existing = conn.execute(
            "SELECT id FROM resources WHERE id = ?",
            (resource_id,),
        ).fetchone()

        if existing is None:
            return jsonify({"error": "resource not found"}), 404

        conn.execute(
            """
            UPDATE resources
            SET name = ?, category = ?, quantity = ?
            WHERE id = ?
            """,
            (name, category, quantity, resource_id),
        )

        row = conn.execute(
            "SELECT * FROM resources WHERE id = ?",
            (resource_id,),
        ).fetchone()

    return jsonify(row_to_dict(row))


@api.route("/api/resources/<int:resource_id>", methods=["DELETE"])
def delete_resource(resource_id):
    with connection(current_app.config["DATABASE_PATH"]) as conn:
        existing = conn.execute(
            "SELECT id FROM resources WHERE id = ?",
            (resource_id,),
        ).fetchone()

        if existing is None:
            return jsonify({"error": "resource not found"}), 404

        conn.execute(
            "DELETE FROM resources WHERE id = ?",
            (resource_id,),
        )

    return "", 204


@api.route("/api/requests", methods=["POST"])
def create_request():
    resource_id, requester, quantity = validate_request(
        request.get_json(silent=True)
    )

    with connection(current_app.config["DATABASE_PATH"]) as conn:
        resource = conn.execute(
            "SELECT * FROM resources WHERE id = ?",
            (resource_id,),
        ).fetchone()

        if resource is None:
            return jsonify({"error": "resource not found"}), 404

        if resource["quantity"] < quantity:
            return jsonify({
                "error": "insufficient resource quantity",
                "available": resource["quantity"],
                "requested": quantity,
            }), 409

        conn.execute(
            """
            UPDATE resources
            SET quantity = quantity - ?
            WHERE id = ?
            """,
            (quantity, resource_id),
        )

        cursor = conn.execute(
            """
            INSERT INTO requests (resource_id, requester, quantity)
            VALUES (?, ?, ?)
            """,
            (resource_id, requester, quantity),
        )

        row = conn.execute(
            "SELECT * FROM requests WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    logger.info(
        "resource_requested request_id=%s resource_id=%s quantity=%s",
        row["id"],
        resource_id,
        quantity,
    )
    return jsonify(row_to_dict(row)), 201


@api.route("/api/requests", methods=["GET"])
def list_requests():
    with connection(current_app.config["DATABASE_PATH"]) as conn:
        rows = conn.execute(
            """
            SELECT requests.*, resources.name AS resource_name
            FROM requests
            JOIN resources ON resources.id = requests.resource_id
            ORDER BY requests.created_at DESC
            """
        ).fetchall()

    return jsonify([row_to_dict(row) for row in rows])
