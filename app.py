from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore
from flask_cors import CORS
from dotenv import load_dotenv
from firebase_config import initialize_firebase

import os

load_dotenv()
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
initialize_firebase()

app = Flask(__name__)
db = firestore.client()
CORS(app)

# ✅ 匯入你所有的 blueprint
from routes.auth_routes import auth_bp
from routes.material_routes import material_bp

# ✅ 註冊 blueprint 
app.register_blueprint(auth_bp)
app.register_blueprint(material_bp)  # ← 加上這行！

@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "Hello from Flask!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

print("\n=== 所有已註冊的路由 ===")
for rule in app.url_map.iter_rules():
    print(rule)
