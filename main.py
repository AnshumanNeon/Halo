import os
from dotenv import load_dotenv
import mysql.connector
from user import *
from password import *
import sys

LOGGED = False
QUIT_FLAG = False

load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

connector = mysql.connector.connect(
    host = "localhost",
    username = MYSQL_USER,
    password = MYSQL_PASSWORD
)

cursor = connector.cursor()

cursor.execute("create database if not exists halo;")
cursor.execute("use halo;")
cursor.execute("create table if not exists users (userid varchar(200) primary key, username varchar(250), private_key varbinary(200), master_password_hash varbinary(200), nonce varbinary(200))")
cursor.execute("create table if not exists passwords (userid varchar(200), foreign key (userid) references users(userid), protected_password varbinary(300), label varchar(250), description varchar(500), password_hash varbinary(300), nonce1 varbinary(200), nonce2 varbinary(200))")

data = []

def entry_options():
    global LOGGED, data, QUIT_FLAG
    
    print("Welcome to the Halo Password Manager\n")
    print("------------------------------------\n")
    print("Options:")
    print("1) Login")
    print("2) Create a New Account")
    print("3) Quit\n")
    print("------------------------------------\n")
    
    choice = int(input(">>> "))

    if choice == 1:
        x = login(cursor)
        LOGGED = x[0]
        data = x[1]
    elif choice == 2:
        create_user(cursor)
        connector.commit()
    elif choice == 3:
        QUIT_FLAG = True
    else:
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
    elif choice == 2:
        label = input("Enter the name/label for your password: ")
        get_password(cursor, data[1], label)
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
        elif confirm != "y" and confirm != "n":
            print("please enter a valid choice. quitting deletion process...")
    elif choice == 5:
        confirm = input("All your saved passwords will be deleted. Are you sure you want to delete this user? (y/n) ")

        if confirm == "y":
            cursor.execute("delete from passwords where userid=%s", (data[0],))
            connector.commit()
            cursor.execute("delete from users where userid=%s", (data[0],))
            connector.commit()
            LOGGED = False
        elif confirm != "y" and confirm != "n":
            print("please enter a valid choice. quitting account deletion process...")
    elif choice == 6:
        LOGGED = False
            
while True:
    if not LOGGED and QUIT_FLAG:
        sys.exit(0)
    elif not LOGGED and not QUIT_FLAG:
        entry_options()
        
    if LOGGED:
        usage_options()
    elif not LOGGED:
        data = []
