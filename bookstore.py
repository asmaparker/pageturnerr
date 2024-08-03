# Book Store

import os
import sys

# Check whether the OS is Linux/MacOS or Windows
if os.name == "posix":
    # Clear the screen
    os.system("clear")  
else:
    # Clear the screen
    os.system("cls")

print("BOOK STORE")

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

if sys.version_info[0] < 3:
    print("Please download Python3 from the link below")
    print("https://www.python.org/downloads/")
    input("Press any key to exit!")
    sys.exit("Python3 not installed")

try:  # Install all required modules
    print("Installing required dependencies...")
    os.system("pip3 install -qqq --disable-pip-version-check --no-cache-dir --no-color --no-warn-conflicts --user --no-python-version-warning --no-input --no-warn-script-location mysql-connector-python")
    os.system("pip3 install -qqq --disable-pip-version-check --no-cache-dir --no-color --no-warn-conflicts --user --no-python-version-warning --no-input --no-warn-script-location prettytable")
    os.system("pip3 install -qqq --disable-pip-version-check --no-cache-dir --no-color --no-warn-conflicts --user --no-python-version-warning --no-input --no-warn-script-location argon2-cffi")
    os.system("pip3 install -qqq --disable-pip-version-check --no-cache-dir --no-color --no-warn-conflicts --user --no-python-version-warning --no-input --no-warn-script-location termcolor")
except:
    sys.exit("Unable to install required dependencies!")  # Exit if modules cannot be installed

try:
    print("Importing modules")
    import argon2  # Password hashing module
    import csv # To work with CSV files
    import datetime  # Get current date and time 
    import requests
    import time  # Used for debugging purposes
    import termcolor  # Color the output in the terminal
    import random  # Used for generation of OTPs
    import urllib # Used for URL encoding
    from getpass import getpass  # Mask passwords while they are being inputted
    from mysql.connector import connect  # Connect to MySQL Server
except:
    sys.exit("Unable to import required dependencies")  # Exit if modules cannot be imported

try:
    print("Connecting to database...")
    cdb = connect(host="localhost", user="asma", password="mysql")  # Connecting to the MySQL server
    db = cdb.cursor()  # Creating the cursor for the MySQL Server
    db.execute("CREATE DATABASE IF NOT EXISTS bookstore")  # Create the database if it doesn't exist
    cdb.commit()  # Save changes
    db.close()  # Close the cursor and ensure that the cursor object has no reference to its original connection object
    cdb.close()  # Close the connection to the server

    cdb = connect(host="localhost", user="asma", password="mysql", database="bookstore")  # Reopen connection to the MySQL server
    db = cdb.cursor()  # Creating the cursor for the MySQL Server
except:
    sys.exit("Unable to connect to the database")

try:
    print("Setting up database")
    db.execute("CREATE TABLE IF NOT EXISTS ")
except:
    sys.exit("Unable to setup database")

try:
    print("Adding content to database...")
    url = "https://raw.githubusercontent.com/asmaparker/CBSEProj/main/books.csv"
    response = urllib.urlopen(url)
    # f = open("data.csv", "r")
    reader = csv.reader(response)
    for row in reader:
        db.execute("INSERT INTO books (title, author, price, quantity) VALUES (%s, %s, %s, %s)", (row[0], row[1], row[2], row[3]))
        cdb.commit()
except:
    sys.exit("Fatal error occurred! Information text is unavailable.")

if os.name == "posix":
    # Clear the screen
    os.system("clear")  
else:
    # Clear the screen
    os.system("cls")


login_status = False  # Check whether the user is logged in or not

def pass_hasher(password):  # Hash a given password
    return argon2.PasswordHasher().hash(password)


def pass_verify(hash, inputpass):  # Verify that an inputted password and the hash are similar
    return argon2.PasswordHasher().verify(hash, inputpass)

