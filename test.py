import mysql.connector

# Connect to the database
conn = mysql.connector.connect(host="localhost", user="asma", password="mysql", database="bookstore")

# Create a cursor object
cursor = conn.cursor()

# Execute a query
cursor.execute('SELECT * FROM test')

# Fetch all the results
results = cursor.fetchall()

# Print the results
print(results[0][0])

# Close the cursor and connection
cursor.close()
conn.close()

