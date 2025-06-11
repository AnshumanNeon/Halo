import mysql
import os
from hash import *
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def show_all_passwords(cursor, userid):
    # run a query to get all the labels and descriptions for all passwords for
    # the given user by searching by the userid
    cursor.execute("select label, description from passwords where userid=%s", (userid,))

    # fetch the reults
    x = cursor.fetchall()

    # check the validity of the results
    if len(x) <= 0:
        # if no results are available then that means that the user has not
        # created any passwords for them
        print("No passwords available for your user.")
        
        if input("Continue..."): return
    else:
        # if results are available then display all the results by looping
        # through the list of results and show each tuple which consists of the
        # label and description
        for a in x:
            print("Label = ", a[0])
            print("Description = ", a[1])

def create_new_password(cursor, vault_key, userid, label, description):
    # generate a random 16 digit password and convert it to hex form to get a
    # alphanumeric string which can be used the password
    generated_psw = os.urandom(8).hex()

    # generate a random number and hash it to get the password salt
    t = os.urandom(4)
    psw_salt = hash_without_salt(t)

    # encrypt the password salt using the vault key to get the "password hash"
    aes1 = AESGCM(vault_key)
    nonce1 = os.urandom(8)
    psw_hash = aes1.encrypt(nonce1, psw_salt, None)

    # encrypt the generated password using the password salt to get a
    # "protected password"
    aes2 = AESGCM(psw_salt)
    nonce2 = os.urandom(8)
    protected_password = aes2.encrypt(nonce2, generated_psw.encode("utf-8"), None)

    # run a query to insert the protected password, password hash and the nonces
    cursor.execute("insert into passwords (userid, protected_password, label, description, password_hash, nonce1, nonce2) values (%s, %s, %s, %s, %s, %s, %s)", (userid, protected_password, label, description, psw_hash, nonce1, nonce2))

    print("Password created for your user successfully!!")

    if input("Continue..."): return

def get_password(cursor, vault_key, label, userid):
    # run a query to get the protected password, the password hash and the nonces
    cursor.execute("select protected_password, password_hash, nonce1, nonce2 from passwords where label=%s and userid=%s", (label, userid))

    # get the result list
    x = cursor.fetchall()[0]

    # get the results from the result list
    protected_password = x[0]
    psw_hash = x[1]
    nonce1 = x[2]
    nonce2 = x[3]

    # decrypt the password hash using the vault key to get back the password salt
    aes1 = AESGCM(vault_key)
    psw_salt = aes1.decrypt(nonce1, psw_hash, None)

    # decrypt the protected password using the password salt to get the password
    aes2 = AESGCM(psw_salt)
    password = aes2.decrypt(nonce2, protected_password, None)

    print("Your password is:", password.decode("utf-8"))

    if input("Continue..."): return
