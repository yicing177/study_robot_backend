from firebase_config import db, bucket
from datetime import datetime, timedelta
import uuid
from models.material import Material
def upload_material(user_id,file_stream,title,filename,file_type):
    file_stream.seek(0)
    material_id=str(uuid.uuid4())#生成唯一
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{now}_{filename}"
    blob = bucket.blob(f"materials/{user_id}/{material_id}_{safe_name}")
    blob.upload_from_file(file_stream, content_type=file_type)
    blob.make_public()
    file_url = blob.public_url

    material=Material(
        material_id=material_id,
        user_id=user_id,
        file_url=file_url,
        title=title,
        type=file_type,
        upload_time=datetime.now()
    )
    
    db.collection("materials").document(material_id).set(material.to_dict())
    return material

def get_material(material_id, user_id):
    doc=db.collection("materials").document( material_id).get()
    if doc.exists:
        data = doc.to_dict()
        if data.get("user_id") == user_id:
            return Material .from_dict(data)#單筆資料
        else:
            raise PermissionError ("你沒權拿這資料")
    else:
        return None 

def get_all_materials(user_id):
    docs = db.collection("materials").where("user_id", "==", user_id).get()
    return [Material.from_dict(doc.to_dict()) for doc in docs]
