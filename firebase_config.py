import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 初始化函數
def initialize_firebase():
    if not firebase_admin._apps:  # 確保只初始化一次
        cred = credentials.Certificate('C:/Users/aries/OneDrive/桌面/yyx_backend/study_robot_backend/firebase/serviceAccountKey.json')
        firebase_admin.initialize_app(cred)

# 確保 Firebase 已初始化
initialize_firebase()

# 取得 Firestore 客戶端
db = firestore.client()