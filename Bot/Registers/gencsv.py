import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

df = pd.DataFrame(columns=['id', 'users'])

os.chdir('Registers')
for file in os.listdir():
    if file.endswith('.txt'):
        opened = open(file, 'r', encoding='utf-8')
        lines = opened.readlines()
        opened.close()
        id = file.replace('.txt', '')
        users = []
        for line in lines:
            if len(line.split()):
                user = line.split()[0]
                if len(line.split()) > 1:
                    date = line.replace(user, '').replace('\n', '')[1:]
                else:
                    date = ''
                users.append({'user': user, 'date': date})
        df = df.append({'id': id, 'users': users}, ignore_index=True)

print(df.head(100))
df.to_json('Registers.json', orient='records', force_ascii=False)