# gpt_service.py（邏輯層）
import traceback
import openai
import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime
from firebase_config import db  # Firestore 客戶端
from openai_api.gpt_quiz_service import generate_quiz_from_chat_history # 呼叫生成題目邏輯
from openai_api.conversation_manager import ConversationPool
from openai_api.firebase_utils import save_summary_to_firestore

# 初始化對話池
conversation_pool = ConversationPool()

# 載入環境變數
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")

# 情緒相關設定
def map_rate_to_scale(rate_label):
    return {
        "slow": 30,
        "normal": 60,
        "fast": 90
    }.get(rate_label, 60)

# 情緒相關設定
def map_style_degree_to_scale(style_degree):
    try:
        s = float(style_degree)
        return max(0.1, min(round(s * 0.6, 2), 2.0))
    except:
        return 1.0

# 自動量化情緒條件
def analyze_speech_parameters_with_gpt(text):
    try:
        messages = [
            {"role": "system", "content": "請根據以下內容判斷適合的語音風格，請以 JSON 格式回傳：{\"emotion\": \"cheerful, sad, excited, friendly, hopeful, serious, gentle, affectionate, calm\" 之一, \"rate\": \"slow|normal|fast\", \"style_degree\": 1~3 數字}"},
            {"role": "user", "content": text}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        result = response.choices[0].message["content"].strip()
        parsed = json.loads(result)
        return {
            "emotion": parsed.get("emotion", "calm"),
            "rate": map_rate_to_scale(parsed.get("rate", "normal")),
            "style_degree": map_style_degree_to_scale(parsed.get("style_degree", 1))
        }
    except Exception as e:
        print(f"[語音參數分析錯誤] {e}")
        return {"emotion": "calm", "rate": 60, "style_degree": 1.0}

# GPT對話主邏輯
def get_gpt_reply(user_input, user_id="unknown", conversation_id=None):
    #從對話池撈指定的對話
    conv = conversation_pool.get_or_create(user_id, conversation_id)
    #print(f"印出 conversation_id: {conversation_id}")

    try:
        conv.append_message("user", user_input)
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=conv.get_chat_history_for_gpt()
        )
        reply_text = response.choices[0].message["content"]
        conv.append_message("assistant", reply_text)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = "dir_text"
        os.makedirs(folder_path, exist_ok=True)

        speech_settings = analyze_speech_parameters_with_gpt(reply_text)
        cleaned_tts_text = remove_emoji(clean_text_for_tts(reply_text))

        # 儲存 TTS JSON
        json_path = os.path.join(folder_path, f"{user_id}_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump({
                "text": cleaned_tts_text,
                "emotion": speech_settings["emotion"],
                "rate": speech_settings["rate"],
                "style_degree": speech_settings["style_degree"]
            }, jf, ensure_ascii=False, indent=4)

        return {
            "reply": reply_text,
            "filename": f"{user_id}_{timestamp}.json",
            "emotion": speech_settings["emotion"],
            "rate": speech_settings["rate"],
            "style_degree": speech_settings["style_degree"],
            "conversation_id": conv.conversation_id if conv else None
        }

    except Exception as e:
        print(f"[GPT 錯誤] {e}")
        traceback.print_exc()  # ✅ 印出完整錯誤行數與堆疊
    
        return {
            "reply": "抱歉，我目前無法提供回覆，請稍後再試一次。",
            "filename": None,
            "emotion": "calm",
            "rate": 60,
            "style_degree": 1.0,
            "conversation_id": conv.conversation_id if conv else None
        }

