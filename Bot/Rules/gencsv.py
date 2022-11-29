import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

df = pd.DataFrame(columns=['id', 'rules'])

os.chdir('Rules')
for file in os.listdir():
    if file.endswith('.txt'):
        opened = open(file, 'r', encoding='utf-8')
        rules = opened.read()
        rules = rules.replace('\n', '\\n').replace('"', "'")
        opened.close()
        id = file.replace('.txt', '').replace('Regras_', '')
        df = df.append({'id': id, 'rules': rules}, ignore_index=True)

print(df.head(100))
df.to_csv('Rules.csv', index=False)