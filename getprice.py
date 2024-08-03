import requests
import csv
import time

def get_isbndb_book_price(isbn, api_key):
    url = f'https://api2.isbndb.com/book/{isbn}'
    headers = {'Authorization': api_key}
    response = requests.get(url=url, headers=headers)
    print(response)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        # save json to text file
        filename = isbn + ".txt"
        with open(file=filename, mode='w') as f:
            f.write(str(data))
        msrp = data['book']['msrp']
        return msrp
    if response.status_code == 403:
        print(response.json())
        print("API rate limit exceeded. Waiting for 1 minute...")
        time.sleep(60)
        return get_isbndb_book_price(isbn, api_key)
    else:
        return 'Price information not available.'

# Example usage
api_key = '54654_777ab1c90ced7e22bb2b5770678ddc08'

# Make a new CSV, by copying old csv and adding a new column price to it
f = open("books.csv", encoding='latin-1')
csv_f = csv.reader(f)
count = 0
new_csv = []
row = [next(csv_f), "Price"]
new_csv.append(row)
for row in csv_f:
    print(row)
    isbn = row[4]
    price = get_isbndb_book_price(isbn, api_key)
    if price == "Price information not available." or float(price) == 0.00:
        count += 1
        print("Zero Cost Books " + str(count))
    print(price)
    row.append(price)
    new_csv.append(row)

f.close()

# Export new_csv to a new file
with open('books_with_price.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(new_csv)