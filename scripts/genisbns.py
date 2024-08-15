import requests
from random import randint
import time

# Replace 'YOUR_API_KEY' with your actual API key from ISBNdb
API_KEY = '54654_777ab1c90ced7e22bb2b5770678ddc08'
API_URL = 'https://api2.isbndb.com/book/'

def is_valid_isbn10(isbn):
    if len(isbn) != 10 or not isbn[:-1].isdigit() or (isbn[-1] not in '0123456789X'):
        return False
    total = sum((i + 1) * int(x) for i, x in enumerate(isbn[:-1]))
    if isbn[-1] == 'X':
        total += 10 * 10
    else:
        total += 10 * int(isbn[-1])
    return total % 11 == 0

def generate_isbn10():
    for _ in range(1000000):  # Generate 1,000,000 ISBNs
        body = ''.join([str(randint(0, 9)) for _ in range(9)])
        checksum = sum((i + 1) * int(x) for i, x in enumerate(body))
        checksum = (11 - (checksum % 11)) % 11
        checksum = 'X' if checksum == 10 else str(checksum)
        isbn = body + checksum
        if is_valid_isbn10(isbn):
            yield isbn

def check_isbn_with_isbndb(isbn):
    print(isbn)
    url = f'https://api2.isbndb.com/book/{isbn}'
    headers = {'Authorization': API_KEY}
    response = requests.get(url=url, headers=headers)
    print(response)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        print(response.json())
        print("API rate limit exceeded. Waiting for 1 minute...")
        time.sleep(60)
        return check_isbn_with_isbndb(isbn)
    else:
        return None

isbn_generator = generate_isbn10()
valid_isbns = []
batch_size = 1000  # Number of ISBNs to check per batch to avoid overwhelming the API

with open('valid_isbns.txt', mode='w') as file:
    for _ in range(1000):  # Check 1,000,000 ISBNs in batches
        batch = [next(isbn_generator) for _ in range(batch_size)]
        for isbn in batch:
            book_info = check_isbn_with_isbndb(isbn)
            if book_info:
                valid_isbns.append(book_info)
                file.write(f"{isbn}\n")  # Write valid ISBN to the file
                print(f"Valid ISBN found: {isbn}")

print("Valid ISBNs with book information:")
print(valid_isbns)