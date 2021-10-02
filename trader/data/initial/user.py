from dataclasses import dataclass
from typing import Optional
from trader.connections.database import session
from trader.data.initial.base import BaseData
from trader.models.user import User


@dataclass(frozen=True, eq=True)
class UserData(BaseData):
    first_name: str
    last_name: str
    email: str
    is_demo: bool = True
    is_live: bool = True

    def query_instance(self) -> Optional[User]:
        return session.query(User).filter_by(email=self.email).one_or_none()

    def create_instance(self) -> User:
        return User(first_name=self.first_name, last_name=self.last_name, email=self.email)


USER_ADMIN = UserData("user_admin_id", "admin", "user", "admin@email.com")
USERS = (USER_ADMIN,)
