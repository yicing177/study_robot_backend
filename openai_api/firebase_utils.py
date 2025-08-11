# 訊息與總結於資料庫的寫入(初版，根據資料庫實際架構再去調整)service

from firebase_admin import firestore
from datetime import datetime
from models.chatmessage import Chatmessage
db = firestore.client()

def save_message_to_firestore(user_id, chat_message : Chatmessage):
    doc_ref = db.collection("Users").document(user_id) \
                .collection("Conversations").document(chat_message.conversation_id) \
                .collection("Messages").document()

    timestamp = chat_message.timestamp or firestore.SERVER_TIMESTAMP
    message_data = {
        "role": chat_message.role,
        "content": chat_message.content,
        "timestamp": timestamp
    }
    doc_ref.set(message_data)


def save_summary_to_firestore(user_id, conversation_id, summary_text):

    summary_ref = db.collection("Users").document(user_id) \
                .collection("Conversations").document(conversation_id)
    print(summary_ref.conversation_id)
    try:
        old_doc = summary_ref.get()
        old_sum = ""
        if old_doc.exists:
            old_sum =old_doc.to_dict().get("summary") 
        print("old one:" )
        print(old_sum)
        print("new:")
        print(summary_text)
        summary_ref.set({
            "summary": summary_text,
            "updatedAt": datetime.now().isoformat(),
        }, merge=True)
        print("success")
    except Exception as e :
        print("failed", e)
def save_conversation_metadata(user_id, conversation_id, title, create_at):

    doc_ref = db.collection("Users").document(user_id).collection("Conversations").document(conversation_id)
    doc_ref.set({
        "title": title,
        "createdAt": create_at.isoformat()
    }, merge=True)