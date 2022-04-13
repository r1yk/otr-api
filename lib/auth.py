from base64 import urlsafe_b64encode, urlsafe_b64decode
from datetime import datetime
import hashlib
import hmac
import json
from typing import Union

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from lib.models import User

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "mydumbsecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
HASH_METHOD = 'sha256'


class JWT:
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    @classmethod
    def create_token(cls, payload: dict) -> str:
        """Encode the headers + payload, and sign with the secret key."""
        encoded_headers = JWT.base64_encode(json.dumps(JWT.headers).encode())
        encoded_payload = JWT.base64_encode(json.dumps(payload).encode())
        to_sign = f"{encoded_headers.decode()}.{encoded_payload.decode()}"
        signature = JWT.get_signature(to_sign)
        return f"{to_sign}.{signature}"

    @classmethod
    def get_signature(cls, message: str) -> str:
        hs256 = hmac.new(
            key=SECRET_KEY.encode(),
            msg=message.encode(),
            digestmod=HASH_METHOD
        )
        return JWT.base64_encode(hs256.digest()).decode()

    @classmethod
    def verify_signature(cls, message: str, signature: str) -> bool:
        return JWT.get_signature(message) == signature

    @classmethod
    def decode_token(cls, token: str) -> dict:
        """Decode the payload, and confirm that it was signed with the secret key."""
        components = token.split('.')
        if len(components) == 3:
            message = '.'.join(components[0:2])
            payload = components[1]
            signature = components[2]
            if JWT.verify_signature(message, signature):
                payload_decoded = json.loads(JWT.base64_decode(payload))
                expiration = payload_decoded['exp']
                if datetime.fromtimestamp(expiration) < datetime.utcnow():
                    print('token expired')
                    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

                return payload_decoded

        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    @classmethod
    def string_to_b64(cls, input: str) -> bytes:
        return JWT.base64_encode(input.encode())

    @classmethod
    def b64_to_string(cls, input: bytes) -> str:
        return JWT.base64_decode(input)

    @classmethod
    def base64_decode(cls, input: Union[str, bytes]) -> bytes:
        if isinstance(input, str):
            input = input.encode()

        padding_needed = 4 - (len(input) % 4)
        if padding_needed > 0:
            input += (b"=" * padding_needed)

        return urlsafe_b64decode(input)

    @classmethod
    def base64_encode(cls, input: bytes) -> bytes:
        return urlsafe_b64encode(input).replace(b"=", b"")


class OTRAuth:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, user_id: str, password: str) -> User:
        """Get the specified user from the database and make sure the hashed passwords match."""
        user = self.get_user(user_id)
        if not user:
            self.return_401()

        hashed_password = hashlib.new(
            HASH_METHOD, password.encode()).hexdigest()
        if hashed_password == user.hashed_password:
            return user

        self.return_401()

    def get_user(self, user_id) -> User:
        """Return the requested user in the database, if it exists."""
        try:
            return self.db.query(User).filter_by(email=user_id).one()
        except NoResultFound:
            self.return_401()

    @classmethod
    def create_token(cls, data: dict) -> str:
        """Encode and cryptographically sign the data to create a new JWT."""

    @classmethod
    def return_401(cls):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
