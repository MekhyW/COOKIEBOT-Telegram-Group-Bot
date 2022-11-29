import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

df = pd.DataFrame(columns=['id', 'message'])

os.chdir('Welcome')
for file in os.listdir():
    if file.endswith('.txt'):
        opened = open(file, 'r', encoding='utf-8')
        message = opened.read()
        message = message.replace('\n', '\\n').replace('"', "'")
        opened.close()
        id = file.replace('.txt', '').replace('Welcome_', '')
        df = df.append({'id': id, 'message': message}, ignore_index=True)

print(df.head(100))
df.to_csv('Welcome.csv', index=False)