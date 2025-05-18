from flask import Flask, request, jsonify, send_from_directory
from firebase_admin import credentials, firestore
from flask_cors import CORS
from dotenv import load_dotenv
from firebase_config import initialize_firebase
from routes.auth_routes import register, login  # 匯入 auth.py 中的函數 # 這段沒用到可以刪吧?
import os

load_dotenv()
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
initialize_firebase()

app = Flask(__name__)


# 使用 Firestore 客戶端

db = firestore.client()
CORS(app)

# ✅ 匯入你所有的 blueprint
from routes.auth_routes import auth_bp
from routes.material_routes import material_bp
from routes.voice import voice_bp
from routes.gpt import gpt_bp

# ✅ 註冊 blueprint 
app.register_blueprint(auth_bp)
app.register_blueprint(material_bp)  # ← 加上這行！
app.register_blueprint(voice_bp,url_prefix='/routes')
app.register_blueprint(gpt_bp)

@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "Hello from Flask!"})

# 找出目前這個 app.py 的資料夾路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/dir_tts_result/<path:filename>')
def serve_tts_file(filename):
    folder_path = os.path.join(BASE_DIR, 'dir_tts_result')
    return send_from_directory(folder_path, filename)

@app.route('/dir_stt_result/<path:filename>')
def serve_stt_file(filename):
    folder_path = os.path.join(BASE_DIR, 'dir_stt_result')
    return send_from_directory(folder_path, filename)

# 要寫在最後！！！！！
if __name__ == '__main__':
    app.run(debug=True, port=5000)

print("\n=== 所有已註冊的路由 ===")
for rule in app.url_map.iter_rules():
    print(rule)
