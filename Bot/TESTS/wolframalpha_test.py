import wolframalpha
question = input('Question: ')
app_id = ''
client = wolframalpha.Client(app_id)
res = client.query(question)
answer = next(res.results).text
print(answer)