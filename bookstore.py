# Page Turner
# Author: Asma Yaseen Parker

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

print("""
╔═╗┌─┐┌─┐┌─┐╔╦╗┬ ┬┬─┐┌┐┌┌─┐┬─┐
╠═╝├─┤│ ┬├┤  ║ │ │├┬┘│││├┤ ├┬┘
╩  ┴ ┴└─┘└─┘ ╩ └─┘┴└─┘└┘└─┘┴└─
""")

# Ignore all warnings
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

# Check if Python 3 is installed
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
    import csv  # To work with CSV files
    import datetime  # Get current date and time
    import requests  # Used to request data from API, download CSV file
    import time  # Used for debugging purposes
    import termcolor  # Color the output in the terminal
    from getpass import getpass  # Mask passwords while they are being inputted
    from groq import Groq  # AI Assistant
    from mysql.connector import connect  # Connect to MySQL Server
except:
    sys.exit("Unable to import required dependencies")  # Exit if modules cannot be imported

try:
    print("Connecting to database...")
    cdb = connect(host="localhost", user="root", password="root")  # Connecting to the MySQL server
    db = cdb.cursor()  # Creating the cursor for the MySQL Server
    db.execute("CREATE DATABASE IF NOT EXISTS bookstore")  # Create the database if it doesn't exist
    cdb.commit()  # Save changes
    db.close()  # Close the cursor and ensure that the cursor object has no reference to its original connection object
    cdb.close()  # Close the connection to the server

    cdb = connect(host="localhost", user="root", password="root",
                  database="bookstore")  # Reopen connection to the MySQL server
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
    db.execute("DELETE FROM inventory") # Delete all existing data in the inventory table
    cdb.commit()
    try:
        f = open("books.csv", encoding='utf-8') # Open books data
        reader = csv.reader(f, delimiter='|') # Read the CSV file with custom delimiter
        next(reader) # Skip the header row
        for row in reader:
            db.execute("INSERT IGNORE INTO inventory VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])) # Insert the data into the inventory table if it doesn't already exist
            cdb.commit()
    except:
        # If the books data is not available, download it from the GitHub repository
        url = "https://raw.githubusercontent.com/asmaparker/pageturnerr/main/books.csv" 
        with requests.get(url=url, stream=True, headers={'Cache-Control': 'no-cache'}) as r: # Request the data from the URL. Stream the data to avoid memory issues
            lines = (line.decode('utf-8') for line in r.iter_lines()) # Decode the data from the stream
            next(lines) # Skip the header row
            for row in csv.reader(lines, delimiter='|'): # Read the CSV file with custom delimiter
                db.execute("INSERT IGNORE INTO inventory VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
                cdb.commit()
except IndexError: # If the data is missing, skip the row
    pass
except:
    sys.exit("Fatal error occurred! Information text is unavailable.") # If the data is not available, exit the program

login_status = False  # Set login status to not logged in


def clear():  # Clear the terminal window
    if os.name == "posix":
        # Clear the screen
        os.system("clear")
    else:
        # Clear the screen
        os.system("cls")


def kill():  # Exit the program
    sys.exit("Thank you for using Page Turner!")


def check_existing_username(username):  # Check whether username already exists
    db.execute("SELECT username FROM users")
    rs = db.fetchall()
    for i in rs: # Iterate through the usernames in the database
        if i[0] == username:
            print("Username already exists!")
            return False
    return True


def register_customer():  # Register a new customer
    global login_status # Set the login status to global to be used in other functions
    global login_username # Set the login username to global to be used in other functions

    name = input("Enter your full name: ")
    email = input("Enter your email: ")
    phone_number = input("Enter your phone number in international format: ")
    username = input("Enter your username: ")
    password = getpass(prompt="Enter your password: ") # Mask the password while it's being inputted
    passhash = pass_hasher(password=password)  # Hash the password

    # Check whether username already exists
    if check_existing_username(username=username) == False:
        register_customer() # If the username already exists, register the customer again

    db.execute("INSERT INTO users VALUES(%s, %s, %s, %s)",
               (name, email, phone_number, username)) # Insert the user details into the users table
    cdb.commit()

    db.execute("INSERT INTO auth VALUES(%s, %s)", (username, passhash)) # Insert the username and password hash into the auth table
    cdb.commit()

    login_username = username # Set the login username to the username entered
    login_status = True # Set the login status to logged in
    clear()  # Clear the terminal window to remove any personal data

    print("Registration successful!")
    print("Hello,", name + "!" "\n")
    main()  # Go to the main menu


def login():  # Log in the user
    global login_status # Set login status to global to be used in other functions
    global login_username # Set login username to global to be used in other functions
    login_username = input("Enter your username: ")
    password = getpass("Enter your password: ") # Mask the password while it's being inputted
    db.execute("SELECT * FROM auth")
    rs = db.fetchall()

    if check_existing_username(username=login_username) == True: # Check if the username exists 
        sys.exit("Username doesn't exist!")

    while True:
        try:
            c = pass_verify(hash=rs[0][1], inputpass=password) # Verify the password entered
        except argon2.exceptions.VerifyMismatchError:
            sys.exit("Incorrect password!")  # Exit if password is incorrect

        if rs[0][0] == login_username and c == True: # If the username and password are correct
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
    kill()


def pass_hasher(password):  # Hash a given password
    return argon2.PasswordHasher().hash(str(password))


def pass_verify(hash, inputpass):  # Verify that an inputted password and the hash are similar
    return argon2.PasswordHasher().verify(hash=hash, password=str(inputpass))


def search():  # Search for a book
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
        isbn = search_isbn(isbn) # Search for the book by ISBN
        if isbn == False: # If the book is not found
            print("Book not found!")
            print()
        else:
            list_info(isbn) # List the information of the book

    elif ch == 2:  # If the choice is 2
        title = input("Enter the title of the book: ")  # Input the title of the book
        isbn = search_title(title) # Search for the book by title
        if isbn == False: # If the book is not found
            print("Book not found!")
            print()
        else:
            list_info(isbn) # List the information of the book

    elif ch == 3:  # If the choice is 3
        publisher = input("Enter the publisher of the book: ")  # Input the publisher of the book
        isbn = search_publisher(publisher) # Search for the book by publisher
        if isbn == False: # If the book is not found
            print("Book not found!")
            print()
        else:
            list_info(isbn) # List the information of the book

    elif ch == 4:  # If the choice is 4
        author = input("Enter the author of the book: ")  # Input the author of the book
        isbn = search_author(author) # Search for the book by author
        if isbn == False: # If the book is not found
            print("Book not found!")
            print()
        else:
            list_info(isbn) # List the information of the book

    elif ch == 5:  # If the choice is 5
        maxprice = input("Enter the maximum price of the book: ")  # Input the maximum price of the book
        minprice = input("Enter the minimum price of the book: ")  # Input the minimum price of the book
        maxprice = max(maxprice, minprice) # Set the maximum price to the maximum of the two prices
        minprice = min(maxprice, minprice) # Set the minimum price to the minimum of the two prices
        isbn = search_price(maxprice, minprice) # Search for the book by price
        if isbn == False: # If the book is not found
            print("Book not found!")
            print()
        else:
            list_info(isbn) # List the information of the book

    elif ch == 6:  # If the choice is 6
        year = input("Enter the year of publishing of the book: ") # Input the year of publishing of the book
        isbn = search_yearofpublishing(year) # Search for the book by year of publishing
        if isbn == False: # If the book is not found
            print("Book not found!")
            print()
        else:
            list_info(isbn) # List the information of the book

    elif ch == 0:  # If the choice is 0
        return # Return to the main menu


def search_isbn(isbn):  # Search for a book by ISBN
    db.execute("SELECT isbn FROM inventory WHERE isbn = '{}'".format(isbn)) # Search for the book by ISBN
    rs = db.fetchall()
    if len(rs) == 0:
        print("Book not found in database! Searching online for book info...")
        get_book_info_external(isbn) # Get book information from ISBNDB API if the book is not found in the database
    else:
        return rs[0][0]


def search_title(title):  # Search for a book by title
    db.execute("SELECT isbn, title FROM inventory WHERE title LIKE '%{}%' LIMIT 10".format(title))
    rs = db.fetchall()
    if len(rs) == 0: # If the book is not found
        print("Books not found! Try searching by ISBN or try a different title.")
        return False
    else:
        j = 0
        for i in rs: # Iterate through the books found
            j += 1
            print("{}. {}".format(j, i[1])) # Print the title of the book

        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: ")) # Input the number of the book to select
                if ch <= 10 and ch >= 1:
                    return rs[ch-1][0] # Return the ISBN of the book
                elif ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list."), "red") # Print an error message if the number is not in the list


def search_publisher(publisher):  # Search for a book by publisher
    db.execute("SELECT isbn, title FROM inventory WHERE publisher LIKE '%{}%' LIMIT 10".format(publisher))
    rs = db.fetchall()
    if len(rs) == 0: # If the book is not found
        print("Books not found! Try searching by ISBN or try a different publisher.")
        return False
    else:
        j = 0
        for i in rs: # Iterate through the books found
            j += 1
            print("{}. {}".format(j, i[1])) # Print the title of the book

        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: ")) # Input the number of the book to select
                if ch <= 10 and ch >= 1:
                    return rs[ch-1][0] # Return the ISBN of the book
                if ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red")) # Print an error message if the number is not in the list


def search_author(author):  # Search for a book by author
    db.execute("SELECT isbn, title FROM inventory WHERE authors LIKE '%{}%' LIMIT 10".format(author))
    rs = db.fetchall()
    if len(rs) == 0: # If the book is not found
        print("Books not found! Try searching by ISBN or try a different author.")
        return False
    else:
        j = 0
        for i in rs: # Iterate through the books found
            j += 1
            print("{}. {}".format(j, i[1])) # Print the title of the book

        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: ")) # Input the number of the book to select
                if ch <= 10 and ch >= 1:
                    return rs[ch-1][0] # Return the ISBN of the book
                if ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red")) # Print an error message if the number is not in the list


def search_price(maxprice, minprice):  # Search for a book by price
    db.execute("SELECT isbn, title FROM inventory WHERE price BETWEEN '{}' AND '{}' LIMIT 10".format(
        minprice, maxprice))
    rs = db.fetchall() 
    if len(rs) == 0: # If the book is not found
        print("No books found within the given price range!")
        return False
    else:
        j = 0
        for i in rs: # Iterate through the books found
            j += 1
            print("{}. {}".format(j, i[1])) # Print the title of the book

        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: ")) # Input the number of the book to select
                if ch <= 10 and ch >= 1:
                    return rs[ch-1][0] # Return the ISBN of the book
                if ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red")) # Print an error message if the number is not in the list


def search_yearofpublishing(year):  # Search for a book by year of publishing
    db.execute("SELECT isbn, title FROM inventory WHERE year(date_published) = '{}' LIMIT 10".format(year))
    rs = db.fetchall()
    if len(rs) == 0: # If the book is not found
        print("No books found with the given year of publishing!")
        return False
    else:
        j = 0
        for i in rs: # Iterate through the books found
            j += 1
            print("{}. {}".format(j, i[1])) # Print the title of the book

        while True:
            try:
                ch = int(input("Enter the number of the book you would like to select: ")) # Input the number of the book to select
                if ch <= 10 and ch >= 1:
                    return rs[ch-1][0] # Return the ISBN of the book
                if ch == 0:
                    return
            except:
                print(termcolor.colored("Error! Choose a number from the list.", "red"))


# Get book information from ISBNDB API if the book is not found in the database
def get_book_info_external(isbn):
    API_KEY = "" # API Key for ISBNDB API
    url = f'https: //api2.isbndb.com/book/{isbn}' # URL for the API
    headers = {'Authorization': API_KEY} # Headers for the API
    response = requests.get(url=url, headers=headers) # Request the data from the API
    if response.status_code == 200: # If the response is successful
        data = response.json() # Get the data from the response
        isbn = data.get("book", {}).get("isbn10", "")
        isbn13 = data.get("book", {}).get("isbn13", "")
        title = data.get("book", {}).get("title_long", "")
        synopsis = data.get("book", {}).get("synopsis", "")
        publisher = data.get("book", {}).get("publisher", "")
        authors = data.get("book", {}).get("authors", [])
        date_published = data.get("book", {}).get("date_published", "")
        language = data.get("book", {}).get("language", "")
        msrp = data.get("book", {}).get("msrp", 0.0)
        msrp = float(msrp) * 3.67
        pages = data.get("book", {}).get("pages", 0)
        list_info(isbn, isbn13, title, synopsis, publisher,
                  authors, date_published, language, msrp, pages) # List the information of the book
    if response.status_code == 403: # If the API rate limit is exceeded
        print("API rate limit exceeded. Waiting for 30 seconds...")
        time.sleep(30) # Wait for 30 seconds
        return get_book_info_external(isbn) # Get the book information from the API
    else: # If the response is not successful
        print("Book not found!")


def list_info(isbn, isbn13=None, title=None, synopsis=None, publisher=None, authors=None, date_published=None, language=None, price=None, pages=None):  # List the information of the book
    db.execute(
        "SELECT isbn,isbn13,title,synopsis,publisher,authors,date_published,language,price,pages FROM inventory WHERE isbn = '{isbn}'".format(isbn=isbn))
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
    if ch == 1: # Add to cart
        db.execute("INSERT IGNORE INTO cart VALUES('{}', '{}')".format(login_username, isbn))
        cdb.commit()
        print("Item added to cart!")
        print()
    elif ch == 2:
        buy(isbn) # Buy the book
        db.execute("DELETE FROM cart WHERE username = '{}' AND isbn = '{}'".format(login_username, isbn)) # Delete the book from the cart
        cdb.commit()
        print()
    elif ch == 3: # Get AI suggestions
        print(termcolor.colored(ai_suggestions(rs[0][2], rs[0][3], str(
            rs[0][6])[0:3], rs[0][5], rs[0][9]), "yellow"))
        # Print AI Warning
        print(termcolor.colored(
            "Warning: The AI suggestions are generated by an AI model and may not be accurate. Please verify the suggestions before making a purchase.", "red", attrs=["bold"]))
        print()
    elif ch == 0:
        return


def ai_suggestions(title, synopsis, year, author, pages):  # Suggest books similar to the one entered
    client = Groq(api_key="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") # Initialize the Groq client with the API key
    completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are a helpful assistant, who informs people about similar books that they would be interested to read"}, {"role": "user", "content": f"The book is {title}. The synopsis of the book is {synopsis}. It was released in {year}. The authors of the book is/are {author}, and the book is {pages} pages long. Suggest three books similar to this one. Do not format the output (just give a plaintext response)."}]) # Create a completion with the AI model and the messages to be sent to the AI.
    return completion.choices[0].message.content # Return the response from the AI


def cart():  # View cart
    print("Your cart:")
    db.execute("SELECT DISTINCT isbn FROM cart WHERE username = '{}'".format(login_username))
    rs = db.fetchall()
    if len(rs) == 0:
        print("Your cart is empty!")
        print()
        return

    j = 0
    for i in rs: # Iterate through the books in the cart
        j += 1
        db.execute("SELECT title FROM inventory WHERE isbn = '{}'".format(i[0]))
        rs2 = db.fetchall()
        print("{}. {}".format(j, rs2[0][0])) # Print the title of the book

    print()
    print("Menu")
    print("1. Remove item from cart")
    print("2. Empty Cart")
    print("3. Checkout")
    print("0. Go back")
    ch = int(input("Enter your choice: "))
    if ch == 1: # Remove item from cart
        ind = int(input("Enter the serial number of the book you want to remove: "))
        isbn = rs[ind-1][0]
        db.execute("DELETE FROM cart WHERE username = '{}' AND isbn = '{}'".format(login_username, isbn))
        cdb.commit()
        print("Item removed from cart!")
        print()

    elif ch == 2: # Empty cart
        db.execute("DELETE FROM cart WHERE username = '{}'".format(login_username))
        cdb.commit()
        print("Cart emptied!")
        print()

    elif ch == 3: # Checkout
        for i in rs:
            db.execute("SELECT price FROM inventory WHERE isbn = '{}'".format(i[0]))
            rs2 = db.fetchall()
            buy(i[0])
            db.execute("DELETE FROM cart WHERE username = '{}' AND isbn = '{}'".format(
                login_username, i[0]))
            cdb.commit()
        print("Order(s) placed successfully!")
        print()
    elif ch == 0:
        return


def edit_customer():  # Edit customer details
    print()
    print("1. Change name")
    print("2. Change email")
    print("3. Change phone number")
    print("4. Change password")
    print("5. Delete account")

    ch = int(input("Enter your choice: "))

    while True:
        if ch == 1: # Change name
            name = input("Enter new name: ")
            db.execute("UPDATE users SET name = %s WHERE username = %s", (name, login_username))
            cdb.commit()
            print("Name changed successfully!")
            print()
            break

        elif ch == 2: # Change email
            email = input("Enter new email: ")
            db.execute("UPDATE users SET email = %s WHERE username = %s", (email, login_username))
            cdb.commit()
            print("Email changed successfully!")
            print()
            break

        elif ch == 3: # Change phone number
            phone_number = input("Enter new phone number in international format: ")
            db.execute("UPDATE users SET phone_number = %s WHERE username = %s",
                       (phone_number, login_username))
            cdb.commit()
            print("Phone number changed successfully!")
            print()
            break

        elif ch == 4: # Change password
            password = getpass("Enter your current password: ") # Mask the password while it's being inputted
            db.execute("SELECT passhash FROM auth WHERE username = %s", (login_username,))
            rs = db.fetchall()[0][0]
            try:
                # Verify if current password matches the hash existing in the database
                pass_check = pass_verify(rs, password)
            except argon2.exceptions.VerifyMismatchError:
                # Go back if the password entered was incorrect
                return

            if pass_check == True: # If the password is correct
                newpass = getpass("Enter new password: ")
                confirm = getpass("Confirm new password: ") # Confirm the new password
                if newpass != confirm: # If the passwords don't match
                    print("Passwords don't match!")
                    print()
                    break
                passhash = pass_hasher(newpass) # Hash the new password
                db.execute("UPDATE auth SET passhash = %s WHERE username = %s",
                           (passhash, login_username)) # Update the password hash in the database
                cdb.commit()
                print("Password changed successfully!")
                print()
                break
        elif ch == 5:
            delete_account() # Delete the user account
            break

        elif ch == 0:
            break


def delete_account():  # Delete the user account
    print(termcolor.colored("Warning: Deleting your account will remove all books from My Library! This action is irreversible!", "red", attrs=["bold"]))
    ch = input("Are you sure you want to delete your account? (y/n): ")
    if ch.lower() == 'y':
        # Prompt for password as confirmation
        password = getpass("Enter your password to confirm account deletion: ") 
        db.execute("SELECT passhash FROM auth WHERE username = '{}'".format(login_username))
        rs = db.fetchall()
        while True:
            try:
                # Verify if current password matches the hash existing in the database
                pass_check = pass_verify(rs[0][0], password)

            except argon2.exceptions.VerifyMismatchError:
                print(termcolor.colored("Incorrect password!", "red"))

            if pass_check == True: # If the password is correct
                db.execute("DELETE FROM users WHERE username = '{}'".format(login_username)) # Delete the user from the users table
                cdb.commit()
                db.execute("DELETE FROM auth WHERE username = '{}'".format(login_username)) # Delete the user from the auth table
                cdb.commit()
                db.execute("DELETE FROM cart WHERE username = '{}'".format(login_username)) # Delete the user's cart
                cdb.commit()
                print("Account deleted successfully!")
                kill() # Exit the program
    else:
        return


def buy(isbn):
    # Check if the book has already been bought by the user
    if check_if_bought(isbn) == True:
        print("You have already bought this book!")
        print()
        return

    while True:
        # Prompt for credit card details
        card_number = input("Enter your credit card number: ")
        if luhn(card_number) == False: # Check the credit card number's validity
            print("Invalid credit card number!")
            continue
        else: # If the credit card number is valid
            expiration_date = input("Enter the expiration date (MM/YY): ")
            # Check expiration date
            if not check_cc_expiry(expiration_date): # Check if the credit card has expired
                print("Credit card expired!")
                continue
            else:
                cvv = getpass("Enter the CVV: ") # Mask the CVV while it's being inputted
                if len(cvv) != 3:
                    print("Invalid CVV!")
                    continue
                else:
                    name = input("Enter the name on the card: ")
                    addr = input("Enter the billing address: ")
                    break

    # Process the payment and complete the transaction
    db.execute("SELECT price FROM inventory WHERE isbn = '{}'".format(isbn))
    price = db.fetchall()[0][0]
    db.execute("INSERT INTO transactions (order_date, username, isbn, total_price) VALUES('{}', '{}', '{}', '{}')".format(
        datetime.datetime.now(), login_username, isbn, price)) # Insert the transaction details into the transactions table
    cdb.commit()

    print(termcolor.colored("Payment successful!", "green"))
    print(termcolor.colored("Thank you for your purchase!", "green"))
    print()


def check_if_bought(isbn):  # Check if the book has already been bought by the user
    db.execute("SELECT isbn FROM transactions WHERE username = '{}'".format(login_username))
    rs = db.fetchall()
    for i in rs: # Iterate through the books bought by the user
        if i[0] == isbn: # If the book has already been bought
            return True
    return False


def list_bought():  # List the books bought by the user
    db.execute("SELECT isbn FROM transactions WHERE username = '{}'".format(login_username))
    rs = db.fetchall()
    if len(rs) == 0: # If the user hasn't bought any books
        print("No books bought yet!")
        print()
        return

    j = 0
    for i in rs: # Iterate through the books bought by the user
        j += 1
        db.execute("SELECT title FROM inventory WHERE isbn = '{}'".format(i[0])) # Get the title of the book
        rs2 = db.fetchall()
        print("{}. {}".format(j, rs2[0][0])) # Print the title of the book
    print()


def luhn(ccn):  # Check if the credit card number entered is correct
    c = [int(x) for x in str(ccn)[::-2]] # Get the digits of the credit card number
    u2 = [(2*int(y))//10+(2*int(y)) % 10 for y in str(ccn)[-2::-2]]
    return sum(c+u2) % 10 == 0


def check_cc_expiry(expiry):
    month, year = str(expiry).split("/")
    if int(month) > 12 or int(month) < 1:
        return False
    if int(year) + 2000 < datetime.datetime.now().year:
        return False
    if int(year) + 2000 == datetime.datetime.now().year and int(month) < datetime.datetime.now().month:
        return False
    else:
        return True


def start():  # Start the program
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


def main():  # Main menu
    while True:
        print("1. Search")
        print("2. Cart")
        print("3. My Library")
        print("4. My Account")
        print("5. Credits")
        print("0. Logout")
        ch = int(input("Enter your choice: "))
        if ch == 1:
            print("""
 __
(_  _  _  __ _ |_
__)(/_(_| | (_ | |
            """)
            search()
        elif ch == 2:
            print("""
 __
/   _ ___|_
\__(_||  |_
""")
            cart()
        elif ch == 3:
            print("""
|V|\/ |  o|_ ___ __\/
| |/  |__||_)|(_|| /
""")
            list_bought()

        elif ch == 4:
            print("""
       _
|V|\/ |_| _ _ _    ___|_
| |/  | |(_(_(_)|_|| ||_
""")
            edit_customer()
        elif ch == 5:
            # TODO: Acknowledgement
            print("""
Thank you!
            """)
        elif ch == 0:
            logout()
        else:
            pass


if __name__ == "__main__":
    start()