# Book Store

import os
import sys

# Check whether the OS is Linux/MacOS or Windows
if os.name == "posix":
    # Clear the screen
    os.system("sudo service mysql start")
    os.system("clear")
else:
    # Clear the screen
    os.system("cls")

print("PAGE TURNER")

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
    os.system("pip3 install -qqq --disable-pip-version-check --no-cache-dir --no-color --no-warn-conflicts --user --no-python-version-warning --no-input --no-warn-script-location argon2-cffi")
    os.system("pip3 install -qqq --disable-pip-version-check --no-cache-dir --no-color --no-warn-conflicts --user --no-python-version-warning --no-input --no-warn-script-location termcolor")
    os.system("pip3 install -qqq --disable-pip-version-check --no-cache-dir --no-color --no-warn-conflicts --user --no-python-version-warning --no-input --no-warn-script-location groq")
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
    from getpass import getpass  # Mask passwords while they are being inputted
    from groq import Groq # AI Assistant
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
    db.execute("CREATE TABLE IF NOT EXISTS inventory (isbn CHAR(10), isbn13 CHAR(13), title LONGTEXT, synopsis LONGTEXT, publisher LONGTEXT, authors LONGTEXT, date_published DATE, language CHAR(2), price FLOAT, pages INT)") 
    db.execute("CREATE TABLE IF NOT EXISTS transactions (receipt_no INT UNIQUE NOT NULL AUTO_INCREMENT, order_date DATE, username VARCHAR(255), isbn CHAR(10), total_price FLOAT)")
    db.execute("CREATE TABLE IF NOT EXISTS cart (username VARCHAR(255), isbn CHAR(10))")
    cdb.commit()
except:
    sys.exit("Unable to setup database")

