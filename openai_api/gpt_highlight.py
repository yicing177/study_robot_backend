import openai
import os
import json
from datetime import datetime
import requests

def generate_tts_for_text(text, user_id="anonymous"):
    # 1. 建立臨時 .json 檔案（給 TTS 用）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}.json"
    filepath = os.path.join("dir_text", filename)
    os.makedirs("dir_text", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"text": text}, f, ensure_ascii=False, indent=4)

    # 2. 呼叫原本的 /tts API（用 POST + filename）
    try:
        response = requests.post("http://localhost:5000/routes/tts", json={"filename": filename})
        result = response.json()
        if "file" in result:
            return result["file"]  # 回傳音檔名稱
        else:
            raise Exception(result.get("error", "TTS 回傳錯誤"))
    except Exception as e:
        raise RuntimeError(f"TTS 呼叫失敗：{e}")

def handle_highlight_action(text, action):
    if action == "read":
        prompt = f"請以簡單溫柔的語氣幫我朗讀這個英文單字或句子：{text}"
    elif action == "translate":
        prompt = f"請將這個英文單字或英文句子翻譯成繁體中文：{text}"
    elif action == "examples":
        prompt = f"請根據這句英文提供 3 個相關的實用例句（附上中文翻譯）：{text}"
    else:
        raise ValueError("未知的 action 類型")

    response = openai.ChatCompletion.create(
        model="gpt-4o", #model
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]
