from universal_funcs import *
import unidecode
import googletrans
translator = googletrans.Translator()
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
chatbot = ChatBot('Cookiebot', storage_adapter='chatterbot.storage.SQLStorageAdapter', database_uri='sqlite:///database.sqlite3', logic_adapters=['chatterbot.logic.BestMatch'])
conversa = ChatterBotCorpusTrainer(chatbot)
conversa.train('chatterbot.corpus.portuguese')
conversa = ListTrainer(chatbot)

def OnSay(cookiebot, msg, chat_id):
    if len(msg['text'].split()) > 3:
        keyword_texts = []
        for word in msg['text'].split():
            keyword_texts.append(unidecode.unidecode(''.join(filter(str.isalnum, word.lower()))))
        print(keyword_texts)
        wait_open("Onsay_Dictionary.txt")
        text_file = open("Onsay_Dictionary.txt", 'r', encoding='utf8')
        lines = text_file.readlines()
        text_file.close()
        for line in lines:
            if len(line.split(" > ")) == 2:
                queries = json.loads(line.split(" > ")[0])
                answer = line.split(" > ")[1]
                if set(queries).issubset(keyword_texts):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, answer, reply_to_message_id=msg['message_id'])
                    return True
    return False

def ChatterbotAbsorb(msg):
    conversa.train([msg['reply_to_message']['text'], msg['text']])

def InteligenciaArtificial(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    message = ""
    Answer = ""
    if "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']:
        message = msg['text'].replace("Cookiebot", '').replace("cookiebot", '').replace("@CookieMWbot", '').replace("COOKIEBOT", '').replace("CookieBot", '').replace("\n", '').capitalize()
    else:
        message = msg['text'].replace("\n", '').capitalize()
    Answer1 = ''
    r = requests.get('https://api.simsimi.net/v2/?text={}&lc=pt&cf=true'.format(message))
    try:
        Answer1 = json.loads(r.text)['messages'][0]['response'].capitalize()
        Answer1 = translator.translate(Answer1, dest='pt').text
    except:
        print(r.text)
        if len(str(r.text).split("{")) > 1:
            Answer1 = str(r.text).split("{")[1]
            Answer1 = "{" + Answer
            Answer1 = json.loads(Answer)['messages'][0]['response'].capitalize()
            Answer1 = translator.translate(Answer1, dest='pt').text
    Answer2 = chatbot.get_response(message)
    Answer2_text = Answer2.text.capitalize()
    if Answer1 and Answer2.confidence < 0.5:
        AnswerFinal = Answer1
    else:
        AnswerFinal = Answer2_text
    cookiebot.sendMessage(chat_id, AnswerFinal, reply_to_message_id=msg['message_id'])