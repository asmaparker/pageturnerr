import requests
import csv

url = "https://raw.githubusercontent.com/asmaparker/pageturnerr/main/books.csv?"
i = 0
with requests.get(url=url, stream=True) as r:
    lines = (line.decode('utf-8') for line in r.iter_lines())
    next(lines)
    for row in csv.reader(lines, delimiter='|'):
        print(row)
        print("ISBN:", row[0])
        print("ISBN13:", row[1])
        print("Title:", row[2])
        print("Synopsis:", row[3])
        print("Publisher:", row[4])
        print("Author:", row[5])
        print("Publication Date:", row[6])
        print("Language:", row[7])
        print("Price:", row[8])
        print("Pages:", row[9])
