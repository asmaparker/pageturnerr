import csv
from mysql.connector import connect

cdb = connect(host='localhost', user='root', password='root', database='bookstore')
db = cdb.cursor()

def verify_record(csv):
    db.execute("SELECT * FROM books")
    rs = db.fetchall()
    for row in rs:
        if row == csv:
            return True
        else:
            print(row)
            input()
            return False

f = open('books.csv', 'r', encoding='utf-8')
reader = csv.reader(f, delimiter='||')
for row in reader:
    print(verify_record(row))