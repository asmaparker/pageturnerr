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

f = open("check.txt")
count = 0
j = 0
for isbn in f:
    j += 1
    check = is_valid_isbn10(isbn)
    count += 1 if not check else 0
    print(isbn, check)

print("Invalid ISBN's", count)
print("Total Valid Books", j - count)