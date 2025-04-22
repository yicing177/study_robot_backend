import sys
import os

# 一定要先加路徑，這樣 Python 才找得到 models 跟 firebase_config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.user import User
from firebase_config import db

def test_create_user():
    user = User(user_id="test001", email="test@beauty.com", name="美女測試")
    db.collection("users").document(user.user_id).set(user.to_dict())
    print("上傳成功！")

def test_get_user():
    doc = db.collection("users").document("test001").get()
    if doc.exists:
        user = User.from_dict(doc.to_dict())
        print("撈到使用者：", user.name)
    else:
        print("找不到使用者")

# 呼叫測試看看
test_create_user()
test_get_user()
