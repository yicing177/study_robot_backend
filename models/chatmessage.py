from datetime import datetime

class Chatmessage:
    def __init__(self, conversation_id, role, content, create_at = None): 
        if isinstance(create_at, str):  # ✅ 重點在這裡
            create_at = datetime.fromisoformat(create_at)
        self.conversation_id = conversation_id
        self.role = role
        self.content = content
        self.create_at = create_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            "conversation_id" : self.conversation_id,
            "role" : self.role,
            "content" : self.content,
            "create_at" : self.create_at.isoformat() if self.create_at else None
        }

    @staticmethod
    def from_dict(data):
        timestamp_str = data.get("create_at")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
        
        return Chatmessage(
            conversation_id = data.get("conversation_id"),
            role = data.get("role"),
            content = data.get("content"),
            create_at = timestamp
        )

        