import urllib.request
import csv

url = "https://raw.githubusercontent.com/asmaparker/pageturnerr/main/books.csv?token=GHSAT0AAAAAACU2SZQM3LQTJYCB566BUQZYZVOQEYQ"
response = urllib.request.urlopen(url)
reader = csv.reader(response)
for row in reader:
    print(row)
    input()