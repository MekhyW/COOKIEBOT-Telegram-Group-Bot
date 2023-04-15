from universal_funcs import *

def decapitalize(s, upper_rest = False):
  return ''.join([s[:1].lower(), (s[1:].upper() if upper_rest else s[1:])])

def TaVivo(cookiebot, msg, chat_id, language):
    Send(cookiebot, chat_id, "Estou vivo\n\nPing enviado em:\n" + str(datetime.datetime.now()), msg, language)

def Analyze(cookiebot, msg, chat_id, language):
    result = ''
    for item in msg['reply_to_message']:
        result += str(item) + ': ' + str(msg['reply_to_message'][item]) + '\n'
    Send(cookiebot, chat_id, result, msg_to_reply=msg)

def Grupos(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    groups = GetRequestBackend('registers')
    num = 0
    for group in groups:
        try:
            id = group['id']
            chat = cookiebot.getChat(int(id))
            time.sleep(0.2)
            if 'title' in chat:
                cookiebot.sendMessage(chat_id, f"{id} - {chat['title']}")
            else:
                cookiebot.sendMessage(chat_id, f"{id} - [NO TITLE]")
            num += 1
        except Exception as e:
            print(e)
            print("Group not found: " + id)
    cookiebot.sendMessage(chat_id, f"Total groups found: {num}")

def Broadcast(cookiebot, msg):
    groups = GetRequestBackend('registers')
    for group in groups:
        try:
            id = group['id']
            Send(cookiebot, int(id), msg['text'].replace('/broadcast', ''))
            time.sleep(0.5)
        except:
            pass

def Comandos(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    wait_open(f"Static/Cookiebot_functions_{language}.txt")
    text_file = open(f"Static/Cookiebot_functions_{language}.txt", "r+", encoding='utf8')
    string = text_file.read()
    text_file.close()
    Send(cookiebot, chat_id, string, msg_to_reply=msg)

def Hoje(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    wait_open("Static/QqEuFaço.txt")
    text_file = open("Static/QqEuFaço.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    Send(cookiebot, chat_id, "Hoje pra vc é dia de "+target, msg, language)
    text_file.close()

def Cheiro(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    wait_open("Static/Cheiro.txt")
    text_file = open("Static/Cheiro.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    Send(cookiebot, chat_id, "*sniff* *sniff*\nHmmmmmm\n\nVocê está com um cheirin de "+target, msg, language)
    text_file.close()

def QqEuFaço(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    wait_open("Static/QqEuFaço.txt")
    text_file = open("Static/QqEuFaço.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    Send(cookiebot, chat_id, "Vai "+target, msg, language)
    text_file.close()

def IdeiaDesenho(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    ideiasdesenho = os.listdir('IdeiaDesenho')
    ideiaID = random.randint(0, len(ideiasdesenho)-1)
    photo = open('IdeiaDesenho'+'/'+ideiasdesenho[ideiaID], 'rb')
    if language == 'pt':
        caption = f"Referência com ID {ideiaID}\n\nNão trace sem dar créditos! (use a busca reversa do google images)"
    elif language == 'es':
        caption = f"Referencia con ID {ideiaID}\n\n¡No rastrear sin dar créditos! (utilice la búsqueda inversa de imágenes de Google)"
    else:
        caption = f"Reference ID {ideiaID}\n\nDo not trace without credits! (use the reverse google images search)"
    SendPhoto(cookiebot, chat_id, photo, caption=caption, msg_to_reply=msg)
    photo.close()

def CustomCommand(cookiebot, msg, chat_id):
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    button = InlineKeyboardButton(text="Again", callback_data=f"REPEAT custom {msg['text']} {msg['message_id']}")
    images = os.listdir("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", ''))
    imageID = random.randint(0, len(images)-1)
    photo = open("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')+'/'+images[imageID], 'rb')
    SendPhoto(cookiebot, chat_id, photo, msg_to_reply=msg)
    photo.close()

def Dado(cookiebot, msg, chat_id, language):
    if msg['text'].startswith("/dado"):
        Send(cookiebot, chat_id, "Rodo um dado de 1 até x, n vezes\nEXEMPLO: /d20 5\n(Roda um d20 5 vezes)")
    elif msg['text'].startswith("/dice"):
        Send(cookiebot, chat_id, "Roll a dice from 1 to x, n times\nEXAMPLE: /d20 5\n(Rotate a d20 5 times)")
    else:
        if len(msg['text'].split()) == 1:
            vezes = 1
        else:
            vezes = int(msg['text'].replace("@CookieMWbot", '').split()[1])
            vezes = max(min(20, vezes), 1)
        limite = int(msg['text'].replace("@CookieMWbot", '').split()[0][2:])
        resposta = f"(d{limite}) "
        if vezes == 1:
            resposta += f"🎲 -> {random.randint(1, limite)}"
        else:
            for vez in range(vezes):
                if language == 'pt':
                    resposta += f"\n{vez+1}º Lançamento: 🎲 -> {random.randint(1, limite)}"
                else:
                    resposta += f"\n{vez+1}th Roll: 🎲 -> {random.randint(1, limite)}"
        Send(cookiebot, chat_id, resposta, msg_to_reply=msg)

def Idade(cookiebot, msg, chat_id, language):
    if not " " in msg['text']:
        Send(cookiebot, chat_id, "Digite um nome, vou dizer a sua idade!\n\nEx: '/idade Mekhy'\n(obs: só o primeiro nome conta)", msg, language)
    else:
        Nome = msg['text'].replace("/idade ", '').replace("/edad", '').replace("/age", '').replace("@CookieMWbot", '').split()[0]
        response = json.loads(requests.get(f"https://api.agify.io?name={Nome}", timeout=2).text)
        Idade = response['age']
        Contagem = response['count']
        if Contagem == 0:
            Send(cookiebot, chat_id, "Não conheço esse nome!", msg, language)
        else:
            Send(cookiebot, chat_id, f"Sua idade é {Idade} anos! 👴\nRegistrado {Contagem} vezes", msg, language)

def Genero(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    if not " " in msg['text']:
        Send(cookiebot, chat_id, "Digite um nome, vou dizer o seu gênero!\n\nEx: '/genero Mekhy'\n(obs: só o primeiro nome conta)\n(obs 2: POR FAVOR NÃO LEVAR ISSO A SÉRIO, É ZUERA)", msg, language)
    else:
        Nome = msg['text'].replace("/genero ", '').replace("/gênero", '').replace("/gender", '').replace("@CookieMWbot", '').split()[0]
        response = json.loads(requests.get(f"https://api.genderize.io?name={Nome}", timeout=2).text)
        Genero = response['gender']
        Probabilidade = response['probability']
        Contagem = response['count']
        if Contagem == 0:
            Send(cookiebot, chat_id, "Não conheço esse nome!", msg, language)
        elif Genero == 'male':
            Send(cookiebot, chat_id, f"É um menino! 👨\n\nProbabilidade --> {Probabilidade*100}%\nRegistrado {Contagem} vezes", msg, language)
        elif Genero == 'female':
            Send(cookiebot, chat_id, f"É uma menina! 👩\n\nProbabilidade --> {Probabilidade*100}%\nRegistrado {Contagem} vezes", msg, language)

def Rojao(cookiebot, msg, chat_id, thread_id=None, isBombot=False):
    Send(cookiebot, chat_id, "fiiiiiiii.... ", msg_to_reply=msg)
    time.sleep(0.1)
    amount = random.randint(5, 20)
    while amount > 0:
        if random.choice([True, False]):
            n = random.randint(1, amount)
        else:
            n = 1
        Send(cookiebot, chat_id, "pra "*n, thread_id=thread_id, isBombot=isBombot)
        amount -= n
    Send(cookiebot, chat_id, "💥POOOOOOOWW💥", thread_id=thread_id, isBombot=isBombot)