try:
    print("Adding content to database...")
    url = "https://raw.githubusercontent.com/asmaparker/pageturnerr/main/books.csv"
    # db.execute("DELETE FROM inventory")
    # cdb.commit()
    with requests.get(url=url, stream=True, headers={'Cache-Control': 'no-cache'}) as r:
        lines = (line.decode('utf-8') for line in r.iter_lines())
        next(lines)
        for row in csv.reader(lines, delimiter='|'):
            db.execute("INSERT IGNORE INTO inventory VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
            cdb.commit()
except IndexError:
    pass
except:
    sys.exit("Fatal error occurred! Information text is unavailable.")

def clear():
    if os.name == "posix":
        # Clear the screen
        os.system("clear")  
    else:
        # Clear the screen
        os.system("cls")

login_status = False  # Check whether the user is logged in or not

def pass_hasher(password):  # Hash a given password
    return argon2.PasswordHasher().hash(str(password))


def pass_verify(hash, inputpass):  # Verify that an inputted password and the hash are similar
    return argon2.PasswordHasher().verify(hash=hash, password=str(inputpass))

def get_book_info_external(isbn):
    # Use the ISBNDB API to get the price of books and store it in 
    API_KEY = ""
    url = f'https://api2.isbndb.com/book/{isbn}'
    headers = {'Authorization': API_KEY}
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        isbn = data.get("book", {}).get("isbn10", "")
        isbn13 = data.get("book", {}).get("isbn13", "")
        title = data.get("book", {}).get("title_long", "")
        synopsis = data.get("book", {}).get("synopsis", "")
        publisher = data.get("book", {}).get("publisher", "")
        authors = data.get("book", {}).get("authors", [])
        date_published = data.get("book", {}).get("date_published", "")
        language = data.get("book", {}).get("language", "")
        msrp = data.get("book", {}).get("msrp", 0.0)
        pages = data.get("book", {}).get("pages", 0)
        list_info(isbn, isbn13, title, synopsis, publisher, authors, date_published, language, msrp, pages)
    if response.status_code == 403:
        print("API rate limit exceeded. Waiting for 30 seconds...")
        time.sleep(30)
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
    global login_status
    global login_username

    name = input("Enter your full name: ")
    email = input("Enter your email: ")
    phone_number = input("Enter your phone number in international format: ")
    username = input("Enter your username: ")
    password = getpass(prompt="Enter your password: ")  # Mask the password while it's being inputted
    passhash = pass_hasher(password=password)  # Hash the password
   
    # Check whether username already exists
    if check_existing_username(username=username) == False:
        register_customer()

    db.execute("INSERT INTO users VALUES(%s, %s, %s, %s)",
            (name, email, phone_number, username))
    cdb.commit()

    db.execute("INSERT INTO auth VALUES(%s, %s)", (username, passhash))
    cdb.commit()

    login_username = username
    login_status = True
    clear()  # Clear the terminal window to remove any personal data

    print("Registration successful!")
    print("Hello,", name + "!" "\n")
    main()  # Go back to the main menu

def login():  # Log in the user
    global login_status
    global login_username
    login_username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    db.execute("SELECT * FROM auth")
    rs = db.fetchall()

    if len(rs) == 0:
        sys.exit("Username doesn't exist!")

    while True:
        try:
            c = pass_verify(hash=rs[0][1], inputpass=password)
        except argon2.exceptions.VerifyMismatchError:
            sys.exit("Incorrect password!")  # Exit if password is incorrect

        if rs[0][0] == login_username and c == True:
            name = db.execute("SELECT name FROM users WHERE username = '{}'".format(login_username))
            name = db.fetchall()[0][0]
            login_status = True  # Set login status to True
            clear()  # Clear terminal to remove personal information
            print("Login successful!")
            print("Hello,", name + "!" "\n")
            return login_status
        
        else:
            login_status = False
            sys.exit("Unknown error occurred!")
        
def logout():  # Log out and exit the program
    global login_status
    global login_username
    login_status = False
    login_username = None
    print("Thank You for using Page Turner!")
    sys.exit("Successfully logged out!")

def luhn(ccn): # Check if the credit card number entered is correct
    c = [int(x) for x in str(ccn)[::-2]]
    u2 = [(2*int(y))//10+(2*int(y)) % 10 for y in str(ccn)[-2::-2]]
    return sum(c+u2) % 10 == 0

def list_info(isbn, isbn13 = None, title = None, synopsis = None, publisher = None, authors = None, date_published = None, language = None, price = None, pages = None):
    db.execute("SELECT isbn,isbn13,title,synopsis,publisher,authors,date_published,language,price,pages FROM inventory WHERE isbn = '{isbn}'".format(isbn=isbn))
    rs = db.fetchall()
    # Make a string for authors that will iterate through all authors and add them to the string
    print(termcolor.colored(rs[0][2], 'cyan', attrs=["bold", "underline"]))
    print(termcolor.colored("Author(s):", 'cyan'), rs[0][5])
    print(termcolor.colored("Synopsis:", 'cyan'), rs[0][3])
    print(termcolor.colored("Price: AED", 'cyan'), rs[0][8])
    print(termcolor.colored("Pages:", 'cyan'), rs[0][9])
    print(termcolor.colored("Publisher:", 'cyan'), rs[0][4])
    print(termcolor.colored("Date Published:", 'cyan'), rs[0][6])
    print(termcolor.colored("Language:", 'cyan'), rs[0][7])
    print(termcolor.colored("ISBNs:", 'cyan'), rs[0][0], rs[0][1])
    print()
    print("1. Add to cart")
    print("2. Buy now")
    print("3. Get AI suggestions")
    print("0. Go back")

    ch = int(input("Enter your choice: "))
    if ch == 1:
        db.execute("INSERT IGNORE INTO cart VALUES('{}', '{}')".format(login_username, isbn))
        cdb.commit()
        print("Item added to cart!")
        print()
    elif ch == 2:
        # TODO
        print()
    elif ch == 3:
        print(termcolor.colored(ai_suggestions(rs[0][2], rs[0][3], str(rs[0][6])[0:3], rs[0][5], rs[0][9]), "yellow", attrs=["blink"]))
        # Print AI Warning
        print(termcolor.colored("Warning: The AI suggestions are generated by an AI model and may not be accurate. Please verify the suggestions before making a purchase.", "red", attrs=["bold"]))
        print()
    elif ch == 0:
        return
    
def ai_suggestions(title, synopsis, year, author, pages):
    client = Groq(api_key="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")
    completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are a helpful assistant, who informs people about similar books that they would be interested to read"}, {"role": "user", "content": f"The book is {title}. The synopsis of the book is {synopsis}. It was released in {year}. The authors of the book is/are {author}, and the book is {pages} pages long. Suggest three books similar to this one. Do not format the output (just give a plaintext response)."}])
    return completion.choices[0].message.content

def search():
    print()
    print("Search for a book")
    print("1. Search by ISBN")  # Search by ISBN
    print("2. Search by title")  # Search by title  
    print("3. Search by publisher")  # Search by publisher  
    print("4. Search by author")  # Search by author    
    print("5. Search by price")  # Search by price  
    print("6. Search by year of publishing")  # Search by year of publishing    
    print("0. Go back")  # Go back to the main menu 

    ch = int(input("Enter your choice: "))  # Input the choice
    if ch == 1:  # If the choice is 1
        isbn = input("Enter the ISBN of the book: ")  # Input the ISBN of the book
        if search_isbn(isbn) == False:
            print("Book not found!")
            print()
        else:
            list_info(isbn)

    elif ch == 2:  # If the choice is 2
        title = input("Enter the title of the book: ")  # Input the title of the book
        isbn = search_title(title)
        if  isbn == False:
            print("Book not found!")
            print()
        else:
            list_info(isbn)

    elif ch == 3:  # If the choice is 3
        publisher = input("Enter the publisher of the book: ")  # Input the publisher of the book
        isbn = search_publisher(publisher)
        if isbn == False:
            print("Book not found!")
            print()
        else:
            list_info(isbn)

    elif ch == 4:  # If the choice is 4
        author = input("Enter the author of the book: ")  # Input the author of the book
        if search_author(author) == False:
            print("Book not found!")    

        else:   
            isbn = search_author(author)
            list_info(isbn)
           
    elif ch == 5:  # If the choice is 5
        maxprice = input("Enter the maximum price of the book: ")   
        minprice = input("Enter the minimum price of the book: ")
        if search_price(maxprice, minprice) == False:
            print("Book not found!")
            print()
        else:
            isbn = search_price(maxprice, minprice)
            list_info(isbn)
            
    elif ch == 6:  # If the choice is 6
        year = input("Enter the year of publishing of the book: ")   
        if search_yearofpublishing(year) == False:
            print("Book not found!")
            print()
        else:
            isbn = search_yearofpublishing(year)
            list_info(isbn)
            
    elif ch == 0:  # If the choice is 0
        return
    
def search_isbn(isbn):
    db.execute("SELECT isbn FROM inventory WHERE isbn = '{}'".format(isbn))
    rs = db.fetchall()
    if len(rs) == 0:
        print("Book not found in database! Searching online for book info...")
        add = get_book_info_external(isbn)
        if add == True:
            search_isbn(isbn)
        else:
            return False
    else:
        return rs[0][0]

def search_title(title):
    db.execute("SELECT isbn, title FROM inventory WHERE title LIKE '%{}%' LIMIT 10".format(title))
    rs = db.fetchall()
    if len(rs) == 0:
        print("Books not found! Try searching by ISBN or try a different title.")    
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))

        while True:
            ch = int(input("Enter the number of the book you would like to select: "))
            if ch <= 10 and ch >= 1:
                return rs[ch-1][0]
            elif ch == 0:
                return
            else:
                print(termcolor.colored("Error! Choose a number from the list."), "red")
            
