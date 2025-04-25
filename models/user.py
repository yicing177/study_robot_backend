class User:
    def __init__(self, user_id, email, name="None"):
        self.user_id= user_id
        self.email= email
        self.name= name
    
    def to_dict(self):
        return{
            "user_id":self.user_id,
            "email":self.email,
            "name":self.name
        }

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data.get("user_id"),
            email=data.get("email"),
            name=data.get("name")
        )


    