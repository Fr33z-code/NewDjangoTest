class BaseService:
    def __init__(self, user=None):
        self.user = user

    def set_user(self, user):
        self.user = user
        return self

    def is_authenticated(self):
        return self.user is not None and self.user.is_authenticated
