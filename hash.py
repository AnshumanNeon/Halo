import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

def hash_without_salt(password):
    kdf = Argon2id(iterations = 1, lanes=4, memory_cost = 64*64, salt=('0' * 16).encode("utf-8"), length=16)
    return kdf.derive(password)

def hash_with_salt(password, salt):
    kdf = Argon2id(iterations = 1, lanes=4, memory_cost = 64*64, salt=salt, length=16)
    return kdf.derive(password)
