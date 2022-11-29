import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

df = pd.DataFrame(columns=['id', 'user', 'date'])

os.chdir('Registers')
for file in os.listdir():
    if file.endswith('.txt'):
        opened = open(file, 'r', encoding='utf-8')
        lines = opened.readlines()
        opened.close()
        id = file.replace('.txt', '')
        for line in lines:
            if len(line.split()):
                user = line.split()[0]
                if len(line.split()) > 1:
                    date = line.replace(user, '').replace('\n', '')[1:]
                else:
                    date = ''
                df = df.append({'id': id, 'user': user, 'date': date}, ignore_index=True)

print(df.head(100))
df.to_csv('Registers.csv', index=False)