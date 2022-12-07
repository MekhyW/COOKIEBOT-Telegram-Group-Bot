from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import pandas as pd
bot = ChatBot(
    'Cookiebot_AI',  
    logic_adapters=[
        'chatterbot.logic.BestMatch'],
    database_uri='sqlite:///AI_ptbr.db'
)
#conversa = ChatterBotCorpusTrainer(bot)
#conversa.train('chatterbot.corpus.portuguese')
conversa = ListTrainer(bot)
df = pd.read_csv('result-master-ptbr.csv')
for index in range(len(df)):
    if index < 531000:
        continue
    print(str(index) + ' / ' + str(len(df)))
    try:
        conversa.train([df.loc[index, 'Question'], df.loc[index, 'Answer']])
    except Exception as e:
        print(e)