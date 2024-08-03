import pandas as pd
import json
import glob

# Load the books.csv into a DataFrame
books_df = pd.read_csv('books.csv')

# Create a dictionary to store msrp values with isbn as the key
msrp_dict = {}

# Directory containing JSON files
files = glob.glob(pathname="D:\\Downloads\\asmaaa\\jsons\\*.json")

# Iterate over JSON files and populate the msrp_dict
for json_file in files:
    print(json_file )
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        isbn = data['book']['isbn']
        msrp = data['book']['msrp']
        msrp_dict[isbn] = msrp

# Add a new column 'msrp' to the books_df DataFrame, defaulting to None
books_df['msrp'] = books_df['isbn'].map(msrp_dict)

# Save the updated DataFrame to a new CSV file
books_df.to_csv('books_with_msrp.csv', index=False)
