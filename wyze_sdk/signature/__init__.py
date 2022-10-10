import hashlib
import hmac
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from time import time
from typing import Optional, Union


class Clock:

    def now(self) -> float:
        return time()

    def nonce(self):
        return round(self.now() * 1000)


class RequestVerifier:

    def __init__(self, signing_secret: str, access_token: Optional[str] = None, clock: Clock = Clock()):
        self.signing_secret = signing_secret
        self.access_token = access_token
        self.clock = clock

    def request_id(self, timestamp: Optional[int] = None):
        if timestamp is not None:
            return self.md5_string(str(self.md5_string(timestamp)))

        return self.md5_string(self.md5_string(str(self.clock.nonce())))

    def md5_string(self, body: Union[str, bytes] = "") -> str:
        if isinstance(body, str):
            body = str.encode(body)
        return hashlib.md5(body).hexdigest()

    def generate_signature(
        self, *, timestamp: str, body: Union[str, bytes]
    ) -> Optional[str]:
        """Generates a standard signature"""
        if timestamp is None:
            return None
        if body is None:
            body = ""
        if isinstance(body, bytes):
            body = body.decode("utf-8")

        format_req = str.encode(f"{body}")
        encoded_secret = str.encode(self.signing_secret)
        request_hash = hmac.new(encoded_secret, format_req, hashlib.md5).hexdigest()
        calculated_signature = f"{request_hash}"
        return calculated_signature

    def generate_dynamic_signature(
        self, *, timestamp: str, body: Union[str, bytes]
    ) -> Optional[str]:
        """Generates a dynamic signature"""
        if timestamp is None:
            return None
        if body is None:
            body = ""
        if isinstance(body, bytes):
            body = body.decode("utf-8")

        format_req = str.encode(f"{body}")
        encoded_secret = str.encode(self.md5_string(f"{self.access_token}{self.signing_secret}"))
        request_hash = hmac.new(encoded_secret, format_req, hashlib.md5).hexdigest()
        calculated_signature = f"{request_hash}"
        return calculated_signature


class MD5Hasher:

    def hash(self, data: Union[str, bytes] = "") -> bytes:
        if isinstance(data, str):
            data = data.encode()
        return hashlib.md5(data).digest()

    def hex(self, data: Union[str, bytes] = "") -> str:
        if isinstance(data, str):
            data = data.encode()
        return hashlib.md5(data).hexdigest()


class CBCEncryptor:

    def __init__(self, iv: Union[str, bytes]):
        if isinstance(iv, str):
            iv = iv.encode()
        self.iv = iv

    def encrypt(self, key: Union[str, bytes], data: Union[str, bytes]) -> bytes:
        if isinstance(key, str):
            key = key.encode()
        if isinstance(data, str):
            data = data.encode()
        cipher = AES.new(key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(pad(data, AES.block_size))

    def decrypt(self, key: Union[str, bytes], data: Union[str, bytes]) -> bytes:
        if isinstance(key, str):
            key = key.encode()
        if isinstance(data, str):
            data = bytes.fromhex(data)
        cipher = AES.new(key, AES.MODE_CBC, self.iv)
        return unpad(cipher.decrypt(data), AES.block_size)
