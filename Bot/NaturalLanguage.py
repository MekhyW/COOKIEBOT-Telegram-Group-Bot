from universal_funcs import *
import wolframalpha, unidecode
import googletrans
translator = googletrans.Translator()
WolframCLIENT = wolframalpha.Client(WolframAPP_ID)

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

def InteligenciaArtificial(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    message = ""
    Answer = ""
    if "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']:
        message = msg['text'].replace("Cookiebot", '').replace("cookiebot", '').replace("@CookieMWbot", '').replace("COOKIEBOT", '').replace("CookieBot", '').replace("\n", '').capitalize()
    else:
        message = msg['text'].replace("\n", '').capitalize()
    try:
        r = WolframCLIENT.query(translator.translate(message, dest='en').text)
        Answer = translator.translate(next(r.results).text, dest='pt').text.capitalize()
        if len(Answer) > 200:
            raise "Flood"
        else:
            cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])
    except:
        r = requests.get('https://api.simsimi.net/v2/?text={}&lc=pt&cf=true'.format(message))
        try:
            Answer = json.loads(r.text)['messages'][0]['response'].capitalize()
        except:
            print(r.text)
            if len(str(r.text).split("{")) > 1:
                Answer = str(r.text).split("{")[1]
                Answer = "{" + Answer
                Answer = json.loads(Answer)['messages'][0]['response'].capitalize()
        Answer = translator.translate(Answer, dest='pt').text
        cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])