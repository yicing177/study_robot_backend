from firebase_config import db 
import uuid
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
def register_user(email: str,password: str):
    
    try:
        # 1) 在 Firebase Authentication 中创建账号
        fb_user = firebase_auth.create_user(
            email=email,
            password=password
        )
    except firebase_exceptions.AlreadyExistsError:
        # 如果邮箱已经存在
        raise ValueError("Email 已经被注册")
    except Exception as e:
        # 其它 Auth 层面的错误
        raise RuntimeError(f"Auth 服务异常：{e}")

    # 2) （可选）将用户信息写入 Firestore
    user = User(
        user_id=fb_user.uid,
        email=email,
        # password 这里不存明文，也可以存个占位
        password=None
    )
    db.collection("users").document(fb_user.uid).set(user.to_dict())
    return fb_user.uid
def login_user(email: str, password: str):
    #看email存在嗎 註冊過嗎
    coll=db.collection("users")
    existing=coll.where("email","==",email).get()

    if not existing:
        raise ValueError("Email not exist, please register")
    
    # 讀回來的使用者資料在 Firestore，包含 hashed password
    user_doc = existing[0].to_dict()
    if not check_password_hash(user_doc["password"], password):
        raise ValueError("密碼錯誤")

    # （可選）同時也可以向 Firebase Auth 要一張 custom token
    firebase_user = firebase_auth.get_user_by_email(email)
    return {"uid": firebase_user.uid, "email": firebase_user.email}






