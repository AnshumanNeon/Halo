import os
from dotenv import load_dotenv
import mysql.connector
from user import *
from password import *
import sys

# create flags to check if a user is logged in (LOGGED) and if the user wants
# to quit (QUIT_FLAG)
LOGGED = False
QUIT_FLAG = False

# load the ".env" file
load_dotenv()

# get the mysql username and password from the ".env" file
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

# create a mysql connector
connector = mysql.connector.connect(
    host = "localhost",
    username = MYSQL_USER,
    password = MYSQL_PASSWORD
)

# create the cursor for the connector
cursor = connector.cursor()

# execute initialization mysql queries
# create the db (if not exists)
cursor.execute("create database if not exists halo;")

# use the db
cursor.execute("use halo;")

# create the user table (if not exists)
cursor.execute("create table if not exists users (userid varchar(200) primary key, username varchar(250), private_key varbinary(200), master_password_hash varbinary(200), nonce varbinary(200))")

# create the passwords table (if not exists)
cursor.execute("create table if not exists passwords (userid varchar(200), foreign key (userid) references users(userid), protected_password varbinary(300), label varchar(250), description varchar(500), password_hash varbinary(300), nonce1 varbinary(200), nonce2 varbinary(200))")

# create the data list where we store the user details (from get_vault_key
# function) when the user logs in
data = []

def entry_options():
    # get the global flags
    global LOGGED, data, QUIT_FLAG

    # print the tui (terminal user interface)
    print("Welcome to the Halo Password Manager\n")
    print("------------------------------------\n")
    print("Options:")
    print("1) Login")
    print("2) Create a New Account")
    print("3) Quit\n")
    print("------------------------------------\n")

    # ask for input
    choice = int(input(">>> "))

    if choice == 1: # login
        x = login(cursor)

        # update the flags if logged in
        LOGGED = x[0]
        data = x[1]
        
        if input("Continue..."): return
    elif choice == 2: # create a new account
        create_user(cursor)

        # commit the changes to the database when the account is created
        connector.commit()
    elif choice == 3: # quit
        # update the QUIT_FLAG
        QUIT_FLAG = True
    else:             # invalid option
        print("Please enter a valid option.")

def usage_options():
    global LOGGED
    print("Options:\n")
    print("------------------------------------\n")
    print("1) See all passwords")
    print("2) Get Password")
    print("3) Create a New Password")
    print("4) Delete Password")
    print("5) Delete this user")
    print("6) Logout")
    print("------------------------------------\n")

    choice = int(input(">>> "))

    if choice == 1:
        show_all_passwords(cursor, data[0])
        if input("Continue..."): return
    elif choice == 2:
        label = input("Enter the name/label for your password: ")
        get_password(cursor, data[1], label, data[0])
    elif choice == 3:
        label = input("Enter the name/label for your password: ")
        description = input("Enter a description for your password (can be left blank): ")
        create_new_password(cursor, data[1], data[0], label, description)
        connector.commit()
    elif choice == 4:
        label = input("Enter the name/label: ")

        cursor.execute("select * from passwords where label=%s;", (label,))

        h = cursor.fetchall()

        if len(h) <= 0:
            print("Not a valid label. quitting deletion process...")
            return
        
        confirm = input("Are you sure you want to delete the password? (y/n) ")

        if confirm == "y":
            cursor.execute("delete from passwords where label=%s", (label,))
            connector.commit()

            print("Deleted the password successfully.")

            if input("Continue..."): return
        elif confirm != "y" and confirm != "n":
            print("please enter a valid choice. quitting deletion process...")
            if input("Continue..."): return
    elif choice == 5:
        confirm = input("All your saved passwords will be deleted. Are you sure you want to delete this user? (y/n) ")

        if confirm == "y":
            cursor.execute("delete from passwords where userid=%s", (data[0],))
            connector.commit()
            cursor.execute("delete from users where userid=%s", (data[0],))
            connector.commit()
            LOGGED = False

            if input("Continue..."): return
        elif confirm != "y" and confirm != "n":
            print("please enter a valid choice. quitting account deletion process...")

            if input("Continue..."): return

    elif choice == 6:
        LOGGED = False

# run an infinite loop
while True:
    if LOGGED:
        # if the user is logged in then clear the screen and display the usage option
        os.system("clear || cls")
        usage_options()
    elif not LOGGED:
        # if the user is not logged in then keep the data list empty
        data = []
        
        if not LOGGED and QUIT_FLAG:
            # if the user is not logged in and wants to quit, then quit
            sys.exit(0)
        elif not LOGGED and not QUIT_FLAG:
            # if the user is not logged in and does not want to quit, then clear
            # the screen and display the entry options
            os.system("clear || cls")
            entry_options()
