import requests
import time
from mysql.connector import connect

cdb = connect(host="localhost", user="root", password="root")
db = cdb.cursor()
db.execute("CREATE DATABASE IF NOT EXISTS bookstore")
db.execute("USE bookstore")
db.execute("CREATE TABLE IF NOT EXISTS books (isbn CHAR(10), isbn13 CHAR(13), title LONGTEXT, synopsis LONGTEXT, publisher LONGTEXT, authors LONGTEXT, date_published DATE, language CHAR(2), price FLOAT, pages INT)")


def get_book_info(isbn):
    # Use the ISBNDB API to get the price of books and store it in 
    API_KEY = "54894_74349bb8001792ce6e5f0f441912f0ef"
    url = f'https://api2.isbndb.com/book/{isbn}'
    headers = {'Authorization': API_KEY}
    response = requests.get(url=url, headers=headers)
    print(response)
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
        if int(float(msrp)) != 0 and int(float(pages)) != 0:
            if len(str(date_published)) == 4:
                date_published = str(date_published) + "-01-01"
            if len(str(date_published)) == 7:
                date_published = str(date_published) + "-01"
            author = ""
            for i in authors:
                author = author + i + ", "
            author = author[:-2]

            msrp = float(msrp) * 3.67

            try:
                db.execute("INSERT INTO books VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (isbn, isbn13, title, synopsis, publisher, author, date_published, language, msrp, pages))
                cdb.commit()

                print("{} added to database".format(isbn))
                # Save the response JSON to a text file
                filename = isbn + ".txt"
                with open(file=filename, mode='w') as jsonss:
                    jsonss.write(str(data))
            except:
                return False        

            return True
        else:
            return False
    if response.status_code == 403:
        print(response.json())
        print("API rate limit exceeded. Waiting for 1 minute...")
        time.sleep(60)
        return get_book_info(isbn)
    else:
        return 404

f = open("isbns.txt")
i = 0
for isbn in f:
    c = get_book_info(isbn)
    print(isbn)
    if c == 404:
        print("Book not found")
    if c == False:
        print("Book price not found")
    if c == True:
        print("Book added to database")
        i += 1
        print("Books added: {}".format(i), end="\r", flush=True)

print("{} books added to database".format(i))    