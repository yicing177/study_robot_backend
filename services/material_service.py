from firebase_config import db, bucket
from datetime import datetime, timedelta
import uuid
from models.material import Material
def upload_material(user_id,file_stream,title,filename,file_type):
    file_stream.seek(0)
    material_id=str(uuid.uuid4())
    blob = bucket.blob(f"materials/{user_id}/{material_id}_{filename}")
    blob.upload_from_file(file_stream, content_type='file_type')
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
