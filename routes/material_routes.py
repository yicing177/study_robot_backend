from flask import Blueprint, request, jsonify
from services.material_service import upload_material

material_bp = Blueprint("material", __name__)

@material_bp.route("/upload_material", methods=["POST"])
def upload_pdf():
    user_id = request.form.get("user_id")
    title = request.form.get("title")
    file = request.files["file"]
    file_type = file.content_type
    
    material = upload_material(user_id, file.stream, title, file.filename,file_type)
    return jsonify({"message": "上傳成功", "material": material.to_dict()})