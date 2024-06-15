from universal_funcs import *
from Publisher import postmail_chat_link
newchat_link = "https://t.me/CookieMWbot?startgroup=new"
testchat_link = "https://t.me/+mX6W3tGXPew2OTIx"
num_chats = 566

def decapitalize(s, upper_rest = False):
  return ''.join([s[:1].lower(), (s[1:].upper() if upper_rest else s[1:])])

def PvDefaultMessage(cookiebot, msg, chat_id, isBombot):
    if 'language_code' in msg['from'] and msg['from']['language_code'] in ['pt', 'pt-BR', 'pt-br', 'pt_PT', 'pt-pt']:
        if isBombot:
            Send(cookiebot, chat_id, "*Olá, eu sou o BomBot\!*\nSou um clone do @CookieMWbot criado para os grupos da Brasil FurFest \(BFF\)\n\nSe tiver alguma dúvida ou quiser a lista completa de comandos, mande uma mensagem para @MekhyW")
        else:
            Send(cookiebot, chat_id, f"*Olá, eu sou o CookieBot\!*\n\nAtualmente estou presente em {number_to_emojis(num_chats)} grupos ativos\!\nSinta\-se livre para me adicionar ao seu \:\)\n\nSou um bot com IA de Conversação, Defesa de Grupo, Pesquisa, Conteúdo Personalizado e Publicação Automática\.\nUse /configurar para alterar minhas configurações \(incluindo idioma\)\nUse /comandos para ver todas as minhas funcionalidades\n\nSe tiver alguma dúvida ou quiser algo adicionado, mande uma mensagem para @MekhyW",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Adicionar a um Grupo 👋", url=newchat_link)],
                [InlineKeyboardButton(text="Mural de Divulgações 📬", url=postmail_chat_link)],
                [InlineKeyboardButton(text="Grupo de teste/assistência 🧪", url=testchat_link)]
            ]))
    else:
        if isBombot:
            Send(cookiebot, chat_id, "*Hello, I'm BomBot\!*\nI'm a clone of @CookieMWbot created for Brasil FurFest \(BFF\) chats\n\nIf you have any questions or want the complete list of commands, send a message to @MekhyW")
        else:
            Send(cookiebot, chat_id, f"*Hello, I'm CookieBot\!*\n\nI'm currently present in {number_to_emojis(num_chats)} active chats\!\nYou can add me to your \:\)\n\nI'm an AI Conversation, Group Defense, Search, Custom Content and Automated Publication bot\.\nUse /configurar to change my settings \(including language\)\nUse /comandos to see all my features\n\nIf you have any questions or want something added, send a message to @MekhyW",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Add me to a Group 👋", url=newchat_link)],
                [InlineKeyboardButton(text="Shared Posts 📬", url=postmail_chat_link)],
                [InlineKeyboardButton(text="Test/assistance Group 🧪", url=testchat_link)]
            ]))


def TaVivo(cookiebot, msg, chat_id, language, isBombot=False):
    ReactToMessage(msg, '👍', isBombot=isBombot)
    Send(cookiebot, chat_id, "*Estou vivo*\n\nPing enviado em\:\n" + str(datetime.datetime.now()), msg, language)

def Analyze(cookiebot, msg, chat_id, language, isBombot=False):
    if not 'reply_to_message' in msg:
        Send(cookiebot, chat_id, "Responda uma mensagem com o comando para analisar", msg, language)
        return
    ReactToMessage(msg, '🤔', isBombot=isBombot)
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
    with open(f"Static/Cookiebot_functions_{language}.txt", "r+", encoding='utf8') as text_file:
        string = text_file.read()
    Send(cookiebot, chat_id, string, msg_to_reply=msg)

def NotifyFunOff(cookiebot, msg, chat_id, language):
    Send(cookiebot, chat_id, "_Funções de diversão estão desativadas nesse chat_", msg, language)

