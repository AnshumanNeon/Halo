from hash import *
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import getpass

def create_user(cursor):
    # taking inputs from user such as username and the password (master_password)
    username = input("Enter username: ")
    master_password = getpass.getpass("Enter password: ")

    # create a userid
    userid = int.from_bytes(os.urandom(8))

    # hash the password to get the master key
    master_key = hash_without_salt(master_password.encode("utf-8"))

    # create a vault key
    random_number = os.urandom(32)
    vault_key = hash_without_salt(random_number)

    # encrypt the vault key using the master key.
    # this gets us the private key
    aes = AESGCM(master_key)
    nonce = os.urandom(8)
    private_key = aes.encrypt(nonce, vault_key, None)

    # create a master password hash
    master_password_hash = hash_with_salt(master_key, master_password.encode("utf-8"))

    # enter into the mysql table
    cursor.execute("insert into users (userid, username, private_key, master_password_hash, nonce) values (%s, %s, %s, %s, %s);", (userid, username, private_key, master_password_hash, nonce))

    print("User creation successful!")

    # check for user input to continue and end the operation
    if input("Continue..."): return

def login(cursor):
    # get the username and password from the user
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    # run query to get the master password hash from the table
    cursor.execute("select master_password_hash from users where username=%s", (username, ))

    # get the results
    x = cursor.fetchall()

    # check if results exist or are valid
    if len(x) <= 0:
        print("No user by this name.")
        return (False, -1)

    # get the password hash from the database
    psw_hash = x[0][0]

    # create a new master key and password hash from the password provided
    tmp_master_key = hash_without_salt(password.encode("utf-8"))
    tmp_psw_hash = hash_with_salt(tmp_master_key, password.encode("utf-8"))

    # check if the hash in the table and the hash created are the same.
    # due to the complexity of hashing and encryption, we can be sure that the
    # hashes can only be same if the original strings are the same.
    # Hence if the hashes are the same, then the password must be the same the
    # one entered at the time of account creation.
    # This fulfills the login process
    if psw_hash == tmp_psw_hash:
        print("Successful Login!")

        # run the query to fetch the userid
        cursor.execute("select userid from users where username=%s", (username, ))

        # fetch the userid
        userid = cursor.fetchall()[0][0]

        # return login completion confirmation and a list of user details from
        # the "get_user_vault_key" function
        return (True, get_user_vault_key(cursor, username, password))

    # if the hashes are not same, then the passwords are not same
    print("Wrong password or username, try again")

    # return confirmation for login unsuccessful and return an empty list for details
    return (False, [])

def get_user_vault_key(cursor, username, password):
    # get private key, master password hash, nonce and the userid
    cursor.execute("select private_key, master_password_hash, nonce, userid from users where username=%s", (username, ))

    # fetch the list which consists of the private key, master password hash,
    # nonce and userid
    x = cursor.fetchall()[0]

    # we do not confirm for the existence and validation of the results in this
    # case since the only call to this function is in the "login" function
    # where we have already done validation for the existence of this user.
    # Hence if a user exists, then they must also have a maste password hash,
    # nonce, userid and a private key.

    # fethch the details from the list
    private_key = x[0]
    master_password_hash = x[1]
    nonce = x[2]
    userid = x[3]

    # create the master_key once again from the password provided by the user
    # since we do not store the amster key directly into the database
    master_key = hash_without_salt(password.encode("utf-8"))

    # retrieve vault key by decrypting the private key using the master key
    aes = AESGCM(master_key)
    vault_key = aes.decrypt(nonce, private_key, None)

    # return the userid and the vault key in a list
    return [userid, vault_key]
