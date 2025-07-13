from abc import ABC, abstractmethod
from domain.entities.user import User

class UserRepository(ABC):

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> User:
        pass
    
    @abstractmethod
    def get_all_users_summary(self) -> str:
        pass