def search_publisher(publisher):
    db.execute("SELECT isbn, title FROM inventory WHERE publisher LIKE '%{}%' LIMIT 10".format(publisher))
    rs = db.fetchall()
    if len(rs) == 0:
        print("Books not found! Try searching by ISBN or try a different publisher.")    
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
                if ch <= 10 and ch >= 1:
                  return rs[ch-1][0]
                if ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))

def search_author(author):
    db.execute("SELECT isbn, title FROM inventory WHERE authors LIKE '%{}%' LIMIT 10".format(author))
    rs = db.fetchall()
    if len(rs) == 0:
        print("Books not found! Try searching by ISBN or try a different author.")    
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
                if ch <= 10 and ch >= 1:
                  return rs[ch-1][0]
                if ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))

def search_price(maxprice, minprice):
    db.execute("SELECT isbn, title FROM inventory WHERE price BETWEEN '{}' AND '{}' LIMIT 10".format(minprice, maxprice))
    rs = db.fetchall()
    if len(rs) == 0:
        print("No books found within the given price range!")
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
                if ch <= 10 and ch >= 1:
                  return rs[ch-1][0]
                if ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))

def search_yearofpublishing(year):
    db.execute("SELECT isbn, title FROM inventory WHERE year(date_published) = '{}' LIMIT 10".format(year))
    rs = db.fetchall()
    if len(rs) == 0:
        print("No books found with the given year of publishing!")
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i[1]))
        
        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: "))
                if ch <= 10 and ch >= 1:
                  return rs[ch-1][0]
                if ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))
            else:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))

