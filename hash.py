import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

# hash the password without using a salt
# since the function requires a salt of an appropriate length. we pass a common
# salt "0000000000000000" after converting it to bytes.
def hash_without_salt(password):
    kdf = Argon2id(iterations = 1, lanes=4, memory_cost = 64*64, salt=('0' * 16).encode("utf-8"), length=16)
    return kdf.derive(password)

# hash the password using a custom salt
def hash_with_salt(password, salt):
    kdf = Argon2id(iterations = 1, lanes=4, memory_cost = 64*64, salt=salt, length=16)
    return kdf.derive(password)
