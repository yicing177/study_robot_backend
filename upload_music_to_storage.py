from firebase_config import db, bucket
from firebase_admin import credentials, storage, firestore
import os
db = firestore.client()
bucket = storage.bucket()

music_folder = ('C:/Users/Chiu ling/Desktop/12projectback/study_robot_backend/music')
files = os.listdir(music_folder)

for file_name in files:

    if not file_name.endswith(".mp3"):
        continue

    title = file_name.replace(".mp3","")
    file_path = os.path.join(music_folder, file_name) 

    blob = bucket.blob(f"musics/{file_name}")
    blob.upload_from_filename(file_path)
    blob.make_public()
    url = blob.public_url

    db.collection("musics").add({
        "user_id" : "system",
        "title" : title,
        "url" : url
    })

    print(f"✅ 已上傳並儲存：{title}")