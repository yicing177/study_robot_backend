from datetime import datetime
class Summary:
    def __init__(self, user_id, summary_text, title, conversation_id, timestamp = None):
        self.user_id = user_id
        self.summary_text = summary_text
        self.title = title
        self.conversation_id = conversation_id 
        self.timestamp = timestamp
    
    def to_dict(self):
        return{
            "user_id" : self.user_id,
            "summary_text" : self.summary_text,
            "title" : self.title,
            "conversation_id" : self.conversation_id,
            "timestamp" : self.timestamp.isoformat() if self.timestamp else None
        }
    

    @staticmethod
    def from_dict(data):
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None

        return Summary(
            user_id = data.get("user_id"),
            summary_text = data.get("summary_text"),
            title = data.get("title"),
            conversation_id = data.get("conversation_id"),
            timestamp = timestamp
        )