def cart(): 
    print("Your cart:")
    db.execute("SELECT DISTINCT isbn FROM cart WHERE username = '{}'".format(login_username))
    rs = db.fetchall()
    if len(rs) == 0:
        print("Your cart is empty!")
        print()
        return

    j = 0
    for i in rs:
        j += 1
        db.execute("SELECT title FROM inventory WHERE isbn = '{}'".format(i[0]))
        rs2 = db.fetchall()
        print("{}. {}".format(j, rs2[0][0]))

    print("1. Remove item from cart")
    print("2. Empty Cart")
    print("3. Checkout")
    print("0. Go back")
    ch = int(input("Enter your choice: "))
    if ch == 1:
        ind = int(input("Enter the index of the book you want to remove: "))
        isbn = rs[ind-1][0]
        db.execute("DELETE FROM cart WHERE username = '{}' AND isbn = '{}'".format(login_username, isbn))
        cdb.commit()
        print("Item removed from cart!")
        print()

    elif ch == 2:
        db.execute("DELETE FROM cart WHERE username = '{}'".format(login_username))
        cdb.commit()
        print("Cart emptied!")
        print()

    elif ch == 3:
        for i in rs:
            db.execute("SELECT price FROM inventory WHERE isbn = '{}'".format(i[0]))
            rs2 = db.fetchall()
            db.execute("INSERT INTO transactions (order_date, username, isbn, total_price) VALUES('{}', '{}', '{}', '{}')".format(datetime.datetime.now(), login_username, i[0], rs2[0][0]))
            cdb.commit()
        print("Order placed successfully!")
        print()
    elif ch == 0:
        return

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
            db.execute("UPDATE users SET name = %s WHERE username = %s", (name, login_username))
            cdb.commit()
            print("Name changed successfully!")
            print()
            break
            
        elif ch == 2:
            email = input("Enter new email: ")
            db.execute("UPDATE users SET email = %s WHERE username = %s", (email, login_username))
            cdb.commit()
            print("Email changed successfully!")
            print()
            break
            
        elif ch == 3:
            phone_number = input("Enter new phone number in international format: ")
            db.execute("UPDATE users SET phone_number = %s WHERE username = %s", (phone_number, login_username))
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
                confirm = getpass("Confirm new password: ")
                if newpass != confirm:
                    print("Passwords don't match!")
                    print()
                    break
                passhash = pass_hasher(newpass)
                db.execute("UPDATE auth SET passhash = %s WHERE username = %s", (passhash, login_username))
                cdb.commit()
                print("Password changed successfully!")
                print()
                break

        elif ch == 0:
            break

def list_bought():
    db.execute("SELECT isbn FROM transactions WHERE username = '{}'".format(login_username))
    rs = db.fetchall()
    if len(rs) == 0:
        print("No books bought yet!")
        print()
        return

    j = 0
    for i in rs:
        j += 1
        db.execute("SELECT title FROM inventory WHERE isbn = '{}'".format(i[0]))
        rs2 = db.fetchall()
        print("{}. {}".format(j, rs2[0][0]))
    print()

def delete_account():
    ch = input("Are you sure you want to delete your account? (y/n): ")
    if ch.lower() == 'y':
        # Prompt for password as confirmation
        password = getpass("Enter your password to confirm account deletion: ")
        db.execute("SELECT passhash FROM auth WHERE username = '{}'".format(login_username))
        rs = db.fetchall()
        while True:
            try:
                pass_check = pass_verify(rs[0][0], password)  # Verify if current password matches the hash existing in the database
                
            except argon2.exceptions.VerifyMismatchError:
                print(termcolor.colored("Incorrect password!", "red"))

            if pass_check == True:
                db.execute("DELETE FROM users WHERE username = '{}'".format(login_username))
                cdb.commit()
                db.execute("DELETE FROM auth WHERE username = '{}'".format(login_username))
                cdb.commit()
                db.execute("DELETE FROM cart WHERE username = '{}'".format(login_username))
                cdb.commit()
                print("Account deleted successfully!")
                kill()
    else:
        return
    
def kill():
    sys.exit("Thank you for using Page Turner!")

def start():
    while True:
        clear()
        print("Welcome to Page Turner!")
        print("1. Login")
        print("2. Register")
        print("0. Exit")
        ch = int(input("Enter your choice: "))
        if ch == 1:
            if login():
                main()
        elif ch == 2:
            register_customer()
        elif ch == 0:
            kill()
        else:
            print("Invalid choice! Please try again.")

def main():
    while True:
        print("1. Search for a book")
        print("2. Account Management")
        print("3. View cart")
        print("4. View bought books")
        print("5. Delete account")
        print("0. Logout")
        ch = int(input("Enter your choice: "))
        if ch == 1:
            search()
        elif ch == 2:
            edit_customer()
        elif ch == 3:
            cart()
        elif ch == 4:
            list_bought()
        elif ch == 5:
            delete_account()
        elif ch == 0:
            logout()

if __name__ == "__main__":
    start()
