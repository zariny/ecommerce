import json
import uuid
import jwt
from datetime import datetime, UTC
from cryptography.fernet import Fernet
from django.conf import settings


class JWTToken:
    conf = settings.JWT
    fernet = Fernet(conf["FIELD_ENCRYPTION_KEY"])
    algorithem = "HS256"

    def __init__(self, token: str):
        self.token = token

    @property
    def payload(self) -> dict:
        result = jwt.decode(
            self.token, self.conf["JWT_SIGN_KEY"], algorithms=[self.algorithem]
        )
        if "perms" in result:
            result["perms"] = self.decriptor(result["perms"])
        return result

    @staticmethod
    def encriptor(data) -> str:
        return JWTToken.fernet.encrypt(json.dumps(data).encode()).decode()

    @staticmethod
    def decriptor(encripted: str) -> json:
        return json.loads(JWTToken.fernet.decrypt(encripted.encode()))

    @classmethod
    def new_access_token(cls, user_id: int, permissions: list[str]) -> str:
        now = datetime.now(UTC)
        payload = {
            "token_type": "access",
            "user_id": user_id,
            "perms": cls.encriptor(permissions),
            "iat": now,
            "exp": now + cls.conf["ACCESS_TOKEN_LIFETIME"],
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, cls.conf["JWT_SIGN_KEY"], algorithm=cls.algorithem)

    @classmethod
    def new_refresh_token(cls, user_id: int) -> str:
        now = datetime.now(UTC)
        payload = {
            "token_type": "refresh",
            "user_id": user_id,
            "iat": now,
            "exp": now + cls.conf["REFRESH_TOKEN_LIFETIME"],
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, cls.conf["JWT_SIGN_KEY"], algorithm=cls.algorithem)
