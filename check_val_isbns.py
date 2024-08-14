import csv

def is_valid_isbn10(isbn):
    isbn = isbn.upper()
    if len(isbn) != 10 or not isbn[:-1].isdigit() or (isbn[-1] not in '0123456789X'):
        return False
    total = sum((i + 1) * int(x) for i, x in enumerate(isbn[:-1]))
    if isbn[-1] == 'X':
        total += 10 * 10
    else:
        total += 10 * int(isbn[-1])
    return total % 11 == 0

def is_valid_isbn13(isbn):
    isbn = isbn.replace('-', '')
    isbn = isbn.strip()
    isbn = isbn.replace("\n", "")
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = sum(int(x) * (3 if i % 2 else 1) for i, x in enumerate(isbn[:-1]))
    return (10 - total % 10) % 10 == int(isbn[-1])

f = open("isbns.txt")
count = 0
j = 0
for isbn in f:
    j += 1
    check = is_valid_isbn13(isbn)
    count += 1 if not check else 0
    if not check:
        print(isbn)
print("Invalid ISBN's", count)
print("Total Valid Books", j - count)