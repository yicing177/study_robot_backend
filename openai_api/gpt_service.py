# gpt_service.py（邏輯層）
import openai
import os
from dotenv import load_dotenv
from datetime import datetime
from firebase_config import db  # Firestore 客戶端
import json

# 載入環境變數
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")

# 初始系統提示
system_prompt = {"role": "system", "content": "你是一個溫柔有耐心的英文學習伴讀機器人，請使用簡單語言並加入例句解釋。"}
chat_history = [system_prompt]          # 有限長度，供 GPT 回應使用
all_chat_history = [system_prompt]      # 完整記錄，供 summarize 使用

MAX_HISTORY_LENGTH = 10 # 先預設10筆，測試時方便節省token

# 儲存對話紀錄 (做總結與智慧多輪對答)
def update_chat_history(role, content):
    global chat_history, all_chat_history

    chat_history.append({"role": role, "content": content})
    while len(chat_history) > MAX_HISTORY_LENGTH + 1:
        chat_history.pop(1)

    all_chat_history.append({"role": role, "content": content})

# 對話邏輯
def get_gpt_reply(user_input, user_id="unknown"):
    global chat_history

    print("✅ 收到 user_input：", user_input)
    print("✅ 當前金鑰長度：", len(openai.api_key))  # 確認 key 有被載入

    try:
        update_chat_history("user", user_input)

        response = openai.ChatCompletion.create(
            model="gpt-4o", # 測試時先用4o節省token
            messages=chat_history
        )
        reply_text = response.choices[0].message["content"]
        update_chat_history("assistant", reply_text)

        # 存回覆到 dir_text/
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = "dir_text"
        os.makedirs(folder_path, exist_ok=True)

        # 存 .txt
        filename = f"{user_id}_{timestamp}.txt"
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(reply_text)

        # 存 .json（給 TTS 用）
        json_path = os.path.join(folder_path, f"{user_id}_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump({"text": reply_text}, jf, ensure_ascii=False, indent=4)

        return {
            "reply": reply_text,
            "filename": f"{user_id}_{timestamp}.json"
        }


    except Exception as e:
        print(f"[GPT 錯誤] {e}")
        return "抱歉，我目前無法提供回覆，請稍後再試一次。"

# 用歷史紀錄做總結
def summarize_chat(user_id="unknown"):
    global all_chat_history

    try:
        history_copy = all_chat_history.copy()
        history_copy.append({
            "role": "user",
            "content": "請根據以上對話，整理出這次學習內容的重點摘要，使用條列式。"
        })

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=history_copy
        )
        summary_text = response.choices[0].message["content"]

        save_summary_to_firestore(user_id, summary_text)
        return summary_text

    except Exception as e:
        print(f"[總算錯誤] {e}")
        return "抱歉，無法整理學習重點，請稍後再試一次。"

# 儲存歷史紀錄到資料庫 (測試中)
def save_summary_to_firestore(user_id, summary_text):
    try:
        doc_ref = db.collection('summaries').document()
        doc_ref.set({
            'user_id': user_id,
            'summary': summary_text,
            'timestamp': datetime.now()
        })
    except Exception as e:
        print(f"[Firestore 儲存錯誤] {e}")

# 從資料庫調用總結 (測試中)
def get_user_summaries(user_id):
    try:
        docs = db.collection('summaries')\
                 .where('user_id', '==', user_id)\
                 .order_by('timestamp', direction='DESCENDING')\
                 .stream()

        summary_list = []
        for doc in docs:
            data = doc.to_dict()
            summary_list.append({
                'summary': data.get('summary', ''),
                'timestamp': data.get('timestamp').strftime("%Y-%m-%d %H:%M:%S")
            })

        return summary_list

    except Exception as e:
        print(f"[Firestore 查詢錯誤] {e}")
        return []

# 調用stt結果
def get_text_from_stt_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("transcript", "")
    except Exception as e:
        print(f"[讀取 STT JSON 錯誤] {e}")
        return ""

# 開啟新對話 (重製暫存紀錄)
def reset_chat_history():
    global chat_history, all_chat_history
    chat_history = [system_prompt]
    all_chat_history = [system_prompt]

