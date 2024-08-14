import requests
import csv
L = []
url = "https://raw.githubusercontent.com/asmaparker/pageturnerr/main/books.csv"
with requests.get(url=url, stream=True, headers={'Cache-Control': 'no-cache'}) as r:
    lines = (line.decode('utf-8') for line in r.iter_lines())
    next(lines)
    for row in csv.reader(lines, delimiter='|'):
        L.append(row)
print(L)