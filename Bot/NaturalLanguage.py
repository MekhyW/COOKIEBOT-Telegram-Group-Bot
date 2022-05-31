from universal_funcs import *
import unidecode
import cloudscraper
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'android','desktop': False})

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


def InteligenciaArtificial(cookiebot, msg, chat_id, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    message = ""
    AnswerFinal = ""
    if "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']:
        message = msg['text'].replace("Cookiebot", '').replace("cookiebot", '').replace("@CookieMWbot", '').replace("COOKIEBOT", '').replace("CookieBot", '').replace("\n", '').capitalize()
    else:
        message = msg['text'].replace("\n", '').capitalize()
    if message == '':
        AnswerFinal = "?"
    else:
        Answer1 = ''
        if language == "pt":
            r = scraper.get('https://api-sv2.simsimi.net/v2/?text={}&lc=pt&cf=true'.format(message), timeout=10)
        elif language == "es":
            r = scraper.get('https://api-sv2.simsimi.net/v2/?text={}&lc=es&cf=true'.format(message), timeout=10)
        else:
            r = scraper.get('https://api-sv2.simsimi.net/v2/?text={}&lc=en&cf=true'.format(message), timeout=10)
        try:
            Answer1 = json.loads(r.text)['messages'][0]['response'].capitalize()
        except:
            if len(str(r.text).split("{")) > 1:
                Answer1 = str(r.text).split("{")[1]
                Answer1 = "{" + Answer1
                Answer1 = json.loads(Answer1)['messages'][0]['response'].capitalize()
        if Answer1 and "Eu não resposta." not in Answer1 and "I don't know what you're saying." not in Answer1:
            AnswerFinal = Answer1
        else:
            AnswerFinal = None
    if AnswerFinal:
        cookiebot.sendMessage(chat_id, AnswerFinal, reply_to_message_id=msg['message_id'])
    else:
        print("NO AI ANSWER")