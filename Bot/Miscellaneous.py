from universal_funcs import *
from Publisher import postmail_chat_link
import Distortioner
newchat_link = "https://t.me/CookieMWbot?startgroup=new"
testchat_link = "https://t.me/+mX6W3tGXPew2OTIx"
updateschannel_link = "https://t.me/cookiebotupdates"
num_chats = 615

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
                [InlineKeyboardButton(text="Canal de Atualizações 📢", url=updateschannel_link)],
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
                [InlineKeyboardButton(text="Updates Channel 📢", url=updateschannel_link)],
                [InlineKeyboardButton(text="Test/assistance Group 🧪", url=testchat_link)]
            ]))

def Privacy(cookiebot, msg, chat_id, language):
    with open('Static/privacy.html', 'r') as file:
        privacy_text = file.read()
    Send(cookiebot, chat_id, privacy_text, msg_to_reply=msg, language=language, parse_mode='HTML')

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
    ReactToMessage(msg, '🔥', isBombot=isBombot)
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    if msg['text'].lower().startswith('/patas'):
        day, month, year, directory = 18, 4, 2025, 'Static/Countdown/Patas'
        calltoaction = random.choice(['Já comprou o seu ingresso? Não perca a oportunidade de participar do maior evento furry de Sorocaba-SP!',
                                  'Este é um evento beneficiente em formato de convenção, para promover e celebrar a cultura de apreciação animais antropomóficos na região de Sorocaba. Foi criado para ajudar as entidades que prestam apoio aos idosos da região.',
                                  'O evento vai acontecer no SOROCABA PARK HOTEL, um local que oferece comodidade e conforto para todos os participantes do evento!',
                                  'As atrações incluem:\n\n-Show com Banda\n-Balada Furry com DJ\n-Pool Party com brinquedos de piscina e DJ\n-Mercadinho Furry\n-E muito mais!'])
        pic = open(directory + '/' + random.choice(os.listdir(directory)), 'rb')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days
        if daysremaining >= -5 and daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b>Faltam {number_to_emojis(daysremaining)} dias para o Patas!</b>\n\n<i>{calltoaction}</i>\n🐾🍌🐾🐒🐾🍌🐾🐒🐾🍌🐾🐒🐾🍌\n\n📆 {day} a {day+3}/{month}, Sorocaba Park Hotel\n💻 Ingressos em: patas.site\n📲 Grupo do evento: @EventoPatas"
    elif msg['text'].lower().startswith('/bff'):
        day, month, year, directory = 25, 7, 2025, 'Static/Countdown/BFF'
        calltoaction = random.choice(['O Sheraton Santos Hotel é reconhecidamente o melhor hotel de Santos. Localizado em frente ao Shopping Praiamar, o maior centro de compras da cidade, o hotel conta com ampla infraestrutura para atender o evento.',
                                  'A Brasil FurFest tem, entre outros objetivos, levantar fundos para caridade em prol do Projeto Social SOS Vida Pet Litoral, que ajuda protetores a manter abrigos para animais de rua na Baixada Santista',
                                  'Quem são os furries? O que é a Brasil FurFest? Descubra em youtube.com/watch?v=vuFGHSL8X34&ab_channel=BrasilFurFest',
                                  'Esperamos para ver todos os furries nas praias da maravilhosa cidade de Santos para essa festa que será inesquecível!',
                                  'Entre as atividades planejadas, temos atividades de social mixer (dinâmicas de grupo) no início do evento para que você engrene os primeiros contatos com os demais participantes no evento.',
                                  'Bombom nasceu na Fantástica Fábrica de Doces com intuito de reunir os furries na Brasil FurFest para muita festa e diversão. Aliás, se a festa tiver caipirinhas melhor ainda!',
                                  'Heróis e Vilões travarão uma batalha épica! Mal podemos esperar! Venha participar desta grande festa do furry fandom brasileiro com o hotel inteiro fechado para o evento!',
                                  'Mais de mil participantes! Isso mesmo: MIL! Desde 2024, batemos um recorde histórico para o furry fandom brasileiro, e tudo graças a vocês que vieram com toda a energia e alegria que só a nossa comunidade furry sabe trazer!',
                                  'Aurora Bloom virá como convidada de honra para a Brasil FurFest 2025, trazendo todo o seu charme e diversão para o evento!'])
        pic = open(directory + '/' + random.choice(os.listdir(directory)), 'rb')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days
        if daysremaining >= -5 and daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b>Faltam {number_to_emojis(daysremaining)} dias para a Brasil FurFest 2025 - Heróis & Vilões!</b>\n\n<i>{calltoaction}\n#fiquenosheraton</i>\n🐾🟩🐾🟨🐾🟩🐾🟨🐾🟩🐾🟨🐾🟩\n\n📆 {day} a {day+2}/{month}, Sheraton Santos Hotel\n💻 Ingressos à venda na porta, upgrades até 1 mês antes do evento através do email reg@brasilfurfest.com.br\n📲 Grupo do evento: @brasilfurfest"
    elif msg['text'].lower().startswith('/fursmeet'):
        day, month, year, directory = 15, 11, 2024, 'Static/Countdown/FurSMeet'
        pic = open(directory + '/' + random.choice(os.listdir(directory)), 'rb')
        calltoaction = random.choice(['O FurSMeet é uma convenção furry de 3 dias realizada em Santa Maria no Rio grande do Sul.Venha viver novas experiências, fazer amigos e se divertir muito no FurSMeet!',
                                      'A oportunidade perfeita para se conectar com outros furries, participar de atividades emocionantes e criar memórias que durarão para sempre!',
                                      'O objetivo do evento é reunir amantes da cultura antropomórfica da região Sul e de todo o Brasil para fazer novos amigos e viver grandes momentos!',
                                      'Nós não lucramos com o evento e pretendemos ajudar futuramente instituições carentes doando o dinheiro que sobra do evento.',
                                      'Por ainda ser um evento pequeno e termos opções de infraestrutura limitadas em Santa Maria, todo o valor do ingresso é investido no hotel, decorações e brindes sem sobrar dinheiro para doar por uma causa.',
                                      'O Capibára pode ter essa fuça de gaúcho rabugento, mas tem um coração grande que nem o Rio Grande do Sul. Assim como qualquer capivara ele faz amizade com qualquer um! Pode ser um gato ou um jacaré, qualquer furry é bem vindo para ser seu amigo.',
                                      'Um bom gaúcho sempre anda bem pilchado, então Capibára não dispensa sua boina, seu lenço e sua faixa pampa da cintura! Para completar ele não larga seu mate de jeito nenhum!'])
        pic = open(directory + '/' + random.choice(os.listdir(directory)), 'rb')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days
        if daysremaining >= -5 and daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b>Faltam {number_to_emojis(daysremaining)} dias para o FurSMeet 2025!</b>\n\n<i>{calltoaction}</i>\n🦕🦫🦕🦫🦕🦫🦕🦫🦕🦫🦕🦫🦕🦫\n\n📆 {day} a {day+2}/{month}, Santa Maria, Rio Grande do Sul\n💻 Informações no site: fursmeet.wixsite.com/fursmeet\n📲 Grupo do evento: @fursmeet"
    cookiebot.sendPhoto(chat_id, pic, caption=caption, reply_to_message_id=msg['message_id'], parse_mode='HTML')
    pic.close()

