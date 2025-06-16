import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
#可以優化成相對路徑之後弄
with open("C:/Users/Chiu ling/Desktop/12projectback/study_robot_backend/firebase/firebase_config_dict.json") as f:
    firebase_config_dict = json.load(f)


# Firebase 初始化函數
def initialize_firebase():
    if not firebase_admin._apps:  # 確保只初始化一次

        cred = credentials.Certificate('C:/Users/Chiu ling/Desktop/12projectback/study_robot_backend/firebase/serviceAccountKey.json')
        firebase_admin.initialize_app(cred,{'storageBucket': 'project-771d3.appspot.com'})


# 確保 Firebase 已初始化
initialize_firebase()
firebase = pyrebase.initialize_app(firebase_config_dict)
# 取得 Firestore 客戶端
db = firestore.client()
bucket = storage.bucket()
auth = firebase.auth()

