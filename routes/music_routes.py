from flask import Blueprint, jsonify
from models.music import Music
from firebase_admin import firestore

music_bp = Blueprint("music",__name__ )
db = firestore.client()

@music_bp.routes("/music" , methods=["GET"])
def get_music(title):
    try:
    
        docs = db.collection("music").where("title" ,"==", title).get()#collection 包
        if not docs:
            return jsonify({"error" : "找不到音樂" }), 404

        music = Music.from_dict(docs[0].to_dict)#先把它變成字典在轉成Music物件
        return jsonify(music.to_dict()), 200  #傳送給前端再轉成字典
    except Exception as e:
        return({"error" : str(e)}), 400

