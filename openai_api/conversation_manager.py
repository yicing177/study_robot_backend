#管理conversation與chat
#使用pool與manager兩個類別

from openai_api.firebase_utils import save_conversation_metadata
from datetime import datetime
import uuid
from openai_api.firebase_utils import save_message_to_firestore, save_summary_to_firestore
from models.chatmessage import Chatmessage

# 管理單個對話中的多段聊天紀錄
class ConversationManager:
    def __init__(self, conversation_id=None, user_id="unknown", system_prompt=None):
        today_str = datetime.now().strftime("%m%d%H%S")
        self.title = f"{today_str}重點整理"
        self.user_id = user_id
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.create_at = datetime.utcnow()  # ✅ 建立時間
        

        self.system_prompt = system_prompt or {
            "role": "system",
            "content": "你是一個溫柔有耐心的英文學習伴讀機器人，請使用簡單語言並加入例句解釋。請用繁體中文回答。"
        }

        self.chat_history = [self.system_prompt]            # 短記憶，給 GPT 使用
        self.current_history = [self.system_prompt]         # 本輪對話（聊天 B）
        self.full_conversation_history = [self.system_prompt]  # 全部歷史（聊天 A+B+...）

        self.summary_parts = []  # 儲存每段 summary 的結果

        # ✅ 初始化時寫入 metadata 到 Firestore


        try:
            save_conversation_metadata(
                self.user_id,
                self.conversation_id,
                self.title or "未命名對話",  # 初始未設定 title，後面會用第一句 user 話補上
                self.create_at
            )
        except Exception as e:
            print("[Firestore 寫入 conversation metadata 失敗]", e)

    def append_message(self, role, content):
        msg = Chatmessage (
            conversation_id = self.conversation_id,
            role = role,
            content = content,
            timestamp = datetime.now().isoformat(),
        )

        self.chat_history.append(msg.to_dict())
        self.current_history.append(msg.to_dict())
        self.full_conversation_history.append(msg.to_dict())

        # 控制 chat_history 長度
        MAX_HISTORY_LENGTH = 10
        if len(self.chat_history) > MAX_HISTORY_LENGTH + 1:
            self.chat_history.pop(1)

        # 寫入 Firestore
        try:
            save_message_to_firestore(self.user_id, msg)
        except Exception as e:
            print("[Firestore 寫入訊息失敗]", e)

    def start_new_round(self):
        # 清空這輪（聊天 B）
        self.chat_history = [self.system_prompt]
        self.current_history = [self.system_prompt]

    def get_summary_input(self):
        # 取得這輪對話的摘要輸入
        return self.current_history.copy() + [{
            "role": "user",
            "content": "請根據以上對話，整理出這次學習內容的重點摘要，使用條列式。"
        }]

    def append_summary(self, summary_text):
        if not self.summary_parts:
            self.summary_parts.append({
                "part": 1,
                "text": summary_text,
                "timestamp": datetime.utcnow()
            })
        else:
            self.summary_parts[0]["text"] += "\n" + summary_text
            self.summary_parts[0]["timestamp"] = datetime.utcnow()
        
        # 寫入 Firestore
        try:
            save_summary_to_firestore(self.user_id, self.conversation_id, self.summary_parts[0]["text"])
        except Exception as e:
            print("[Firestore 寫入摘要失敗]", e)

    def export_summary(self):
        return self.summary_parts

    def export_messages(self):
        return self.full_conversation_history

    def export_current_round(self):
        return self.current_history

    def get_chat_history_for_gpt(self):
        return self.chat_history

# 管理多個對話
class ConversationPool:
    def __init__(self):
        self.user_conversations = {}

    def get_or_create(self, user_id, conv_id=None):
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = {}

        if conv_id and conv_id in self.user_conversations[user_id]:
            return self.user_conversations[user_id][conv_id]

        # 建立新 conversation
        from .conversation_manager import ConversationManager
        new_conv = ConversationManager(conversation_id=conv_id, user_id=user_id)
        self.user_conversations[user_id][new_conv.conversation_id] = new_conv
        return new_conv
    
    def create(self, user_id):  
        from .conversation_manager import ConversationManager
        new_conv = ConversationManager(user_id=user_id)
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = {}
        self.user_conversations[user_id][new_conv.conversation_id] = new_conv
        return new_conv

    def list_conversations(self, user_id):
        return list(self.user_conversations.get(user_id, {}).keys())

    def get_conversation(self, user_id, conv_id):
        return self.user_conversations.get(user_id, {}).get(conv_id)
    
    def get_all_conversations(self, user_id):
        return list(self.user_conversations.get(user_id, {}).values())