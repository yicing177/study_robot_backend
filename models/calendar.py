from datetime import datetime;

class Calendar:
    def __init__(self, calendar_id, user_id, title, content, datetime, xposition, yposition, created_at=None):
        self.calendar_id = calendar_id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.datetime = datetime
        self.xposition = xposition
        self.yposition = yposition
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return{
            "calendar_id" : self.calendar_id,
            "user_id": self.user_id,
            "title" : self.title,
            "content" : self.content,
            "datetime" : self.datetime.isoformat(),
            "xposition" : self.xposition,
            "yposition" : self.yposition,
            "created_at" : self.created_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        return Calendar(
            calendar_id = data.get("calendar_id"),
            user_id = data.get("user_id"),
            title = data.get("title"),
            content = data.get("content"),
            datetime = datetime.fromisoformat(data.get("datetime")),
            xposition = data.get("xposition"),
            yposition = data.get("yposition"),
            created_at = datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None,

        )