def Desenterrar(cookiebot, msg, chat_id, thread_id=None):
    for attempt in range(10):
        try:
            chosenid = random.randint(1, msg['message_id'])
            Forward(cookiebot, chat_id, chat_id, chosenid, thread_id=thread_id)
            return
        except:
            pass

def Morte(cookiebot, msg, chat_id, language):
    ReactToMessage(msg, '👻')
    path = 'Static/Death/' + random.choice(os.listdir('Static/Death'))
    if len(msg['text'].split()) > 1:
        caption = '💀💀💀 ' + msg['text'].split()[1]
    elif 'reply_to_message' in msg:
        caption = '💀💀💀 ' + msg['reply_to_message']['from']['first_name']
    else:
        caption = '💀💀💀 ' + '@'+msg['from']['username'] if 'username' in msg['from'] else msg['from']['first_name']
    if language == 'pt':
        caption += ' foi de ' + random.choice(['ARRASTA PRA CIMA', 'AMERICANAS', 'F NO CHAT', 'HEXA 2022', 'COMES E BEBES', 'WAKANDA FOREVER NA HORIZONTAL', 'VOLANTE NO VASCO', 'DRAKE E JOSH', 'OLAVO DE CARVALHO', 'SEGUE PRA PARTE 2', 'TELA AZUL', 'FUNDADOR DA FAROFA YOKI', 'ESTAMPA DE CAMISA', 'CPF CANCELADO', 'KICK DO SERVIDOR', 'CARRINHO BATE BATE', 'SAMBARILOVE', 'ESTUDAR EM REALENGO', 'FISH AND CHIPS', 'LINK NA BIO', 'TOBOGÃ PRO INFERNO', 'CRINJOLAS', 'FRAIDI NAITES ATE FREDE']) + '! 💀💀💀'
    else:
        caption += random.choice([' ESTÁ MORTO', ' FOI-SE EMBORA', ' FALECEU']) + '! 💀💀💀'
    with open('Static/death.txt', 'r', encoding='utf-8') as f:
        line = random.choice(f.readlines())
        line = line.replace('\n', '')
    caption += '\n\nMotivo: <b>' + line + '</b> 🔥\nF no chat. 🫡'
    if path.endswith('.gif'):
        animation = open(path, 'rb')
        SendAnimation(cookiebot, chat_id, animation, caption=caption, msg_to_reply=msg, language=language)
        animation.close()
    else:
        photo = open(path, 'rb')
        SendPhoto(cookiebot, chat_id, photo, caption=caption, msg_to_reply=msg, language=language)
        photo.close()

