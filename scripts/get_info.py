import requests
import csv
import time

def get_isbndb_book_info(isbn, api_key):
    url = f'https://api2.isbndb.com/book/{isbn}'
    headers = {'Authorization': api_key}
    response = requests.get(url=url, headers=headers)
    print(response)
    print(response.json())

    if response.status_code == 200:
        data = response.json()
        book_info = [data.get("book", {}).get("isbn10", ""), data.get("book", {}).get("isbn13", ""), data.get("book", {}).get("title_long", ""), data.get("book", {}).get("synopsis", ""), data.get("book", {}).get("publisher", ""), data.get("book", {}).get("authors", []), data.get("book", {}).get("date_published", ""), data.get("book", {}).get("language", ""), data.get("book", {}).get("msrp", 0.0)]
        return book_info
    if response.status_code == 403:
        print(response.json())
        print("API rate limit exceeded. Waiting for 1 minute...")
        time.sleep(60)
        return get_isbndb_book_info(isbn, api_key)
    else:
        print(f"Error: Unable to fetch data for ISBN {isbn}. Status code: {response.status_code}")
        return None

api_key = '54654_777ab1c90ced7e22bb2b5770678ddc08'
books = ["isbn", "isbn13", "title", "synopsis", "publisher", "authors", "date_published", "language", "price", "pages", "avg_rating"]
f = open("books.csv")
reader = csv.reader(f)

j = open("books_with_info.csv", "w", newline='')
writer = csv.writer(j)

# writer.writerow(books)
for row in reader:
    isbn = row[4]
    print(row)
    book_info = get_isbndb_book_info(isbn, api_key)
    pages = row[7]
    avg_rating = row[3]
    if book_info:
        book_info.append(pages)
        book_info.append(avg_rating)
        writer.writerow(book_info)

f.close()