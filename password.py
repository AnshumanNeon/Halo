import mysql
import os
from hash import *
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def show_all_passwords(cursor, userid):
    cursor.execute("select label, description from passwords where userid=%s", (userid,))

    x = cursor.fetchall()

    if len(x) <= 0:
        print("No passwords available for your user.")
        
        if input("Continue..."): return
    else:
        for a in x:
            print(a)

def create_new_password(cursor, vault_key, userid, label, description):
    generated_psw = os.urandom(8).hex()

    t = os.urandom(4)
    psw_salt = hash_without_salt(t)

    aes1 = AESGCM(vault_key)
    nonce1 = os.urandom(8)
    psw_hash = aes1.encrypt(nonce1, psw_salt, None)

    aes2 = AESGCM(psw_salt)
    nonce2 = os.urandom(8)
    protected_password = aes2.encrypt(nonce2, generated_psw.encode("utf-8"), None)

    cursor.execute("insert into passwords (userid, protected_password, label, description, password_hash, nonce1, nonce2) values (%s, %s, %s, %s, %s, %s, %s)", (userid, protected_password, label, description, psw_hash, nonce1, nonce2))
    print("Password created for your user successfully!!")
    if input("Continue..."): return

def get_password(cursor, vault_key, label):
    cursor.execute("select protected_password, password_hash, nonce1, nonce2 from passwords where label=%s", (label,))

    x = cursor.fetchall()[0]

    protected_password = x[0]
    psw_hash = x[1]
    nonce1 = x[2]
    nonce2 = x[3]

    aes1 = AESGCM(vault_key)
    psw_salt = aes1.decrypt(nonce1, psw_hash, None)

    aes2 = AESGCM(psw_salt)
    password = aes2.decrypt(nonce2, protected_password, None)

    print("Your password is:", password.decode("utf-8"))
    if input("Continue..."): return
