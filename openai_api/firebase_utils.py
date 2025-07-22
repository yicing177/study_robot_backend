# 訊息與總結於資料庫的寫入(初版，根據資料庫實際架構再去調整)

from firebase_admin import firestore
from datetime import datetime

db = firestore.client()

def save_message_to_firestore(user_id, conversation_id, message):
    doc_ref = db.collection("Users").document(user_id) \
                .collection("Conversations").document(conversation_id) \
                .collection("Messages").document()

    message_data = {
        "role": message["role"],
        "content": message["content"],
        "timestamp": message.get("timestamp", datetime.now().isoformat())
    }
    doc_ref.set(message_data)

def save_summary_to_firestore(user_id, conversation_id, summary_text):
    summary_ref = db.collection("Users").document(user_id) \
                .collection("Conversations").document(conversation_id)

    summary_ref.set({
        "summary": summary_text,
        "updatedAt": datetime.now().isoformat()
    }, merge=True)

def save_conversation_metadata(user_id, conversation_id, title):
    doc_ref = db.collection("Users").document(user_id).collection("Conversations").document(conversation_id)
    doc_ref.set({
        "title": title,
        "createdAt": datetime.now().isoformat()
    }, merge=True)