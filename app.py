from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore
from flask_cors import CORS
from dotenv import load_dotenv
from firebase_config import initialize_firebase

import os


# 載入 .env 檔案
load_dotenv()

# 從 .env 文件中讀取 Firebase 金鑰路徑
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')

# 初始化 Firebase
initialize_firebase()

# 創建 Flask 應用
app = Flask(__name__)

# 使用 Firestore 客戶端
db = firestore.client()


CORS(app)  # 允許前端請求


from routes.auth_routes import auth_bp
app.register_blueprint(auth_bp)
# 註冊 Blueprint
app.register_blueprint(auth_bp)


@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "Hello from Flask!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)



