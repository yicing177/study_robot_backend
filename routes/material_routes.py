from flask import Blueprint, request, jsonify,g
from services.material_service import upload_material, get_material, get_all_materials
from routes.auth_routes import login_required
material_bp = Blueprint("material", __name__)

@material_bp.route("/upload_material", methods=["POST"])
@login_required
def upload_pdf():
    user_id=g.user_id 

    title = request.form.get("title")
    file = request.files["file"]
    file_type = file.content_type
    
    material = upload_material(user_id, file.stream, title, file.filename,file_type)
    return jsonify({"message": "上傳成功", "material": material.to_dict()})

@material_bp.route("/get_material", methods = ["GET"])
@login_required
def get_material_route():
    user_id = g.user_id
    material_id = request.args.get("material_id")
    try:
        material = get_material(material_id, user_id)
        if material:
            return jsonify(material.to_dict()), 200
        else:
            return jsonify({"error":"找不到資料"}), 404 
    except PermissionError as e:
        return jsonify({"error":str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@material_bp.route("/get_all_materials", methods=["GET"])
@login_required
def get_all_materials_route():
    user_id = g.user_id
    try:
        materials = get_all_materials(user_id)
        return jsonify([m.to_dict() for m in materials]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