# 總結主邏輯 (含自動整合)
def summarize_chat(user_id="unknown", conversation_id=None):
    conv = conversation_pool.get_or_create(user_id, conversation_id)

    try:
        messages = conv.get_summary_input()
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        summary_text = response.choices[0].message["content"]
        conv.append_summary(summary_text)

        # 合併所有摘要成一份整體摘要（純文字接起來）
        all_summaries = [s["text"] for s in conv.export_summary()]
        full_summary = "\n".join(all_summaries)

        # 儲存合併後的總結到 Firestore
        save_summary_to_firestore(user_id, conversation_id, full_summary)

        return full_summary
    except Exception as e:
        print(f"[總結錯誤] {e}")
        return "抱歉，無法整理學習重點，請稍後再試一次。"

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
def reset_chat_history(user_id="unknown", conversation_id=None):
    # 這裡傳入 None → 會建立新的 Conversation
    conv = conversation_pool.get_or_create(user_id, conversation_id)
    # 不需要再 start_new_round()，新 conv 本來就是乾淨的
    return conv  # ✅ 回傳給路由好帶回前端

# 生成題目 (主邏輯寫在gpt_quiz_service.py裡)
def generate_quiz_from_chat(user_id="unknown", conversation_id=None, num_questions=3):
    conv = conversation_pool.get_or_create(user_id,conversation_id)
    return generate_quiz_from_chat_history(conv.export_messages(), num_questions)

# 清除JSON的強調符號
import re, unicodedata

_ZW_SPACES = u"\u200B\u200C\u200D\u200E\u200F\uFEFF"   # 零寬/方向符
_BULLETS = "•●◦▪▫※・‧"                                  # 常見項目符號

def clean_text_for_tts(text: str) -> str:
    if not text:
        return ""

    # 1) 全形→半形，正規化（把全形 *、＿、冒號等轉成 ASCII）
    t = unicodedata.normalize("NFKC", text)

    # 2) 移除零寬字元、NBSP
    t = re.sub(f"[{_ZW_SPACES}]", "", t)
    t = t.replace("\u00A0", " ")

    # 3) 移除多行程式碼區塊與行內程式碼
    t = re.sub(r"```.*?```", "", t, flags=re.DOTALL)
    t = re.sub(r"`([^`]*)`", r"\1", t)

    # 4) 連結/圖片語法：保留文字
    t = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", t)          # 圖片整段去掉
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)      # [text](url) -> text

    # 5) 標題與引用（#、>）
    t = re.sub(r"^\s{0,3}#{1,6}\s*", "", t, flags=re.MULTILINE)
    t = re.sub(r"^\s*>\s*", "", t, flags=re.MULTILINE)

    # 6) 列表記號：行首 - * + 與「行首/行內的數字編號」都處理
    t = re.sub(r"^\s*[-*+]\s+", "", t, flags=re.MULTILINE)     # - * + 列表
    t = re.sub(r"(^|\s)\d+\.\s+", r"\1", t, flags=re.MULTILINE)  # 這行是關鍵修正！
    for b in _BULLETS:
        t = t.replace(b, "")

    # 7) 粗體/斜體（允許跨行）
    t = re.sub(r"(\*\*|__)(.*?)\1", r"\2", t, flags=re.DOTALL)
    t = re.sub(r"(\*|_)(.*?)\1", r"\2", t, flags=re.DOTALL)

    # 8) 保險：若仍有散落 * 或 _（未成對），一律移除
    t = t.replace("*", "").replace("_", "")

    # 9) 空白整理
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[ \t]{2,}", " ", t)

    return t.strip()

# 清除JSON的表情符號
def remove_emoji(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # 😀 表情
        u"\U0001F300-\U0001F5FF"  # 💡 符號
        u"\U0001F680-\U0001F6FF"  # 🚀 車輛
        u"\U0001F1E0-\U0001F1FF"  # 🇺🇸 國旗
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# 自動生成對話標題
def generate_conversation_title(initial_message):
    try:
        prompt = [
            {"role": "system", "content": "請根據這段對話內容生成一個 10 字以內的中文標題，簡潔描述主題，不要加引號。"},
            {"role": "user", "content": initial_message[:100]}
        ]
        response = openai.ChatCompletion.create(
            model=os.getenv("GPT_MODEL", "gpt-4o"),
            messages=prompt
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("[標題產生失敗]", e)
        return "未命名對話"