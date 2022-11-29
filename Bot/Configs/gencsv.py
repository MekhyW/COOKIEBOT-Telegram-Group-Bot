import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

df = pd.DataFrame(columns=['id', 'furbots', 'stickerSpamLimit', 'timeWithoutSendingImages', 'timeCaptcha', 'functionsFun', 'functionsUtility', 'sfw', 'language', 'publisherPost', 'publisherAsk'])

os.chdir('Configs')
for file in os.listdir():
    if file.endswith('.txt'):
        opened = open(file, 'r', encoding='utf-8')
        lines = opened.readlines()
        opened.close()
        id = file.replace('.txt', '').replace('Config_', '')
        for line in lines:
            if line.startswith('FurBots'):
                furbots = bool(int(line.replace('FurBots: ', '').replace('\n', '')))
            elif line.startswith('Sticker_Spam_Limit'):
                stickerSpamLimit = int(line.replace('Sticker_Spam_Limit: ', '').replace('\n', ''))
            elif line.startswith('Tempo_sem_poder_mandar_imagem'):
                timeWithoutSendingImages = int(line.replace('Tempo_sem_poder_mandar_imagem: ', '').replace('\n', ''))
            elif line.startswith('Tempo_Captcha'):
                timeCaptcha = int(line.replace('Tempo_Captcha: ', '').replace('\n', ''))
            elif line.startswith('Funções_Diversão'):
                functionsFun = bool(int(line.replace('Funções_Diversão: ', '').replace('\n', '')))
            elif line.startswith('Funções_Utilidade'):
                functionsUtility = bool(int(line.replace('Funções_Utilidade: ', '').replace('\n', '')))
            elif line.startswith('SFW'):
                sfw = bool(int(line.replace('SFW: ', '').replace('\n', '')))
            elif line.startswith('Language'):
                language = line.replace('Language: ', '').replace('\n', '')
            elif line.startswith('Publisher_Post'):
                publisherPost = bool(int(line.replace('Publisher_Post: ', '').replace('\n', '')))
            elif line.startswith('Publisher_Ask'):
                publisherAsk = bool(int(line.replace('Publisher_Ask: ', '').replace('\n', '')))
        df = df.append({'id': id, 'furbots': furbots, 'stickerSpamLimit': stickerSpamLimit, 'timeWithoutSendingImages': timeWithoutSendingImages, 'timeCaptcha': timeCaptcha, 'functionsFun': functionsFun, 'functionsUtility': functionsUtility, 'sfw': sfw, 'language': language, 'publisherPost': publisherPost, 'publisherAsk': publisherAsk}, ignore_index=True)

print(df.head(100))
df.to_csv('Configs.csv', index=False)