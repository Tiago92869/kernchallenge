class UserSchema:
    @staticmethod
    def serialize_user(user):
        return{
            "id": str(user.id),
            "firstname": user.first_name,
            "lastname": user.last_name,
            "email": user.email,
            "is_active": user.is_active
        }
    
    @staticmethod
    def serialize_login(auth_token, refresh_token):
        return {
            "auth_token": auth_token,
            "refresh_token": refresh_token
        }
    
    