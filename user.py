from hash import *
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def create_user(cursor):
    username = input("Enter username: ")
    master_password = input("Enter password: ")

    # create a userid

    userid = int.from_bytes(os.urandom(8))

    # create a pivate key

    master_key = hash_without_salt(master_password.encode("utf-8"))
    random_number = os.urandom(32)
    vault_key = hash_without_salt(random_number)

    aes = AESGCM(master_key)
    nonce = os.urandom(8)
    private_key = aes.encrypt(nonce, vault_key, None)

    # create a master password hash

    master_password_hash = hash_with_salt(master_key, master_password.encode("utf-8"))

    # enter into the mysql table

    cursor.execute("insert into users (userid, username, private_key, master_password_hash, nonce) values (%s, %s, %s, %s, %s);", (userid, username, private_key, master_password_hash, nonce))

    print("User creation successful!")

def login(cursor):
    username = input("Enter username: ")
    password = input("Enter password: ")

    cursor.execute("select master_password_hash from users where username=%s", (username, ))

    x = cursor.fetchall()

    if len(x) <= 0:
        print("No user by this name.")
        return (False, -1)

    psw_hash = x[0][0]

    tmp_master_key = hash_without_salt(password.encode("utf-8"))
    tmp_psw_hash = hash_with_salt(tmp_master_key, password.encode("utf-8"))

    if psw_hash == tmp_psw_hash:
        print("Successful Login!")

        cursor.execute("select userid from users where username=%s", (username, ))

        userid = cursor.fetchall()[0][0]

        return (True, get_user_vault_key(cursor, username, password))

    print("Wrong password or username, try again")
    return (False, -1)

def get_user_vault_key(cursor, username, password):
    # get master key and nonce and private key
    cursor.execute("select private_key, master_password_hash, nonce, userid from users where username=%s", (username, ))

    x = cursor.fetchall()[0]

    private_key = x[0]
    master_password_hash = x[1]
    nonce = x[2]
    userid = x[3]

    master_key = hash_without_salt(password.encode("utf-8"))

    # retrieve vault key
    aes = AESGCM(master_key)
    vault_key = aes.decrypt(nonce, private_key, None)

    return [userid, vault_key]