def IdeiaDesenho(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    ideiasdesenho = os.listdir('Static/IdeiaDesenho')
    ideiaID = random.randint(0, len(ideiasdesenho)-1)
    photo = open('Static/IdeiaDesenho'+'/'+ideiasdesenho[ideiaID], 'rb')
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
    images = os.listdir("Static/Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", ''))
    imageID = random.randint(0, len(images)-1)
    photo = open("Static/Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')+'/'+images[imageID], 'rb')
    SendPhoto(cookiebot, chat_id, photo, msg_to_reply=msg)
    photo.close()

def Dado(cookiebot, msg, chat_id, language):
    if msg['text'].startswith("/dado"):
        Send(cookiebot, chat_id, "Rodo um dado de 1 até x, n vezes\n>EXEMPLO\: /d20 5\n>\(Roda um d20 5 vezes\)")
    elif msg['text'].startswith("/dice"):
        Send(cookiebot, chat_id, "Roll a dice from 1 to x, n times\n>EXAMPLE\: /d20 5\n>\(Rolls a d20 5 times\)")
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
        Send(cookiebot, chat_id, "Digite um nome, vou dizer a sua idade!\n>Exemplo\: '/idade Mekhy'\n>\(obs\: só o primeiro nome conta\)", msg, language)
    else:
        Nome = msg['text'].replace("/idade ", '').replace("/edad ", '').replace("/age ", '').replace("/idade@CookieMWbot", '').replace("/age@CookieMWbot", '').replace("/edad@CookieMWbot", '').split()[0]
        response = json.loads(requests.get(f"https://api.agify.io?name={Nome}", timeout=10).text)
        Idade = response['age']
        Contagem = response['count']
        if Contagem == 0:
            Send(cookiebot, chat_id, "Não conheço esse nome\!", msg, language)
        else:
            Send(cookiebot, chat_id, f"Sua idade é ||{Idade} anos\! 👴||\nRegistrado *{Contagem}* vezes", msg, language)

def Genero(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    if not " " in msg['text']:
        Send(cookiebot, chat_id, "Digite um nome, vou dizer o seu gênero\!\n>Exemplo\: '/genero Mekhy'\n>\(obs\: só o primeiro nome conta\)\n>\(obs 2\: POR FAVOR NÃO LEVAR ISSO A SÉRIO, É ZUERA\)", msg, language)
    else:
        Nome = msg['text'].replace("/genero ", '').replace("/gênero ", '').replace("/gender ", '').replace("/genero@CookieMWbot", '').replace("/gênero@CookieMWbot", '').replace("/gender@CookieMWbot", '').split()[0]
        response = json.loads(requests.get(f"https://api.genderize.io?name={Nome}", timeout=10).text)
        Genero = response['gender']
        Probabilidade = response['probability']
        Contagem = response['count']
        if Contagem == 0:
            Send(cookiebot, chat_id, "Não conheço esse nome\!", msg, language)
        elif Genero == 'male':
            Send(cookiebot, chat_id, f"É ||um menino\! 👨||\n\nProbabilidade \-\-\> {Probabilidade*100}%\nRegistrado {Contagem} vezes", msg, language)
        elif Genero == 'female':
            Send(cookiebot, chat_id, f"É ||uma menina\! 👩||\n\nProbabilidade \-\-\> {Probabilidade*100}%\nRegistrado {Contagem} vezes", msg, language)

def Rojao(cookiebot, msg, chat_id, thread_id=None, isBombot=False):
    ReactToMessage(msg, '🎉', isBombot=isBombot)
    Send(cookiebot, chat_id, "fiiiiiiii\.\.\.\. ", msg_to_reply=msg)
    time.sleep(0.1)
    amount = random.randint(5, 20)
    while amount > 0:
        if random.choice([True, False]):
            n = random.randint(1, amount)
        else:
            n = 1
        Send(cookiebot, chat_id, "pra "*n, thread_id=thread_id, isBombot=isBombot)
        amount -= n
    Send(cookiebot, chat_id, "*💥POOOOOOOWW💥*", thread_id=thread_id, isBombot=isBombot)

def Reclamacao(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    if language == 'pt':
        with open('Static/reclamacao/milton_pt.jpg', 'rb') as photo:
            SendPhoto(cookiebot, chat_id, photo, 
                      caption=f"Bom dia/tarde/noite, {msg['from']['first_name']},\nCaso tenha alguma reclamação, fique à vontade para responder essa mensagem. Se não, seguimos com nossas atividades.\nAtenciosamente,\nMilton do RH.", 
                      msg_to_reply=msg)
    else:
        with open('Static/reclamacao/milton_eng.jpg', 'rb') as photo:
            SendPhoto(cookiebot, chat_id, photo, 
                      caption=f"Good morning/afternoon/evening, {msg['from']['first_name']},\nIf you have any complaints, feel free to reply to this message. If not, we continue with our activities.\nSincerely,\nMilton from HR.", 
                      msg_to_reply=msg)
            
def ReclamacaoAnswer(cookiebot, msg, chat_id, language):
    DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))
    SendChatAction(cookiebot, chat_id, 'upload_audio')
    protocol = f"{random.randint(10, 99)}-{random.randint(100000, 999999)}/{datetime.datetime.now().year}"
    with open(f"Static/reclamacao/{random.choice([file for file in os.listdir('Static/reclamacao') if file.endswith('.wav')])}", 'rb') as hold_audio:
        hold_msg = cookiebot.sendVoice(chat_id, hold_audio, caption=f"Protocol: {protocol}", reply_to_message_id=msg['message_id'])
    time.sleep(random.randint(10, 20))
    DeleteMessage(cookiebot, telepot.message_identifier(hold_msg))
    with open('Static/reclamacao/answers.txt', 'r', encoding='utf8') as answers:
        answer = random.choice(answers.readlines()).replace('\n', '')
        answer += '\n\nAtenciosamente,\nMilton do RH.'
    Send(cookiebot, chat_id, answer, msg_to_reply=msg, language=language)

def Countdown(cookiebot, msg, chat_id, language, isBombot):
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    if msg['text'].lower().startswith('/patas'):
        directory = 'Static/Countdown/Patas'
        pic = open(directory + '/' + random.choice(os.listdir(directory)), 'rb')
        calltoaction = random.choice(['Já comprou o seu ingresso? Não perca a oportunidade de participar do maior evento furry de Sorocaba-SP\!',
                                  'Este é um evento beneficiente em formato de convenção, para promover e celebrar a cultura de apreciação animais antropomóficos na região de Sorocaba. Foi criado para ajudar as entidades que prestam apoio aos idosos da região.',
                                  'O evento vai acontecer no SOROCABA PARK HOTEL, um local que oferece comodidade e conforto para todos os participantes do evento\!',
                                  'As atrações incluem:\n\n-Show com Banda\n-Balada Furry com DJ\n-Pool Party com brinquedos de piscina e DJ\n-Mercadinho Furry\n-E muito mais\!'])
        day, month = 18, 4
        daysremaining = (datetime.datetime(datetime.datetime.now().year, month, day) - datetime.datetime.now()).days
        if daysremaining < 0:
            daysremaining += 365
        caption = f"*Faltam {number_to_emojis(daysremaining)} dias para o Patas\!*\n\n_{calltoaction}_\n🐾🍌🐾🐒🐾🍌🐾🐒🐾🍌🐾🐒🐾🍌\n\n📆 {day} a {day+3}/{month}, Sorocaba Park Hotel\n💻 Ingressos em: patas.site\n📲 Grupo do evento: @bananaa2024"
    elif msg['text'].lower().startswith('/bff'):
        directory = 'Static/Countdown/BFF'
        pic = open(directory + '/' + random.choice(os.listdir(directory)), 'rb')
        calltoaction = random.choice(['O Sheraton Santos Hotel é reconhecidamente o melhor hotel de Santos. Localizado em frente ao Shopping Praiamar, o maior centro de compras da cidade, o hotel conta com ampla infraestrutura para atender o evento.',
                                  'A Brasil FurFest tem, entre outros objetivos, levantar fundos para caridade em prol do Projeto Social SOS Vida Pet Litoral, que ajuda protetores a manter abrigos para animais de rua na Baixada Santista',
                                  'Um Hotel Mal-Assombrado repleto de muita diversão! A sétima edição da Brasil FurFest será incrível! Venha participar desta grande festa do furry fandom brasileiro com o hotel inteiro fechado para o evento\!',
                                  'Esperamos para ver todos os furries nas praias da maravilhosa cidade de Santos para essa festa que será inesquecível\!',
                                  'Entre as atividades planejadas, temos atividades de social mixer (dinâmicas de grupo) no início do evento para que você engrene os primeiros contatos com os demais participantes no evento.',
                                  'Bombom nasceu na Fantástica Fábrica de Doces com intuito de reunir os furries na Brasil FurFest para muita festa e diversão. Aliás, se a festa tiver caipirinhas melhor ainda\!'])
        day, month = 19, 7
        daysremaining = (datetime.datetime(datetime.datetime.now().year, month, day) - datetime.datetime.now()).days
        if daysremaining < 0:
            daysremaining += 365
        caption = f"*Faltam {number_to_emojis(daysremaining)} dias para a Brasil FurFest\!*\n\n_{calltoaction}_\n🐾🟩🐾🟨🐾🟩🐾🟨🐾🟩🐾🟨🐾🟩\n\n📆 {day} a {day+2}/{month}, Sheraton Santos Hotel\n💻 Ingressos em: brasilfurfest.com.br\n📲 Grupo do evento: @brasilfurfest\n👾 Discord: discord.gg/ztABTT737H\n🎥 YouTube: youtube.com/brasilfurfest"
    cookiebot.sendPhoto(chat_id, pic, caption=caption, reply_to_message_id=msg['message_id'], parse_mode='MarkdownV2')
