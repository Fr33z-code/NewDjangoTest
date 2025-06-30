class BaseService:
    def __init__(self, user=None):
        self.user = user

    def set_user(self, user):
        self.user = user
        return self
