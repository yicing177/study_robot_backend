from flask import Blueprint,request, jsonify
from firebase_admin import auth 
from firebase_config import db  # 從 firebase_config 匯入 Firestore
from services.auth_service import register_user, login_user

# 建立 Blueprint 實例
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    print("接收到的資料：", data)  # 打印請求的資料
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error":"不能為空"}), 400
        
    try:
        user_id = register_user(email, password)
        return jsonify({"message": "註冊成功", "user_id": user_id}), 201
    except ValueError as e:
        print("真實錯誤", e)
        print("真實錯誤", type(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("真實錯誤", e)
        print("真實錯誤", type(e))
        return jsonify({'message':'伺服器錯誤'}) ,500

    
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "請提供 email 和 password"}), 400
    
    # 檢查是否已經註冊
    try:
        existing_user = login_user(email, password)
        return {
            "uid" : existing_user["uid"],
            "idToken" : existing_user["idToken"],
            "email" : email
        }
    except Exception as e:
        return jsonify({"error":"回傳錯誤"}), 400



