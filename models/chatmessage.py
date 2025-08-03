from datetime import datetime

class Chatmessage:
    def __init__(self, conversation_id, role, content, timestamp=None): 
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        self.conversation_id = conversation_id
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self):
        return {
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return Chatmessage(
            conversation_id=data.get("conversation_id"),
            role=data.get("role"),
            content=data.get("content"),
            timestamp=data.get("timestamp")
        )
