import random
import json
import os
import time
import math
import datetime
import requests
from universal_funcs import get_request_backend, send_message, delete_message, storage_bucket, send_photo, send_chat_action, react_to_message, forward_message, number_to_emojis, wait_open, get_media_content, get_bot_token, send_animation
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from Publisher import POSTMAIL_CHAT_LINK
import Distortioner
bloblist_ideiadesenho = list(storage_bucket.list_blobs(prefix="IdeiaDesenho"))
bloblist_death = list(storage_bucket.list_blobs(prefix="Death"))
bloblist_bff = list(storage_bucket.list_blobs(prefix="Countdown/BFF"))
bloblist_patas = list(storage_bucket.list_blobs(prefix="Countdown/Patas"))
bloblist_fursmeet = list(storage_bucket.list_blobs(prefix="Countdown/FurSMeet"))
bloblist_trex = list(storage_bucket.list_blobs(prefix="Countdown/Trex"))
custom_commands = list(dict.fromkeys([folder.name.split('/')[1] for folder in storage_bucket.list_blobs(prefix="Custom/")]))
print("Custom commands: " + str(custom_commands))
NEW_CHAT_LINK = "https://t.me/CookieMWbot?startgroup=new"
TEST_CHAT_LINK = "https://t.me/+mX6W3tGXPew2OTIx"
UPDATES_CHANNEL_LINK = "https://t.me/cookiebotupdates"
NUMBER_CHATS = 756

def decapitalize(s, upper_rest = False):
    return ''.join([s[:1].lower(), (s[1:].upper() if upper_rest else s[1:])])

