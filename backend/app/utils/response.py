from flask import jsonify


def success(data, message="success"):
    return jsonify({"data": data, "message": message})


def error(code, message, status_code=400):
    response = jsonify({"error": {"code": code, "message": message}})
    response.status_code = status_code
    return response
