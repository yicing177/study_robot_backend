from firebase_config import db, bucket
from datetime import datetime, timedelta
import uuid
from models.material import Material
def upload_material(user_id,file_stream,title,filename,):
    material_id=str(uuid.uuid4())
    blob = bucket.blob(f"materials/{user_id}/{material_id}_{filename}")
    blob.upload_from_file(file_stream, content_type='application/pdf')
    file_url = blob.generate_signed_url(expiration=datetime.utcnow() + timedelta(days=365))

    material=Material(
        material_id=material_id,
        user_id=user_id,
        file_url=file_url,
        title=title,
        upload_time=datetime.now()
    )
    
    db.collection("materials").document(material_id).set(material.to_dict())
    return material
