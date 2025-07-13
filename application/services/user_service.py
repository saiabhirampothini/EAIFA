from domain.repositories.user_repo import UserRepository
from domain.entities.user import User

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_user_by_id(self, user_id: str) -> User:
        return self.user_repo.get_user_by_id(user_id)
    
    def get_all_users_summary(self) ->str:
        return self.user_repo.get_all_users_summary()