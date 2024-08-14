from groq import Groq

def ai_suggestions(title, synopsis, year, author, pages):
    client = Groq(api_key="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")
    completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are a helpful assistant, who informs people about similar books that they would be interested to read"}, {"role": "user", "content": f"The book is {title}. The synopsis of the book is {synopsis}. It was released in {year}. The authors of the book is/are {author}, and the book is {pages} pages long. Suggest three books similar to this one."}])
    return completion.choices[0].message.content
