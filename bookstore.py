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
    import urllib.request # Used for URL encoding
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
    db.execute("CREATE TABLE IF NOT EXISTS users (name VARCHAR(255), email VARCHAR(255), phone_number VARCHAR(255), username VARCHAR(255))")
    db.execute("CREATE TABLE IF NOT EXISTS auth (username VARCHAR(255), passhash LONGTEXT)") 
    db.execute("CREATE TABLE IF NOT EXISTS inventory (isbn INT, isbn13 INT, title LONGTEXT, synopsis LONGTEXT, publisher LONGTEXT, authors LONGTEXT, date_published DATE, language CHAR(2), price FLOAT, pages INT, avg_rating FLOAT)") 
    db.execute("CREATE TABLE IF NOT EXISTS transactions (receipt_no INT UNIQUE NOT NULL AUTOINCREMENT, order_date DATE, username VARCHAR(255), isbn CHAR(10), total_price FLOAT)")
    db.execute("CREATE TABLE IF NOT EXISTS cart (username VARCHAR(255), isbn CHAR(10))")
    cdb.commit()
except:
    sys.exit("Unable to setup database")

try:
    print("Adding content to database...")
    url = "https://raw.githubusercontent.com/asmaparker/pageturnerr/main/books.csv?token=GHSAT0AAAAAACU2SZQM3LQTJYCB566BUQZYZVOQEYQ"
    with requests.get(url, stream=True) as r:
        lines = (line.decode('utf-8') for line in r.iter_lines())
        for row in csv.reader(lines):
            if row[9] != '0.00':
                db.execute("INSERT INTO inventory VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
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

def luhn(ccn): # Check if the credit card number entered is correct
    c = [int(x) for x in str(ccn)[::-2]]
    u2 = [(2*int(y))//10+(2*int(y)) % 10 for y in str(ccn)[-2::-2]]
    return sum(c+u2) % 10 == 0


def list_info(isbn):
    db.execute("SELECT isbn,isbn13,title,synopsis,publisher,authors,date_published,language,price,pages,avg_rating FROM inventory WHERE isbn = {isbn}".format(isbn=isbn))
    rs = db.fetchall()

    print(termcolor.colored(rs[0][2], 'cyan', attrs=["bold", "underline"]))
    print(termcolor.colored("Author:", 'cyan'), rs[0][5])
    print(termcolor.colored("Average Rating:", 'cyan'), rs[0][10])
    print(termcolor.colored("Synopsis:", 'cyan'), rs[0][3])
    print(termcolor.colored("Price:", 'cyan'), rs[0][8])
    print(termcolor.colored("Pages:", 'cyan'), rs[0][9])
    print(termcolor.colored("Publisher:", 'cyan'), rs[0][4])
    print(termcolor.colored("Date Published:", 'cyan'), rs[0][6])
    print(termcolor.colored("Language:", 'cyan'), rs[0][7])
    print(termcolor.colored("ISBNs:", 'cyan'), rs[0][0], rs[0][1])
    print()

def search_isbn(isbn):
    db.execute("SELECT isbn FROM inventory WHERE isbn = {}".format(isbn))
    rs = db.fetchall()
    if len(rs) == 0:
        return False
    else:
        return rs[0][0]

def search_title(title):
    db.execute("SELECT isbn, title FROM inventory WHERE title LIKE %{}% LIMIT 10".format(title))
    rs = db.fetchall()
    if len(rs) == 0:
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            if ch <= 9 and ch >= 1:
                return rs[ch-1][0]
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
        

def search_publisher(publisher):
    db.execute("SELECT isbn, title FROM inventory WHERE publisher LIKE %{}% LIMIT 10".format(publisher))
    rs = db.fetchall()
    if len(rs) == 0:
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            if ch <= 9 and ch >= 1:
                return rs[ch-1][0]
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))

def search_author(author):
    db.execute("SELECT isbn, title FROM inventory WHERE authors LIKE %{}% LIMIT 10".format(author))
    rs = db.fetchall()
    if len(rs) == 0:
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            if ch <= 9 and ch >= 1:
                return rs[ch-1][0]
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))

def search_ratings(ratings):
    db.execute("SELECT isbn, title FROM inventory WHERE avg_rating BETWEEN {} AND {} LIMIT 10".format(ratings, ratings+1))
    rs = db.fetchall()
    if len(rs) == 0:
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            if ch <= 9 and ch >= 1:
                return rs[ch-1][0]
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))

def search_price(maxprice, minprice):
    db.execute("SELECT isbn, title FROM inventory WHERE price BETWEEN {} AND {} LIMIT 10".format(minprice, maxprice))
    rs = db.fetchall()
    if len(rs) == 0:
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            if ch <= 9 and ch >= 1:
                return rs[ch-1][0]
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))

def search_yearofpublishing():
    year = input("Enter the year of publishing: ")
    db.execute("SELECT isbn, title FROM inventory WHERE year(date_published) = {} LIMIT 10".format(year))
    rs = db.fetchall()
    if len(rs) == 0:
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            if ch <= 9 and ch >= 1:
                return rs[ch-1][0]
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))


def cart(): 
    print("Your cart:")
    db.execute("SELECT DISTINCT isbn FROM cart WHERE username = %s", (login_username,))
    rs = db.fetchall()
    if len(rs) == 0:
        print("Your cart is empty!")
        print()
        return

    for i in rs:
        db.execute("SELECT title, price FROM inventory WHERE isbn = %s", (i[0],))
        rs2 = db.fetchall()
        print("Title:", rs2[0][0])
        print("Price:", rs2[0][1])
        print()

    print("1. Remove item from cart")
    print("2. Checkout")
    print("0. Go back")
    ch = int(input("Enter your choice: "))
    if ch == 1:
        isbn = input("Enter the index of the book you want to remove: ")
        db.execute("DELETE FROM cart WHERE username = %s AND isbn = %s", (login_username, isbn))
        cdb.commit()
        print("Item removed from cart!")
        print()
    elif ch == 2:
        total_price = 0
        for i in rs:
            db.execute("SELECT price FROM inventory WHERE isbn = {}".format(i[0]))
            rs2 = db.fetchall()
            total_price += rs2[0][0]
        db.execute("INSERT INTO transactions (order_date, username, isbn, total_price) VALUES(%s, %s, %s, %s)", (datetime.datetime.now(), login_username, i[0], total_price))
        cdb.commit()
        print("Order placed successfully!")
        print()
    elif ch == 0:
        return
    
