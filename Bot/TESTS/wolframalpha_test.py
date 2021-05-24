import wolframalpha
question = input('Question: ')
app_id = '629QXL-6L55AEKG5L'
client = wolframalpha.Client(app_id)
res = client.query(question)
answer = next(res.results).text
print(answer)