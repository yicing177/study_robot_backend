from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore
from flask_cors import CORS
from dotenv import load_dotenv
from firebase_config import initialize_firebase
from routes.auth import register, login  # 匯入 auth.py 中的函數
from routes.voice import voice_bp
import os


# 載入 .env 檔案
load_dotenv()

# 從 .env 文件中讀取 Firebase 金鑰路徑
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')

# 初始化 Firebase
initialize_firebase()

# 創建 Flask 應用
app = Flask(__name__)
app.register_blueprint(voice_bp,url_prefix='/routes')

# 使用 Firestore 客戶端
db = firestore.client()


CORS(app)  # 允許前端請求

# 註冊路由
@app.route('/register', methods=['POST'])
def register_route():
    print("收到請求:", request.json)
    return register()  # 調用 auth.py 中的 register 函數

@app.route('/login', methods=['POST'])
def login_route():
    return login()  # 調用 auth.py 中的 login 函數


@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "Hello from Flask!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)



