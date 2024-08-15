# Read list of all files in directory, change single quotes to double quotes and write to same file

import glob
files = glob.glob(pathname="D:\\Downloads\\asmaaa\\jsons\\*.txt")

"""
for file in files:
    with open(file, 'r') as f:
        data = f.read()
        data = data.replace('"', "'")
    with open(file, 'w') as f:
        f.write(data)
"""

for file in files:
    with open(file, 'r') as f:
        data = f.read()
        data = data.replace("'book':", '"book":')
    with open(file, 'w') as f:
        f.write(data)
