import openai
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")

# 先萃取主題
def extract_topic_from_chat_history(chat_history):
    """
    根據完整對話記錄自動歸納主題（如現在完成式、情緒表達等）
    """
    try:
        prompt = [
            {
                "role": "system",
                "content": "你是一個英文學習助理，請閱讀以下對話並推論出使用者正在學習的主題，例如：現在完成式、問句用法、情緒表達等。請只回傳簡短主題名稱。"
            },
            {
                "role": "user",
                "content": "\n".join([msg["content"] for msg in chat_history if msg["role"] != "system"])
            }
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o", # model
            messages=prompt
        )
        topic = response.choices[0].message["content"].strip()
        return topic

    except Exception as e:
        print(f"[主題判斷錯誤] {e}")
        return "英文綜合練習"

# 用萃取完的主題來生成題目
def generate_quiz_from_chat_history(chat_history, num_questions=3, difficulty="medium"):
    """
    從 chat_history 中自動判斷主題並生成選擇題，支援難度選擇
    """
    try:
        topic = extract_topic_from_chat_history(chat_history)
        user_text = "\n".join([msg["content"] for msg in chat_history if msg["role"] == "user"])

        # 難度描述
        difficulty_description = {
            "easy": "題目以基本單字或文法為主，句型簡單、選項明確。",
            "medium": "題目涉及一般句型與文法理解，需適度思考後作答。",
            "hard": "題目包含進階句構、時態與語意陷阱，挑戰理解與推理能力。"
        }.get(difficulty, "題目涉及一般句型與文法理解，需適度思考後作答。")

        # Prompt 組合
        prompt = f"""根據以下英文學習對話內容，請你為使用者出 {num_questions} 題「{difficulty} 難度」的選擇題，主題為「{topic}」。

題目要求如下：
- 題目應與主題密切相關
- 每題包含：
  - question（題目文字）
  - options（四個選項）
  - answer（正確答案）
  - explanation（使用繁體中文簡要說明為何正解）
- 難度說明：「{difficulty_description}」

請以 JSON 陣列格式回傳，例如：
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "...",
    "explanation": "..."
  }}
]

以下是對話內容：
{user_text}
"""

        response = openai.ChatCompletion.create(
            model=os.getenv("GPT_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}]
        )

        raw_text = response.choices[0].message["content"].strip()

        # ✅ DEBUG 印出 GPT 原始回應
        if os.getenv("DEBUG_MODE", "false").lower() == "true":
            print("[GPT 回傳原始內容]:\n", raw_text)

        # ✅ 從 GPT 回傳中擷取 JSON 區塊（防止 markdown 包裹 + 多餘說明）
        match = re.search(r"\[\s*{.*?}\s*]", raw_text, re.DOTALL)
        if match:
            json_text = match.group(0)
            return json.loads(json_text)
        else:
            print("[⚠️ 無法擷取有效 JSON 區段，原始內容如下]:\n", raw_text)
            return []

    except json.JSONDecodeError as je:
        print(f"[JSON 解析錯誤] {je}")
        return []

    except Exception as e:
        print(f"[出題錯誤] {e}")
        return []

