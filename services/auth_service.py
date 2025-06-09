from firebase_config import db 
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
import pyrebase
from firebase_config import firebase_config_dict  # 你的 Firebase 設定 dict

firebase = pyrebase.initialize_app(firebase_config_dict)
auth = firebase.auth()
def register_user(email: str,password: str):

    existing_user = db.collection("users").where("email", "==", email).get()# 檢查是否已經註冊
    if existing_user:  # 確保有查到資料才判斷已註冊
        raise ValueError("email 被註冊過了")
    if len(password) < 8:
        raise ValueError("太短了")
    try:
        # 1) 在 Firebase Authentication 中创建账号
        fb_user = firebase_auth.create_user(email=email,password=password)
    except firebase_exceptions.AlreadyExistsError:      
        raise ValueError("Email 已經被註冊")# 如果邮箱已经存在
    except Exception as e:
        raise RuntimeError(f"Auth 服务异常：{e}")# 其它 Auth 层面的错误

    # 2) （可选）将用户信息写入 Firestore
    user = User(user_id=fb_user.uid,email=email,)
    db.collection("users").document(fb_user.uid).set(user.to_dict())
    return fb_user.uid
def login_user(email: str, password: str):
 
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return {
            "uid" : user["localId"] ,
            "email" : email, 
            "id_token" : user["idToken"]
        }
    except Exception as e:
        print("登入錯誤", e)
        raise ValueError("帳號密碼錯誤")

def verify_id_token(id_token):
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return {
            "email" : decoded_token.get("email" ,""),
            "uid": decoded_token["uid"]
        }
    except Exception as e:
        raise ValueError("token 過期") 





