class Music:
    def __init__(self, user_id, title, url):
        self.user_id = user_id
        self.title = title
        self.url = url
    def to_dict(self):
        return{
            "user_id" : self.user_id,
            "title" : self.title,
            "url" : self.url
        }
    
    @staticmethod
    def from_dict(data):

        return Music(
            user_id =data.get( "user_id"),
            title = data.get("title"),
            url = data.get("url")
        ) 
        

        