import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Firebase 初始化函數
def initialize_firebase():
    if not firebase_admin._apps:  # 確保只初始化一次

        cred = credentials.Certificate('C:/Users/Chiu ling/Desktop/12projectback/study_robot_backend/firebase/serviceAccountKey.json')
        firebase_admin.initialize_app(cred,{'storageBucket':'project-771d3.firebasestorage.app'})

firebase_config_dict = {
    "apiKey": "AIzaSyCGjCb6y-3_gvAGPJVDVmDM4EmZ226VuNA",
    "authDomain": "project-771d3.firebaseapp.com",
    "databaseURL": "https://project-771d3-default-rtdb.firebaseio.com",
    "projectId": "project-771d3",
    "storageBucket": "project-771d3.appspot.com",
    "messagingSenderId": "745736050770",
    "appId": "1:745736050770:web:7b926b93375c6e59f2678b",
    "measurementId": "G-5PPK6CZFSC"
}


# 確保 Firebase 已初始化
initialize_firebase()
firebase = pyrebase.initialize_app(firebase_config_dict)
# 取得 Firestore 客戶端
db = firestore.client()
bucket = storage.bucket()
auth = firebase.auth()