def get_book_info_external(isbn):
    # Use the ISBNDB API to get the price of books and store it in 
    API_KEY = ""
    url = f'https://api2.isbndb.com/book/{isbn}'
    headers = {'Authorization': API_KEY}
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        msrp = data['book']['msrp']
        return msrp
    if response.status_code == 403:
        print("API rate limit exceeded. Waiting for 1 minute...")
        time.sleep(60)
        return get_book_info_external(isbn)
    else:
        return 404

def check_existing_username(username):
    # Check whether username already exists
    db.execute("SELECT username FROM users")
    rs = db.fetchall()
    for i in rs:
        if i[0] == username:
            print("Username already exists!")
            return False
    return True

def register_customer():  # Register a new customer
    name = input("Enter your full name: ")
    email = input(prompt="Enter your email: ")
    phone_number = input("Enter your phone number in international format: ")
    username = input("Enter your username: ")
    password = getpass(prompt="Enter your password: ")  # Mask the password while it's being inputted
    passhash = pass_hasher(password=password)  # Hash the password
   
    # Check whether username already exists
    if check_existing_username(username=username) == False:
        register_customer()

    db.execute("INSERT INTO users (name, email, phone_number, username) VALUES(%s, %s, %s, %s)",
            (name, email, phone_number, username))
    cdb.commit()

    db.execute("INSERT INTO auth VALUES(%s, %s)", (username, passhash))
    cdb.commit()

    os.system("cls")  # Clear the terminal window to remove any personal data
    main()  # Go back to the main menu

def login():  # Log in the user
    global login_status
    global login_username
    login_username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    db.execute("SELECT username, passhash FROM auth")
    rs = db.fetchall()

    if len(rs) == 0:
        sys.exit("Username doesn't exist!")

    while True:
        for i in rs:
            try:
                c = pass_verify(i[1], password)
            except argon2.exceptions.VerifyMismatchError:
                sys.exit("Incorrect password!")  # Exit if password is incorrect

            if i[0] == login_username and c == True:
                login_status = True  # Set login status to True
                os.system('cls')  # Clear terminal to remove personal information
                print("Login successful!")
                print("Hello,", login_username + "!" "\n")
                return login_status
            elif i[0] != login_username or c == False:
                login_status = False
                sys.exit("Username doesn't exist!")
            else:
                login_status = False
                sys.exit("Unknown error occurred!")
        break

def logout():  # Log out and exit the program
    global login_status
    global login_username
    login_status = False
    login_username = None
    print("Thank You for using Book Store!")
    sys.exit("Successfully logged out!")

def edit_customer():  # Edit customer details
    print()
    print("1. Change name")
    print("2. Change email")
    print("3. Change phone number")
    print("4. Change password")
    
    ch = int(input("Enter your choice: "))
    
    while True:
        if ch == 1:
            name = input("Enter new name: ")
            db.execute("UPDATE customers SET name = %s WHERE username = %s", (name, login_username))
            cdb.commit()
            print("Name changed successfully!")
            print()
            break
            
        elif ch == 2:
            email = input("Enter new email: ")
            db.execute("UPDATE customers SET email = %s WHERE username = %s", (email, login_username))
            cdb.commit()
            print("Email changed successfully!")
            print()
            break
            
        elif ch == 3:
            phone_number = input("Enter new phone number in international format: ")
            db.execute("UPDATE customers SET phone_number = %s WHERE username = %s", (phone_number, login_username))
            cdb.commit()
            print("Phone number changed successfully!")
            print()
            break
        
        elif ch == 4:
            password = getpass("Enter your current password: ")
            db.execute("SELECT passhash FROM auth WHERE username = %s", (login_username,))
            rs = db.fetchall()[0][0]
            try:
                pass_check = pass_verify(rs, password)  # Verify if current password matches the hash existing in the database
            except argon2.exceptions.VerifyMismatchError:
                sys.exit(status="Incorrect password!")  # Exit the program if the password entered was incorrect
            
            if pass_check == True:
                newpass = getpass("Enter new password: ")
                passhash = pass_hasher(newpass)
                db.execute("UPDATE auth SET passhash = %s WHERE username = %s", (passhash, login_username))
                cdb.commit()
                print("Password changed successfully!")
                print()
                break

        elif ch == 0:
            break
