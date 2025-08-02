from datetime import datetime  
class Chathistory:
    def __init__(self, user_id, conversation_id, title, create_at = None, upload_at = None):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.title = title
        self.upload_at = upload_at
        self.create_at = create_at or datetime.utcnow()

    def to_dict(self):
        return {
            "user_id" : self.user_id,
            "conversation_id" : self.conversation_id,
            "title" : self.title,
            "upload_at": self.upload_at.isoformat() if self.upload_at else None,
            "create_at" : self.create_at.isoformat() if self.create_at else None
        }
    
@staticmethod
def from_dict(data):
    create_str = data.get("create_at")
    upload_str = data.get("upload_at")

    return Chathistory(
        user_id=data.get("user_id"),
        conversation_id=data.get("conversation_id"),
        title=data.get("title"),
        create_at=datetime.fromisoformat(create_str) if create_str else None,
        upload_at=datetime.fromisoformat(upload_str) if upload_str else None
    )