def pv_default_message(cookiebot, msg, chat_id, is_alternate_bot):
    send_chat_action(cookiebot, chat_id, 'typing')
    is_portuguese = 'language_code' in msg['from'] and msg['from']['language_code'] in ['pt', 'pt-BR', 'pt-br', 'pt_PT', 'pt-pt']
    bot_identities = {
        1: {
            'name': 'BomBot',
            'description_pt': "Sou um clone do @CookieMWbot criado para os grupos da Brasil FurFest (BFF)",
            'description_en': "I'm a clone of @CookieMWbot created for Brasil FurFest (BFF) chats",
        },
        2: {
            'name': 'Pawsy',
            'description_pt': "Sou um clone do @CookieMWbot criado para os grupos do Pawstral, evento furry que ocorre no Chile!",
            'description_en': "I'm a clone of @CookieMWbot created for the groups of Pawstral, a furry event that takes place in Chile!",
        },
        3 : {
            'name': 'TarinBot',
            'description_pt': "Sou um clone do @CookieMWbot criado para os grupo estadual de furries de Santa Catarina, o SCFurs (Santa Catarina Furries)",
            'description_en': "I'm a clone of @CookieMWbot created for the state group of furries from Santa Catarina (Brazil), SCFurs (Santa Catarina Furries)",
        },
        4 : {
            'name': 'ConnectBot',
            'description_pt': "Sou um clone do @CookieMWbot desenvolvido para o evento FurConect em Goiás!",
            'description_en': "I'm a clone of @CookieMWbot developed for the FurConect event in Goiás (Brazil)!",
        },
        'default': {
            'name': 'CookieBot',
            'description_pt': f"Atualmente estou presente em {number_to_emojis(NUMBER_CHATS)} grupos ativos! Sinta-se livre para me adicionar ao seu :)",
            'description_en': f"I'm currently present in {number_to_emojis(NUMBER_CHATS)} active chats! You can add me to your :)",
            'additional_info': "Sou um bot com IA de Conversação, Defesa de Grupo, Pesquisa, Conteúdo Personalizado e Publicação Automática.",
            'additional_info_en': "I'm an AI Conversation, Group Defense, Search, Custom Content and Automated Publication bot.",
            'commands': "/configurar para alterar minhas configurações (incluindo idioma)\nUse /comandos para ver todas as minhas funcionalidades",
            'commands_en': "/configurar to change my settings (including language)\nUse /comandos to see all my features"
        }
    }
    bot = bot_identities.get(is_alternate_bot, bot_identities['default'])
    name = bot['name']
    description = bot['description_pt'] if is_portuguese else bot['description_en']
    additional_info = bot.get('additional_info', '')
    additional_info_en = bot.get('additional_info_en', '')
    commands = bot.get('commands', '')
    commands_en = bot.get('commands_en', '')
    if bot == bot_identities['default']:
        message = (f"*Olá, eu sou o {name}!*\n\n{description}\n\n{additional_info}\n"
                   f"{commands}\n\nSe tiver alguma dúvida ou quiser algo adicionado, mande uma mensagem para @MekhyW") \
            if is_portuguese else \
            (f"*Hello, I'm {name}!* \n\n{description}\n\n{additional_info_en}\n"
             f"{commands_en}\n\nIf you have any questions or want something added, send a message to @MekhyW")
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Adicionar a um Grupo 👋" if is_portuguese else "Add me to a Group 👋", url=NEW_CHAT_LINK)],
            [InlineKeyboardButton(text="Mural de Divulgações 📬" if is_portuguese else "Shared Posts 📬", url=POSTMAIL_CHAT_LINK)],
            [InlineKeyboardButton(text="Canal de Atualizações 📢" if is_portuguese else "Updates Channel 📢", url=UPDATES_CHANNEL_LINK)],
            [InlineKeyboardButton(text="Grupo de teste/assistência 🧪" if is_portuguese else "Test/assistance Group 🧪", url=TEST_CHAT_LINK)]
        ])
    else:
        message = f"*Olá, eu sou o {name}!*\n{description}\n\nSe tiver alguma dúvida ou quiser a lista completa de comandos, mande uma mensagem para @MekhyW" \
            if is_portuguese else \
            f"*Hello, I'm {name}!*\n{description}\n\nIf you have any questions or want the complete list of commands, send a message to @MekhyW"
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Mural de Divulgações 📬" if is_portuguese else "Shared Posts 📬", url=POSTMAIL_CHAT_LINK)],
            [InlineKeyboardButton(text="Canal de Atualizações 📢" if is_portuguese else "Updates Channel 📢", url=UPDATES_CHANNEL_LINK)],
            [InlineKeyboardButton(text="Grupo de teste/assistência 🧪" if is_portuguese else "Test/assistance Group 🧪", url=TEST_CHAT_LINK)]
        ])
    send_message(cookiebot, chat_id, message, reply_markup=reply_markup)

