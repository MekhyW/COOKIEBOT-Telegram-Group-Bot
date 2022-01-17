from universal_funcs import *
import googletrans
translator = googletrans.Translator()

def decapitalize(s, upper_rest = False):
  return ''.join([s[:1].lower(), (s[1:].upper() if upper_rest else s[1:])])

def TaVivo(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Estou vivo\n\nPing enviado em:\n" + str(datetime.datetime.now()))

def Comandos(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Cookiebot functions.txt")
    text_file = open("Cookiebot functions.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    string = ""
    for line in lines:
        if len(line.split()) != 3:
            string += str(line)
    cookiebot.sendMessage(chat_id, string, reply_to_message_id=msg['message_id'])

def Hoje(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    category = random.choice(['entertainment', 'general', 'science', 'technology'])
    lang = random.choice(['pt', 'en'])
    r = requests.get('https://newsapi.org/v2/top-headlines?language={}&from={}&to={}&category={}&apiKey={}'.format(lang, str(yesterday), str(today), category, newsAPIkey))
    dictionary = json.loads(r.text)
    article = dictionary['articles'][random.randint(0, len(dictionary['articles'])-1)]
    title = article['title'].split(' - ')[0]
    title = translator.translate(title, dest='pt').text
    source = article['url']
    cookiebot.sendMessage(chat_id, "Hoje {}\nFonte: {}".format(decapitalize(title), source), reply_to_message_id=msg['message_id'])

def Cheiro(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Cheiro.txt")
    text_file = open("Cheiro.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "*sniff* *sniff*\nHmmmmmm\n\nVocê está com um cheirin de "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def QqEuFaço(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("QqEuFaço.txt")
    text_file = open("QqEuFaço.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "Vai "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def IdeiaDesenho(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    ideiasdesenho = os.listdir('IdeiaDesenho')
    ideiaID = random.randint(0, len(ideiasdesenho)-1)
    photo = open('IdeiaDesenho'+'/'+ideiasdesenho[ideiaID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, caption="Referência com ID {}\n\nNão trace sem dar créditos! (use a busca reversa do google images)".format(ideiaID), reply_to_message_id=msg['message_id'])
    photo.close()

def Contato(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, '💌 Email: felipe_catapano@yahoo.com.br\n🔵 Telegram: @MekhyW\n🟦 LinkedIn: https://www.linkedin.com/in/felipe-catapano/\n⚛️ GitHub: https://github.com/MekhyW')

def CustomCommand(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    images = os.listdir("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", ''))
    imageID = random.randint(0, len(images)-1)
    photo = open("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')+'/'+images[imageID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])
    photo.close()

def Dado(cookiebot, msg, chat_id):
    if msg['text'].startswith("/dado"):
        cookiebot.sendMessage(chat_id, "Rodo um dado de 1 até x, n vezes\nEXEMPLO: /d20 5\n(Roda um d20 5 vezes)")
    else:
        if len(msg['text'].split()) == 1:
            vezes = 1
        else:
            vezes = int(msg['text'].replace("@CookieMWbot", '').split()[1])
            vezes = max(min(20, vezes), 1)
        limite = int(msg['text'].replace("@CookieMWbot", '').split()[0][2:])
        resposta = "(d{}) ".format(limite)
        if vezes == 1:
            resposta += "🎲 -> {}".format(random.randint(1, limite))
        else:
            for vez in range(vezes):
                resposta += "\n{}º Lançamento: 🎲 -> {}".format(vez+1, random.randint(1, limite))
        cookiebot.sendMessage(chat_id, resposta, reply_to_message_id=msg['message_id'])

def Idade(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if not " " in msg['text']:
        cookiebot.sendMessage(chat_id, "Digite um nome, vou dizer a sua idade!\n\nEx: '/idade Mekhy'\n(obs: só o primeiro nome conta)", reply_to_message_id=msg['message_id'])
    else:
        Nome = msg['text'].replace("/idade ", '').split()[0]
        response = json.loads(requests.get("https://api.agify.io?name={}".format(Nome)).text)
        Idade = response['age']
        Contagem = response['count']
        if Contagem == 0:
            cookiebot.sendMessage(chat_id, "Não conheço esse nome!", reply_to_message_id=msg['message_id'])
        else:
            cookiebot.sendMessage(chat_id, "Sua idade é {} anos! 👴\nRegistrado {} vezes".format(Idade, Contagem), reply_to_message_id=msg['message_id'])

def Genero(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if not " " in msg['text']:
        cookiebot.sendMessage(chat_id, "Digite um nome, vou dizer o seu gênero!\n\nEx: '/genero Mekhy'\n(obs: só o primeiro nome conta)\n(obs 2: POR FAVOR NÃO LEVAR ISSO A SÉRIO, É ZUERA)", reply_to_message_id=msg['message_id'])
    else:
        Nome = msg['text'].replace("/genero ", '').split()[0]
        response = json.loads(requests.get("https://api.genderize.io?name={}".format(Nome)).text)
        Genero = response['gender']
        Probabilidade = response['probability']
        Contagem = response['count']
        if Contagem == 0:
            cookiebot.sendMessage(chat_id, "Não conheço esse nome!", reply_to_message_id=msg['message_id'])
        elif Genero == 'male':
            cookiebot.sendMessage(chat_id, "É um menino! 👨\n\nProbabilidade --> {}%\nRegistrado {} vezes".format(Probabilidade*100, Contagem), reply_to_message_id=msg['message_id'])
        elif Genero == 'female':
            cookiebot.sendMessage(chat_id, "É uma menina! 👩\n\nProbabilidade --> {}%\nRegistrado {} vezes".format(Probabilidade*100, Contagem), reply_to_message_id=msg['message_id'])