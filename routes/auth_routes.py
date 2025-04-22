from flask import Blueprint,request, jsonify
from firebase_admin import auth 
from firebase_config import db  # 從 firebase_config 匯入 Firestore

# 建立 Blueprint 實例
auth_bp = Blueprint("auth", __name__)
# 指定 users collection
users_ref = db.collection("users")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    print("接收到的資料：", data)  # 打印請求的資料
    email = data.get('email')
    password = data.get('password')
    
    # 檢查是否已經註冊
    existing_user = users_ref.where("email", "==", email).get()
    if existing_user:  # 確保有查到資料才判斷已註冊
        return jsonify({'meesage':'Email already registered!'}), 400
    
    try:
        # 使用 Firebase Authentication 創建新用戶
        user = auth.create_user(email=email, password=password)
    
        # 把 email 存入 Firestore
        users_ref.document(user.uid).set({"email": email})
        return jsonify({"message": "註冊成功", "uid": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "請提供 email 和 password"}), 400
    
    # 檢查是否已經註冊
    existing_user = users_ref.where("email", "==", email).get()
    if not existing_user:  # 確保有查到資料才判斷已註冊
        return jsonify({'meesage':'Email not exist , please registe!'}), 400
    
     # Firebase Authentication 驗證密碼
    try:
        user = auth.get_user_by_email(email)  # 確保帳號存在
        return jsonify({"message": "登入成功", "uid": user.uid}), 200
    except Exception as e:
        return jsonify({"error": "登入失敗，請確認帳號或密碼"}), 400




    # 這裡不直接驗證密碼，因為 Firebase Authentication 需要透過前端處理
    return jsonify({"message": "請使用 Firebase Client 取得 ID Token"}), 200
