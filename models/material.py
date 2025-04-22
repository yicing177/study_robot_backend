class Material:
    def __init__(self, user_id, title, material_id, file_url="None", upload_time="None"):
        self.user_id=user_id
        self.title=title
        self.file_url=file_url
        self.upload_time=upload_time
        self.material_id=material_id

    def to_dict(self):
        return{
            "user_id":self.user_id,
            "title": self.title,
            "file_url":self.file_url,
            "material_id":self.material_id,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None
        }              

    @staticmethod
    def from_dict(data):
        return Material(
            user_id=data.get("user_id"),
            title=data.get("title"),
            file_url=data.get("file_url"),
            material_id=data.get("material_id"),
            upload_time=data.get("upload_time")
        )