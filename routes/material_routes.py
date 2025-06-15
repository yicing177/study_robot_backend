from flask import Blueprint, request, jsonify,g
from services.material_service import upload_material
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