def Sorte(cookiebot, msg, chat_id, language):
    with open('Static/Sorte/sorte.gif', 'rb') as f:
        anim_id = SendAnimation(cookiebot, chat_id, f, msg_to_reply=msg, language=language)
    with open('Static/Sorte/sorte.txt', 'r', encoding='utf-8') as f:
        line = random.choice(f.readlines())
        line = line.replace('\n', '')
    numbers = []
    tens = []
    while len(numbers) < 6:
        number = random.randint(1, 99)
        if math.floor(number / 10) not in tens:
            numbers.append(number)
            tens.append(math.floor(number / 10))
    numbers_str = ' '.join([str(number) for number in numbers])
    answer = f'Sua sorte:\n 🥠 <span class="tg-spoiler">" {line} "</span> 🥠'
    answer += f'\nSeus números da sorte: <span class="tg-spoiler">{numbers_str}</span>'
    time.sleep(4)
    DeleteMessage(cookiebot, (str(chat_id), str(anim_id)))
    Send(cookiebot, chat_id, answer, msg_to_reply=msg, language=language, parse_mode='HTML')

def Destroy(cookiebot, msg, chat_id, language, isBombot=False):
    if language == 'pt':
        instru = "Responda a um vídeo, foto, audio, gif ou sticker com o comando para distorcer (ou use /zoar pfp)"
    else:
        instru = "Reply to a video, photo, audio, gif or sticker with the command to distort (or use /destroy pfp)"
    if msg['text'].endswith('pfp'):
        SendChatAction(cookiebot, chat_id, 'upload_photo')
        token = bombotTOKEN if isBombot else cookiebotTOKEN
        file_path_telegram = cookiebot.getFile(cookiebot.getUserProfilePhotos(msg['from']['id'])['photos'][0][-1]['file_id'])['file_path']
        r = requests.get(f"https://api.telegram.org/file/bot{token}/{file_path_telegram}", allow_redirects=True, timeout=10)
        filename = file_path_telegram.split('/')[-1]
        with open(filename, 'wb') as f:
            f.write(r.content)
        Distortioner.distortioner(filename)
        with open('distorted.jpg', 'rb') as photo:
            cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])
        os.remove('distorted.jpg')
        os.remove(filename)
    elif not 'reply_to_message' in msg:
        Send(cookiebot, chat_id, instru, msg, language)
    elif 'video' in msg['reply_to_message']:
        thismighttakeawhile = cookiebot.sendMessage(chat_id, "(hold on, this might take a while...)", reply_to_message_id=msg['message_id'])
        SendChatAction(cookiebot, chat_id, 'upload_video')
        video_file = GetMediaContent(cookiebot, msg['reply_to_message'], 'video', isBombot=isBombot, downloadfile=True)
        Distortioner.distortioner(video_file)
        with open('distorted.mp4', 'rb') as video:
            cookiebot.sendVideo(chat_id, video, reply_to_message_id=msg['message_id'])
        cookiebot.deleteMessage((chat_id, thismighttakeawhile['message_id']))
        os.remove('distorted.mp4')
        os.remove(video_file)
    elif 'photo' in msg['reply_to_message']:
        SendChatAction(cookiebot, chat_id, 'upload_photo')
        photo_file = GetMediaContent(cookiebot, msg['reply_to_message'], 'photo', isBombot=isBombot, downloadfile=True)
        Distortioner.distortioner(photo_file)
        with open('distorted.jpg', 'rb') as photo:
            cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])
        os.remove('distorted.jpg')
        os.remove(photo_file)
    elif 'audio' in msg['reply_to_message'] or 'voice' in msg['reply_to_message']:
        SendChatAction(cookiebot, chat_id, 'upload_voice')
        if 'audio' in msg['reply_to_message']:
            audio_file = GetMediaContent(cookiebot, msg['reply_to_message'], 'audio', isBombot=isBombot, downloadfile=True)
        else:
            audio_file = GetMediaContent(cookiebot, msg['reply_to_message'], 'voice', isBombot=isBombot, downloadfile=True)
        Distortioner.distort_audiofile(audio_file, 10, 1, 'distorted.mp3')
        with open('distorted.mp3', 'rb') as audio:
            cookiebot.sendAudio(chat_id, audio, reply_to_message_id=msg['message_id'])
        os.remove('distorted.mp3')
        os.remove(audio_file)
    elif 'sticker' in msg['reply_to_message']:
        SendChatAction(cookiebot, chat_id, 'upload_photo')
        sticker_file = GetMediaContent(cookiebot, msg['reply_to_message'], 'sticker', isBombot=isBombot, downloadfile=True)
        Distortioner.process_image(sticker_file, 'distorted.png', 25)
        with open('distorted.png', 'rb') as sticker:
            cookiebot.sendSticker(chat_id, sticker, reply_to_message_id=msg['message_id'])
        os.remove('distorted.png')
        os.remove(sticker_file)
    elif 'animation' in msg['reply_to_message']:
        SendChatAction(cookiebot, chat_id, 'upload_video')
        animation_file = GetMediaContent(cookiebot, msg['reply_to_message'], 'animation', isBombot=isBombot, downloadfile=True)
        Distortioner.distortioner(animation_file, is_gif=True)
        with open('distorted.mp4', 'rb') as animation:
            cookiebot.sendAnimation(chat_id, animation, reply_to_message_id=msg['message_id'])
        os.remove('distorted.mp4')
        os.remove(animation_file)
    else:
        Send(cookiebot, chat_id, instru, msg, language)