def privacy_statement(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    with open('Static/privacy.html', 'r', encoding='utf-8') as file:
        privacy_text = file.read()
    send_message(cookiebot, chat_id, privacy_text, msg_to_reply=msg, language=language, parse_mode='HTML')

def is_alive(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    react_to_message(msg, '👍', is_alternate_bot=is_alternate_bot)
    send_chat_action(cookiebot, chat_id, 'typing')
    send_message(cookiebot, chat_id, "<b>Estou vivo</b>\n\nPing enviado em:\n" + str(datetime.datetime.now()), msg, language)

def analyze(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if not 'reply_to_message' in msg:
        send_message(cookiebot, chat_id, "Responda uma mensagem com o comando para analisar", msg, language)
        return
    react_to_message(msg, '🤔', is_alternate_bot=is_alternate_bot)
    result = ''
    for item in msg['reply_to_message']:
        result += str(item) + ': ' + str(msg['reply_to_message'][item]) + '\n'
    send_message(cookiebot, chat_id, result, msg_to_reply=msg)

def list_groups(cookiebot, chat_id):
    send_chat_action(cookiebot, chat_id, 'typing')
    file_path = 'list_groups.json'
    existing_chats, new_chats, removed_chats = [], [], []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf8') as file:
            try:
                existing_chats = json.load(file)
            except json.JSONDecodeError:
                pass
    groups = get_request_backend('registers')
    for group in groups:
        try:
            chat = cookiebot.getChat(int(group['id']))
            time.sleep(0.2)
            if 'title' in chat:
                chat_info = f"{group['id']} - {chat['title']}"
                if not any(chat.startswith(chat_info.split()[0]) for chat in existing_chats):
                    new_chats.append(chat_info)
                cookiebot.sendMessage(chat_id, chat_info)
        except Exception:
            print("Group not found: " + group['id'])
            removed_chats.append(group['id'])
    cookiebot.sendMessage(chat_id, f"Total groups found: {len(groups) - len(removed_chats)}")
    with open(file_path, 'w', encoding='utf8') as file:
        json.dump([f"{group['id']} - {group.get('title', '')}" for group in groups], file)
    if new_chats:
        cookiebot.sendMessage(chat_id, f"New groups found: {', '.join(new_chats)}")
    if removed_chats:
        cookiebot.sendMessage(chat_id, f"Removed groups: {', '.join(removed_chats)}")

def broadcast_message(cookiebot, msg):
    groups = get_request_backend('registers')
    for group in groups:
        try:
            group_id = group['id']
            send_message(cookiebot, int(group_id), msg['text'].replace('/broadcast', ''))
            time.sleep(0.5)
        except Exception:
            pass

def list_commands(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    wait_open(f"Static/Cookiebot_functions_{language}.txt")
    with open(f"Static/Cookiebot_functions_{language}.txt", "r+", encoding='utf8') as text_file:
        string = text_file.read()
    send_message(cookiebot, chat_id, string, msg_to_reply=msg)

def notify_fun_off(cookiebot, msg, chat_id, language):
    send_message(cookiebot, chat_id, "<i>Funções de diversão estão desativadas nesse chat</i>", msg, language)

def drawing_idea(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    idea_id = random.randint(0, len(bloblist_ideiadesenho)-1)
    blob = bloblist_ideiadesenho[idea_id]
    photo = blob.generate_signed_url(datetime.timedelta(minutes=15), method='GET')
    if language == 'pt':
        caption = f"Referência com ID {idea_id}\n\nNão trace sem dar créditos! (use a busca reversa do google images)"
    elif language == 'es':
        caption = f"Referencia con ID {idea_id}\n\n¡No rastrear sin dar créditos! (utilice la búsqueda inversa de imágenes de Google)"
    else:
        caption = f"Reference ID {idea_id}\n\nDo not trace without credits! (use the reverse google images search)"
    send_photo(cookiebot, chat_id, photo, caption=caption, msg_to_reply=msg)

def pesh(cookiebot, msg, chat_id, language, photo, image_id):
    with open('Static/pesh.txt', 'r', encoding='utf8') as file:
        species = random.choice(file.readlines()).replace('\n', '')
    caption = f"Pesh com ID {image_id}\n🐟 Seu glub glub da sorte: <b>{species}</b> 🐟"
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Pesh Gang", url=f"https://t.me/peshspecies")]])
    send_photo(cookiebot, chat_id, photo, caption=caption, reply_markup=inline_keyboard, msg_to_reply=msg, language=language)

def custom_command(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    bloblist = list(storage_bucket.list_blobs(prefix="Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '').split()[0]))
    if len(msg['text'].split()) > 1 and msg['text'].split()[1].isdigit():
        image_id = int(msg['text'].split()[1])
    else:
        image_id = random.randint(0, len(bloblist)-1)
    photo = bloblist[image_id].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
    if msg['text'].startswith("/pesh"):
        pesh(cookiebot, msg, chat_id, language, photo, image_id)
        return
    caption = f"Foto custom de {msg['text'].replace('/', '').replace('@CookieMWbot', '').split()[0].capitalize()} com ID {image_id}"
    send_photo(cookiebot, chat_id, photo, msg_to_reply=msg, caption=caption, language=language)

def roll_dice(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    if msg['text'].startswith("/dado"):
        send_message(cookiebot, chat_id, "Rodo um dado de 1 até x, n vezes\n<blockquote>EXEMPLO: /d20 5\nRoda um d20 5 vezes</blockquote>")
    elif msg['text'].startswith("/dice"):
        send_message(cookiebot, chat_id, "Roll a dice from 1 to x, n times\n<blockquote>EXAMPLE: /d20 5\nRolls a d20 5 times</blockquote>")
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
        send_message(cookiebot, chat_id, resposta, msg_to_reply=msg)

def age(cookiebot, msg, chat_id, language):
    if not " " in msg['text']:
        send_message(cookiebot, chat_id, "Digite um nome, vou dizer a sua idade!\n<blockquote>Exemplo: '/idade Mekhy'\n(obs: só o primeiro nome conta)</blockquote>", msg, language)
    else:
        nome = msg['text'].replace("/idade ", '').replace("/edad ", '').replace("/age ", '').replace("/idade@CookieMWbot", '').replace("/age@CookieMWbot", '').replace("/edad@CookieMWbot", '').split()[0]
        response = json.loads(requests.get(f"https://api.agify.io?name={nome}", timeout=10).text)
        idade = response['age']
        registered_times = response['count']
        if registered_times == 0:
            send_message(cookiebot, chat_id, "Não conheço esse nome!", msg, language)
        else:
            send_message(cookiebot, chat_id, f'Sua idade é <span class="tg-spoiler">{idade} anos! 👴</span>\nRegistrado <b>{registered_times}</b> vezes', msg, language)

def gender(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    if not " " in msg['text']:
        send_message(cookiebot, chat_id, "Digite um nome, vou dizer o seu gênero!\n<blockquote>Exemplo: '/genero Mekhy'\n(obs: só o primeiro nome conta)\n(obs 2: POR FAVOR NÃO LEVAR ISSO A SÉRIO, É ZUERA)</blockquote>", msg, language)
    else:
        nome = msg['text'].replace("/genero ", '').replace("/gênero ", '').replace("/gender ", '').replace("/genero@CookieMWbot", '').replace("/gênero@CookieMWbot", '').replace("/gender@CookieMWbot", '').split()[0]
        response = json.loads(requests.get(f"https://api.genderize.io?name={nome}", timeout=10).text)
        genero = response['gender']
        probability = response['probability']
        registered_times = response['count']
        if registered_times == 0:
            send_message(cookiebot, chat_id, "Não conheço esse nome!", msg, language)
        elif genero == 'male':
            send_message(cookiebot, chat_id, f'É <span class="tg-spoiler">um menino! 👨</span> \n\nProbabilidade --> {probability*100}%\nRegistrado {registered_times} vezes', msg, language)
        elif genero == 'female':
            send_message(cookiebot, chat_id, f'É <span class="tg-spoiler">uma menina! 👩</span> \n\nProbabilidade --> {probability*100}%\nRegistrado {registered_times} vezes', msg, language)

def firecracker(cookiebot, msg, chat_id, thread_id=None, is_alternate_bot=0):
    react_to_message(msg, '🎉', is_alternate_bot=is_alternate_bot)
    send_message(cookiebot, chat_id, "fiiiiiiii.... ", msg_to_reply=msg)
    time.sleep(0.1)
    amount = random.randint(5, 20)
    while amount > 0:
        if random.choice([True, False]):
            n = random.randint(1, amount)
        else:
            n = 1
        send_message(cookiebot, chat_id, "pra "*n, thread_id=thread_id, is_alternate_bot=is_alternate_bot)
        amount -= n
    send_message(cookiebot, chat_id, "<b>💥POOOOOOOWW💥</b>", thread_id=thread_id, is_alternate_bot=is_alternate_bot)

def complaint(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    if language == 'pt':
        with open('Static/reclamacao/milton_pt.jpg', 'rb') as photo:
            send_photo(cookiebot, chat_id, photo,
                      caption=f"Bom dia/tarde/noite, {msg['from']['first_name']},\nCaso tenha alguma reclamação, fique à vontade para responder essa mensagem. Se não, seguimos com nossas atividades.\nAtenciosamente,\nMilton do RH.",
                      msg_to_reply=msg)
    else:
        with open('Static/reclamacao/milton_eng.jpg', 'rb') as photo:
            send_photo(cookiebot, chat_id, photo,
                      caption=f"Good morning/afternoon/evening, {msg['from']['first_name']},\nIf you have any complaints, feel free to reply to this message. If not, we continue with our activities.\nSincerely,\nMilton from HR.",
                      msg_to_reply=msg)

def complaint_answer(cookiebot, msg, chat_id, language):
    delete_message(cookiebot, telepot.message_identifier(msg['reply_to_message']))
    send_chat_action(cookiebot, chat_id, 'upload_audio')
    protocol = f"{random.randint(10, 99)}-{random.randint(100000, 999999)}/{datetime.datetime.now().year}"
    with open(f"Static/reclamacao/{random.choice([file for file in os.listdir('Static/reclamacao') if file.endswith('.wav')])}", 'rb') as hold_audio:
        hold_msg = cookiebot.sendVoice(chat_id, hold_audio, caption=f"Protocol: {protocol}", reply_to_message_id=msg['message_id'])
    time.sleep(random.randint(10, 20))
    delete_message(cookiebot, telepot.message_identifier(hold_msg))
    with open('Static/reclamacao/answers.txt', 'r', encoding='utf8') as answers:
        answer = random.choice(answers.readlines()).replace('\n', '')
        answer += '\n\nAtenciosamente,\nMilton do RH.'
    send_message(cookiebot, chat_id, answer, msg_to_reply=msg, language=language)

def event_countdown(cookiebot, msg, chat_id, language, is_alternate_bot):
    react_to_message(msg, '🔥', is_alternate_bot=is_alternate_bot)
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    if msg['text'].lower().startswith('/patas'):
        day, month, year = 18, 4, 2025
        calltoaction = random.choice(['Já comprou o seu ingresso? Não perca a oportunidade de participar do maior evento furry de Sorocaba-SP!',
                                  'Este é um evento beneficiente em formato de convenção, para promover e celebrar a cultura de apreciação animais antropomóficos na região de Sorocaba. Foi criado para ajudar as entidades que prestam apoio aos idosos da região.',
                                  'O evento vai acontecer no SOROCABA PARK HOTEL, um local que oferece comodidade e conforto para todos os participantes do evento!',
                                  'As atrações incluem:\n\n-Show com Banda\n-Balada Furry com DJ\n-Pool Party com brinquedos de piscina e DJ\n-Mercadinho Furry\n-E muito mais!'])
        pic = bloblist_patas[random.randint(0, len(bloblist_patas)-1)].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b>Faltam {number_to_emojis(daysremaining)} dias para o Patas!</b>\n\n<i>{calltoaction}</i>\n🐾🍌🐾🐒🐾🍌🐾🐒🐾🍌🐾🐒🐾🍌\n\n📆 {day} a {day+3}/{month}, Sorocaba Park Hotel\n💻 Ingressos em: patas.site\n📲 Grupo do evento: @EventoPatas"
    elif msg['text'].lower().startswith('/bff'):
        day, month, year = 25, 7, 2025
        calltoaction = random.choice(['O Sheraton Santos Hotel é reconhecidamente o melhor hotel de Santos. Localizado em frente ao Shopping Praiamar, o maior centro de compras da cidade, o hotel conta com ampla infraestrutura para atender o evento.',
                                  'A Brasil FurFest tem, entre outros objetivos, levantar fundos para caridade em prol do Projeto Social SOS Vida Pet Litoral, que ajuda protetores a manter abrigos para animais de rua na Baixada Santista',
                                  'Quem são os furries? O que é a Brasil FurFest? Descubra em youtube.com/watch?v=vuFGHSL8X34&ab_channel=BrasilFurFest',
                                  'Esperamos para ver todos os furries nas praias da maravilhosa cidade de Santos para essa festa que será inesquecível!',
                                  'Entre as atividades planejadas, temos atividades de social mixer (dinâmicas de grupo) no início do evento para que você engrene os primeiros contatos com os demais participantes no evento.',
                                  'Bombom nasceu na Fantástica Fábrica de Doces com intuito de reunir os furries na Brasil FurFest para muita festa e diversão. Aliás, se a festa tiver caipirinhas melhor ainda!',
                                  'Heróis e Vilões travarão uma batalha épica! Mal podemos esperar! Venha participar desta grande festa do furry fandom brasileiro com o hotel inteiro fechado para o evento!',
                                  'Mais de mil participantes! Isso mesmo: MIL! Desde 2024, batemos um recorde histórico para o furry fandom brasileiro, e tudo graças a vocês que vieram com toda a energia e alegria que só a nossa comunidade furry sabe trazer!',
                                  'Aurora Bloom virá como convidada de honra para a Brasil FurFest 2025, trazendo todo o seu charme e diversão para o evento!'])
        pic = bloblist_bff[random.randint(0, len(bloblist_bff)-1)].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b>Faltam {number_to_emojis(daysremaining)} dias para a Brasil FurFest 2025 - Heróis & Vilões!</b>\n\n<i>{calltoaction}\n#fiquenosheraton</i>\n🐾🟩🐾🟨🐾🟩🐾🟨🐾🟩🐾🟨🐾🟩\n\n📆 {day} a {day+2}/{month}, Sheraton Santos Hotel\n💻 Ingressos a partir de 15 de setembro, upgrades até 1 mês antes do evento através do email reg@brasilfurfest.com.br\n📲 Grupo do evento: @brasilfurfest"
    elif msg['text'].lower().startswith('/fursmeet'):
        day, month, year = 15, 11, 2024
        calltoaction = random.choice(['O FurSMeet é uma convenção furry de 3 dias realizada em Santa Maria no Rio grande do Sul.Venha viver novas experiências, fazer amigos e se divertir muito no FurSMeet!',
                                      'A oportunidade perfeita para se conectar com outros furries, participar de atividades emocionantes e criar memórias que durarão para sempre!',
                                      'O objetivo do evento é reunir amantes da cultura antropomórfica da região Sul e de todo o Brasil para fazer novos amigos e viver grandes momentos!',
                                      'Nós não lucramos com o evento e pretendemos ajudar futuramente instituições carentes doando o dinheiro que sobra do evento.',
                                      'Por ainda ser um evento pequeno e termos opções de infraestrutura limitadas em Santa Maria, todo o valor do ingresso é investido no hotel, decorações e brindes sem sobrar dinheiro para doar por uma causa.',
                                      'O Capibára pode ter essa fuça de gaúcho rabugento, mas tem um coração grande que nem o Rio Grande do Sul. Assim como qualquer capivara ele faz amizade com qualquer um! Pode ser um gato ou um jacaré, qualquer furry é bem vindo para ser seu amigo.',
                                      'Um bom gaúcho sempre anda bem pilchado, então Capibára não dispensa sua boina, seu lenço e sua faixa pampa da cintura! Para completar ele não larga seu mate de jeito nenhum!',
                                      'A primeira convenção furry no sul do Brasil está voltando com mais uma edição! O vale dos dinossauros aguarda você para uma aventura jurássica!! 🦖🦕'])
        pic = bloblist_fursmeet[random.randint(0, len(bloblist_fursmeet)-1)].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b>Faltam {number_to_emojis(daysremaining)} dias para o FurSMeet {year}!</b>\n\n<i>{calltoaction}</i>\n🦕🦖🦫🦕🦖🦫🦕🦖🦫🦕🦖🦫🦕🦖🦫\n\n📆 {day} a {day+2}/{month}, Santa Maria, Rio Grande do Sul\n🎫Link para comprar ingresso: fursmeet.carrd.co\n💻 Informações no site: fursmeet.wixsite.com/fursmeet\n📲 Grupo do evento: @fursmeetchat"
    elif msg['text'].lower().startswith('/trex'):
        day, month, year = 21, 9, 2024
        calltoaction = random.choice(['Já pensou em se divertir com sua própria fursuit ou cosplay dentro de um Shopping? Então venha conhecer o T-Rex Furplayer!',
                                      'Um evento muito acolhedor e divertido, com intuito de reunir furries e cosplayers para criar novas amizades e memórias inesquecíveis enquanto se divertem nas incríveis atrações do T-Rex Park!',
                                      'O T-Rex Park é um parque de diversões votado a um tema Jurássico, aonde reúne vários brinquedos divertidos com vários dinossauros espalhados pelo parque, e o melhor, é que de noite ele se torna um parque mágico com muitas luzes em neon!',
                                      'No T-Rex Pool, conhecida por ter mais de 1 MILHÃO de bolinhas, os participantes mergulham em uma experiência única e colorida, onde a diversão é garantida em meio a um mar de bolinhas, proporcionando momentos inesquecíveis de brincadeira e descontração no evento.',
                                      'No T-Rex Jump, a diversão é elevada a novas alturas, proporcionando aos participantes uma experiência saltitante e cheia de energia em meio à atmosfera jurássica do evento.',
                                      'O que vocês estão esperando? Não perca esse momento incrível! Venha criar memórias inesquecíveis com os seus amigos!',
                                      'No T-Rex Furplayer, a criatividade se funde com a diversão em um encontro único! Reunindo as comunidades Cosplayers e Furries, em um ambiente cheio de energia e pura diversão!',
                                      'A Staff dedicada do T-Rex Furplayer, garante que cada detalhe seja uma experiência incrível e perfeita para todos, proporcionando aos participantes uma experiência impecável e acolhedora, repleta de diversão e memórias inesquecíveis!'])
        pic = bloblist_trex[random.randint(0, len(bloblist_trex)-1)].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b>Faltam {number_to_emojis(daysremaining)} dias para o T-Rex Furplayer!</b>\n\n<i>{calltoaction}</i>\n🦖🐺🦖🦸‍♂🦖🐺🦖🦸‍♂🦖🐺🦖🦸‍♂🦖🐺🦖🦸‍♂🦖\n\n📆 {day}/{month} - Shopping D, Canindé São Paulo - SP\n💻 Ingressos em: trexfurplayer.wordpress.com\n📲 Grupo do evento: @trexfurplayergroup"
    else:
        send_message(cookiebot, chat_id, "Evento não encontrado", msg, language)
        return
    send_photo(cookiebot, chat_id, pic, caption=caption, msg_to_reply=msg, language=language, is_alternate_bot=is_alternate_bot)

def unearth(cookiebot, msg, chat_id, thread_id=None):
    send_chat_action(cookiebot, chat_id, 'typing')
    for _ in range(100):
        try:
            chosenid = random.randint(1, msg['message_id'])
            forward_message(cookiebot, chat_id, chat_id, chosenid, thread_id=thread_id)
            return chosenid
        except Exception:
            return None

def death(cookiebot, msg, chat_id, language):
    react_to_message(msg, '👻')
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    fileblob = bloblist_death[random.randint(0, len(bloblist_death)-1)]
    filename = fileblob.name
    fileurl = fileblob.generate_signed_url(datetime.timedelta(minutes=15), method='GET')
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
    caption += '\nMotivo: <b>' + line + '</b> 🔥\nF no chat. 🫡'
    if filename.endswith('.gif'):
        send_animation(cookiebot, chat_id, fileurl, caption=caption, msg_to_reply=msg, language=language)
    else:
        send_photo(cookiebot, chat_id, fileurl, caption=caption, msg_to_reply=msg, language=language)

def fortune_cookie(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    anim_id = send_animation(cookiebot, chat_id, 'https://s12.gifyu.com/images/S5e9b.gif', msg_to_reply=msg, language=language)
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
    time.sleep(3)
    delete_message(cookiebot, (str(chat_id), str(anim_id)))
    send_chat_action(cookiebot, chat_id, 'typing')
    send_message(cookiebot, chat_id, answer, msg_to_reply=msg, language=language, parse_mode='HTML')

def destroy(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    if language == 'pt':
        instru = "Responda a um vídeo, foto, audio, gif ou sticker com o comando para distorcer (ou use /zoar pfp)"
    else:
        instru = "Reply to a video, photo, audio, gif or sticker with the command to distort (or use /destroy pfp)"
    if msg['text'].endswith('pfp'):
        send_chat_action(cookiebot, chat_id, 'upload_photo')
        token = get_bot_token(is_alternate_bot)
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
        send_message(cookiebot, chat_id, instru, msg, language)
    elif 'video' in msg['reply_to_message']:
        thismighttakeawhile = cookiebot.sendMessage(chat_id, "(hold on, this might take a while...)", reply_to_message_id=msg['message_id'])
        send_chat_action(cookiebot, chat_id, 'upload_video')
        video_file = get_media_content(cookiebot, msg['reply_to_message'], 'video', is_alternate_bot=is_alternate_bot, downloadfile=True)
        Distortioner.distortioner(video_file)
        with open('distorted.mp4', 'rb') as video:
            cookiebot.sendVideo(chat_id, video, reply_to_message_id=msg['message_id'])
        cookiebot.deleteMessage((chat_id, thismighttakeawhile['message_id']))
        os.remove('distorted.mp4')
        os.remove(video_file)
    elif 'photo' in msg['reply_to_message']:
        send_chat_action(cookiebot, chat_id, 'upload_photo')
        photo_file = get_media_content(cookiebot, msg['reply_to_message'], 'photo', is_alternate_bot=is_alternate_bot, downloadfile=True)
        Distortioner.distortioner(photo_file)
        with open('distorted.jpg', 'rb') as photo:
            cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])
        os.remove('distorted.jpg')
        os.remove(photo_file)
    elif 'audio' in msg['reply_to_message'] or 'voice' in msg['reply_to_message']:
        send_chat_action(cookiebot, chat_id, 'upload_voice')
        if 'audio' in msg['reply_to_message']:
            audio_file = get_media_content(cookiebot, msg['reply_to_message'], 'audio', is_alternate_bot=is_alternate_bot, downloadfile=True)
        else:
            audio_file = get_media_content(cookiebot, msg['reply_to_message'], 'voice', is_alternate_bot=is_alternate_bot, downloadfile=True)
        Distortioner.distort_audiofile(audio_file, 10, 1, 'distorted.mp3')
        with open('distorted.mp3', 'rb') as audio:
            cookiebot.sendAudio(chat_id, audio, reply_to_message_id=msg['message_id'])
        os.remove('distorted.mp3')
        os.remove(audio_file)
    elif 'sticker' in msg['reply_to_message']:
        send_chat_action(cookiebot, chat_id, 'upload_photo')
        sticker_file = get_media_content(cookiebot, msg['reply_to_message'], 'sticker', is_alternate_bot=is_alternate_bot, downloadfile=True)
        Distortioner.process_image(sticker_file, 'distorted.png', 25)
        with open('distorted.png', 'rb') as sticker:
            cookiebot.sendSticker(chat_id, sticker, reply_to_message_id=msg['message_id'])
        os.remove('distorted.png')
        os.remove(sticker_file)
    elif 'animation' in msg['reply_to_message']:
        send_chat_action(cookiebot, chat_id, 'upload_video')
        animation_file = get_media_content(cookiebot, msg['reply_to_message'], 'animation', is_alternate_bot=is_alternate_bot, downloadfile=True)
        Distortioner.distortioner(animation_file, is_gif=True)
        with open('distorted.mp4', 'rb') as animation:
            cookiebot.sendAnimation(chat_id, animation, reply_to_message_id=msg['message_id'])
        os.remove('distorted.mp4')
        os.remove(animation_file)
    else:
        send_message(cookiebot, chat_id, instru, msg, language)
