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
from Server import NUMBER_CHATS
import Distortioner
bloblist_ideiadesenho = list(storage_bucket.list_blobs(prefix="IdeiaDesenho"))
bloblist_death = list(storage_bucket.list_blobs(prefix="Death"))
bloblist_bff = list(storage_bucket.list_blobs(prefix="Countdown/BFF"))
bloblist_patas = list(storage_bucket.list_blobs(prefix="Countdown/Patas"))
bloblist_fursmeet = list(storage_bucket.list_blobs(prefix="Countdown/FurSMeet"))
bloblist_furcamp = list(storage_bucket.list_blobs(prefix="Countdown/Furcamp"))
bloblist_pawstral = list(storage_bucket.list_blobs(prefix="Countdown/Pawstral"))
custom_commands = list(dict.fromkeys([folder.name.split('/')[1] for folder in storage_bucket.list_blobs(prefix="Custom/")]))
NEW_CHAT_LINK = "https://t.me/CookieMWbot?startgroup=new"
WEBSITE_LINK = "https://cookiebotfur.net"
TEST_CHAT_LINK = "https://t.me/+mX6W3tGXPew2OTIx"
UPDATES_CHANNEL_LINK = "https://t.me/cookiebotupdates"

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
            'description_en': f"I'm currently present in {number_to_emojis(NUMBER_CHATS)} active chats! Feel free to add me to yours :)",
            'additional_info': "\n\nSou um bot com IA de Conversação, Defesa de Grupo, Pesquisa, Conteúdo Personalizado e Publicação Automática.",
            'additional_info_en': "\n\nI'm an AI Conversation, Group Defense, Search, Custom Content and Automated Publication bot.",
            'commands': "/configurar para alterar minhas configurações (incluindo idioma)\nUse /comandos para ver todas as minhas funcionalidades\n\n",
            'commands_en': "/configurar to change my settings (including language)\nUse /comandos to see all my features\n\n"
        }
    }
    bot = bot_identities.get(is_alternate_bot, bot_identities['default'])
    name = bot['name']
    description = bot['description_pt'] if is_portuguese else bot['description_en']
    additional_info = bot.get('additional_info', '')
    additional_info_en = bot.get('additional_info_en', '')
    commands = bot.get('commands', '')
    commands_en = bot.get('commands_en', '')
    message = (f"*Olá {msg['from']['first_name']}, eu sou o {name}!*\n\n{description}{additional_info}\n"
                f"{commands}Se tiver alguma dúvida ou quiser algo adicionado, mande uma mensagem para @MekhyW") \
        if is_portuguese else \
        (f"*Hello {msg['from']['first_name']}, I'm {name}!* \n\n{description}{additional_info_en}\n"
            f"{commands_en}If you have any questions or want something added, send a message to @MekhyW")
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Adicionar a um Grupo 👋" if is_portuguese else "Add me to a Group 👋", url=NEW_CHAT_LINK)],
        [InlineKeyboardButton(text="Website / Painel de Controle 🌐" if is_portuguese else "Website / Control Panel 🌐", url=WEBSITE_LINK)],
        [InlineKeyboardButton(text="Mural de Divulgações 📬" if is_portuguese else "Shared Posts 📬", url=POSTMAIL_CHAT_LINK)],
        [InlineKeyboardButton(text="Canal de Atualizações 📢" if is_portuguese else "Updates Channel 📢", url=UPDATES_CHANNEL_LINK)],
        [InlineKeyboardButton(text="Grupo de teste/assistência 🧪" if is_portuguese else "Test/assistance Group 🧪", url=TEST_CHAT_LINK)]
    ])
    send_message(cookiebot, chat_id, message, reply_markup=reply_markup)

def privacy_statement(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    text = "Os termos de privacidade do Cookiebot (e seus clones) estão disponíveis em https://cookiebotfur.net/privacy" if language == 'pt' else "Las condiciones de privacidad de Cookiebot (y sus clones) están disponibles en https://cookiebotfur.net/privacy" if language == 'es' else "Cookiebot's privacy terms (and its clones) are available at https://cookiebotfur.net/privacy"
    send_message(cookiebot, chat_id, text, msg_to_reply=msg, parse_mode='HTML')

def is_alive(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    react_to_message(msg, '👍', is_alternate_bot=is_alternate_bot)
    send_chat_action(cookiebot, chat_id, 'typing')
    text = "<b> Estou vivo </b>\n\nPing enviado em:\n" if language == 'pt' else "<b>Estoy vivo</b>\n\nPing enviado a:\n" if language == 'es' else "<b> I'm alive </b>\n\nPing sent at:\n"
    send_message(cookiebot, chat_id, text + str(datetime.datetime.now()), msg)

def analyze(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if not 'reply_to_message' in msg:
        text = "Responda uma mensagem com o comando para analisar" if language == 'pt' else "Responde a un mensaje con el comando para analizar" if language == 'es' else "Reply to a message with the command to analyze"
        send_message(cookiebot, chat_id, text, msg)
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
            time.sleep(0.4)
            if 'title' in chat and chat['type'] in ['group', 'supergroup']:
                chat_info = f"{group['id']} - {chat['title']}"
                if not any(chat.startswith(chat_info.split()[0]) for chat in existing_chats):
                    new_chats.append(chat_info)
                cookiebot.sendMessage(chat_id, chat_info)
                time.sleep(0.1)
        except Exception:
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
    text = "<i> Funções de diversão estão desativadas nesse chat </i>" if language == 'pt' else "<i> Funções de diversión están desactivadas en este chat </i>" if language == 'es' else "<i> Fun functions are disabled in this chat </i>"
    send_message(cookiebot, chat_id, text, msg)

def notify_utility_off(cookiebot, msg, chat_id, language):
    text = "<i> Funções de utilidade estão desativadas nesse chat </i>" if language == 'pt' else "<i> Las funciones de utilidad están deshabilitadas en este chat. </i>" if language == 'es' else "<i> Utility functions are disabled in this chat </i>"
    send_message(cookiebot, chat_id, text, msg)

def drawing_idea(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    idea_id = random.randint(0, len(bloblist_ideiadesenho)-1)
    blob = bloblist_ideiadesenho[idea_id]
    photo = blob.generate_signed_url(datetime.timedelta(minutes=15), method='GET')
    caption = f"Referência com ID {idea_id}\n\nNão trace sem dar créditos! (use a busca reversa do google images)" if language == 'pt' else f"Referencia con ID {idea_id}\n\n¡No rastrear sin dar créditos! (utilice la búsqueda inversa de imágenes de Google)" if language == 'es' else f"Reference ID {idea_id}\n\nDo not trace without credits! (use the reverse google images search)"
    send_photo(cookiebot, chat_id, photo, caption=caption, msg_to_reply=msg)

def custom_command(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    bloblist = list(storage_bucket.list_blobs(prefix="Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '').replace("@pawstralbot", '').split()[0]))
    if len(msg['text'].split()) > 1 and msg['text'].split()[1].isdigit():
        image_id = int(msg['text'].split()[1])
    else:
        image_id = random.randint(0, len(bloblist)-1)
    photo = bloblist[image_id].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
    name = msg['text'].replace('/', '').replace('@CookieMWbot', '').split()[0].capitalize()
    caption = f"Foto custom de {name} com ID {image_id}" if language == 'pt' else f"Foto custom de {name} con ID {image_id}" if language == 'es' else f"Custom photo of {name} with ID {image_id}"
    send_photo(cookiebot, chat_id, photo, msg_to_reply=msg, caption=caption)

def roll_dice(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    if msg['text'].startswith("/dado"):
        send_message(cookiebot, chat_id, "Rodo um dado de 1 até x, n vezes\n<blockquote> EXEMPLO: /d20 5\nRoda um d20 5 vezes </blockquote>")
    elif msg['text'].startswith("/dice"):
        send_message(cookiebot, chat_id, "Roll a dice from 1 to x, n times\n<blockquote> EXAMPLE: /d20 5\nRolls a d20 5 times </blockquote>")
    else:
        if len(msg['text'].split()) == 1:
            vezes = 1
        else:
            vezes = int(msg['text'].replace("@CookieMWbot", '').replace("@pawstralbot", '').split()[1])
            vezes = max(min(20, vezes), 1)
        limite = int(msg['text'].replace("@CookieMWbot", '').replace("@pawstralbot", '').split()[0][2:])
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
        send_message(cookiebot, chat_id, "Digite um nome, vou dizer a sua idade!\n<blockquote> Exemplo: '/idade Mekhy'\n(obs: só o primeiro nome conta) </blockquote>", msg, language)
    else:
        nome = msg['text'].replace("/idade ", '').replace("/edad ", '').replace("/age ", '').replace("/idade@CookieMWbot", '').replace("/age@CookieMWbot", '').replace("/edad@CookieMWbot", '').split()[0]
        response = json.loads(requests.get(f"https://api.agify.io?name={nome}", timeout=10).text)
        idade = response['age']
        registered_times = response['count']
        if registered_times == 0:
            text = "Não conheço esse nome!" if language == 'pt' else "No conozco ese nombre!" if language == 'es' else "I don't know that name!"
            send_message(cookiebot, chat_id, text, msg)
        else:
            text = f'Sua idade é <span class="tg-spoiler">{idade} anos! 👴</span>\nRegistrado <b> {registered_times} </b> vezes' if language == 'pt' else f'¡Tu edad es <span class="tg-spoiler">{age} años! 👴</span>\nRegistrado <b>{registered_times}</b> veces' if language == 'es' else f'Your age is <span class="tg-spoiler">{age} years! 👴</span>\nRegistered <b>{registered_times}</b> times'
            send_message(cookiebot, chat_id, text, msg)

def gender(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    if not " " in msg['text']:
        text = "Digite um nome, vou dizer o seu gênero!\n<blockquote> Exemplo: '/genero Mekhy' </blockquote>" if language == 'pt' else "Introduce un nombre y te diré tu género.\n<blockquote> Ejemplo: '/gender Mekhy'</blockquote>" if language == 'es' else "Enter a name, I'll tell you your gender!\n<blockquote> Example: '/gender Mekhy'</blockquote>"
        send_message(cookiebot, chat_id, text, msg)
    else:
        nome = msg['text'].replace("/genero ", '').replace("/gênero ", '').replace("/gender ", '').replace("/genero@CookieMWbot", '').replace("/gênero@CookieMWbot", '').replace("/gender@CookieMWbot", '').split()[0]
        response = json.loads(requests.get(f"https://api.genderize.io?name={nome}", timeout=10).text)
        genero = response['gender']
        probability = response['probability']
        registered_times = response['count']
        if registered_times == 0:
            text = "Não conheço esse nome!" if language == 'pt' else "No conozco ese nombre!" if language == 'es' else "I don't know that name!"
            send_message(cookiebot, chat_id, text, msg)
        elif genero == 'male':
            text = f'É <span class="tg-spoiler">um menino! 👨</span> \n\nProbabilidade --> {probability*100}%\nRegistrado {registered_times} vezes' if language == 'pt' else f'¡Es un niño! 👨</span> \n\nProbabilidad --> {probability*100}%\nRegistrado {registered_times} veces' if language == 'es' else f'Its <span class="tg-spoiler">a boy! 👨</span> \n\nProbability --> {probability*100}%\nRegistered {registered_times} times'
            send_message(cookiebot, chat_id, text, msg)
        elif genero == 'female':
            text = f'É <span class="tg-spoiler">uma menina! 👩</span> \n\nProbabilidade --> {probability*100}%\nRegistrado {registered_times} vezes' if language == 'pt' else f'¡Es una niña! 👩</span> \n\nProbabilidad --> {probability*100}%\nRegistrado {registered_times} veces' if language == 'es' else f'Its <span class="tg-spoiler">a girl! 👩</span> \n\nProbability --> {probability*100}%\nRegistered {registered_times} times'
            send_message(cookiebot, chat_id, text, msg)

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
    send_message(cookiebot, chat_id, "<b> 💥POOOOOOOWW💥 </b>", thread_id=thread_id, is_alternate_bot=is_alternate_bot)

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
    with open(f'Static/reclamacao/answers_{language}.txt', 'r', encoding='utf8') as answers:
        answer = random.choice(answers.readlines()).replace('\n', '')
    send_message(cookiebot, chat_id, answer, msg_to_reply=msg)

def event_countdown(cookiebot, msg, chat_id, language, is_alternate_bot):
    react_to_message(msg, '🔥', is_alternate_bot=is_alternate_bot)
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    if msg['text'].lower().startswith('/patas'):
        day, month, year = 11, 12, 2026
        calltoaction = random.choice(['Já comprou o seu ingresso? Não perca a oportunidade de participar do maior evento furry de Sorocaba-SP!',
                                  'Este é um evento beneficiente em formato de convenção, para promover e celebrar a cultura de apreciação animais antropomóficos na região de Sorocaba. Foi criado para ajudar as entidades que prestam apoio aos idosos da região.',
                                  'O evento vai acontecer no SOROCABA PARK HOTEL, um local que oferece comodidade e conforto para todos os participantes do evento!',
                                  'As atrações incluem:\n\n-Show com Banda\n-Balada Furry com DJ\n-Pool Party com brinquedos de piscina e DJ\n-Mercadinho Furry\n-E muito mais!'])
        pic = bloblist_patas[random.randint(0, len(bloblist_patas)-1)].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days + 1
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b> Faltam {number_to_emojis(daysremaining)} dias para o Patas! </b>\n\n<i> {calltoaction} </i>\n🐾🍌🐾🐒🐾🍌🐾🐒🐾🍌🐾🐒🐾🍌\n\n📆 {day} a {day+3}/{month}, Sorocaba Park Hotel\n💻 Ingressos em: patas.site\n📲 Grupo do evento: @EventoPatas"
    elif msg['text'].lower().startswith('/bff'):
        day, month, year = 17, 7, 2026
        calltoaction = random.choice(['A Brasil FurFest tem, entre outros objetivos, levantar fundos para caridade em prol do Projeto Social SOS Vida Pet Litoral, que ajuda protetores a manter abrigos para animais de rua na Baixada Santista',
                                  'Quem são os furries? O que é a Brasil FurFest? Descubra em youtube.com/watch?v=vuFGHSL8X34&ab_channel=BrasilFurFest',
                                  'Esperamos para ver todos os furries nos parques da maravilhosa cidade de São Paulo para essa festa que será inesquecível!',
                                  'Entre as atividades planejadas, temos atividades de social mixer (dinâmicas de grupo) no início do evento para que você engrene os primeiros contatos com os demais participantes no evento.',
                                  'Bombom nasceu na Fantástica Fábrica de Doces com intuito de reunir os furries na Brasil FurFest para muita festa e diversão. Aliás, se a festa tiver caipirinhas melhor ainda!',
                                  'Em 2026, o tempo vai dar tilt! Preparem-se para uma viagem maluca por uma linha do tempo quebrada - passado, presente e futuro colidindo em um só lugar!',
                                  'Mais de mil participantes! Isso mesmo: MIL! Desde 2024, batemos um recorde histórico para o furry fandom brasileiro, e tudo graças a vocês que vieram com toda a energia e alegria que só a nossa comunidade furry sabe trazer!',
                                  'O evento utiliza o ConCat, um sistema de gerenciamento de eventos usado em algumas das maiores convenções furry do mundo!',
                                  'Nosso novo lar será em Campinas, no Hotel Premium, que conta com um espaço de lazer incrível e muito mais conforto no centro de convenções para todo mundo curtir ao máximo.',
                                  'O Premium Hotel é a opção perfeita para quem procura a melhor hospedagem na região de Campinas, seja para desfrutar de momentos agradáveis e relaxantes com a família ou então participar de eventos como a BFF!',
                                  'O Premium Hotel dispõe de wi-fi cortesia para hóspedes, restaurante, american bar, business center e ampla área de lazer com academia, sauna, duas piscinas externas, uma piscina climatizada, quadras esportivas, espaço kids e playground.',
                                  'O Premium Hotel Campinas está localizado na R. Novotel, 931 - Jardim Nova Aparecida, oferecendo fácil acesso às principais atrações e rodovias da cidade.'])
        pic = bloblist_bff[random.randint(0, len(bloblist_bff)-1)].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days + 1
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b> Faltam {number_to_emojis(daysremaining)} dias para a Brasil FurFest 2026 - Sem Tempo Irmão! </b>\n\n<i> {calltoaction} </i>\n🐾🟩🐾🟨🐾🟩🐾🟨🐾🟩🐾🟨🐾🟩\n\n📆 {day} a {day+2}/{month}\n📍 Hotel Premium - Campinas\n💻 Site: brasilfurfest.com.br, upgrades até 1 mês antes do evento através do email reg@brasilfurfest.com.br\n📲 Grupo do evento: @brasilfurfest"
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
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days + 1
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b> Faltam {number_to_emojis(daysremaining)} dias para o FurSMeet {year}! </b>\n\n<i> {calltoaction} </i>\n🦕🦖🦫🦕🦖🦫🦕🦖🦫🦕🦖🦫🦕🦖🦫\n\n📆 {day} a {day+2}/{month}, Santa Maria, Rio Grande do Sul\n🎫Link para comprar ingresso: fursmeet.carrd.co\n💻 Informações no site: fursmeet.wixsite.com/fursmeet\n📲 Grupo do evento: @fursmeetchat"
    elif msg['text'].lower().startswith('/furcamp'):
        day, month, year = 13, 2, 2026
        calltoaction = random.choice(['O FURCAMP é um evento furry criado no Brasil e acontece todos os anos em meados de fevereiro (durante o Carnaval). Com sua primeira edição piloto em março de 2019 sendo um sucesso, o evento cativou seus participantes e a equipe que o criou.',
                                      'Com sua bela paisagem, o Acampamento Terra do Saber possui pomar, trilhas e lagos para a pesca esportiva. É destinado a grupos grandes e especialmente aos visitantes que estejam em busca de uma acomodação diferenciada, podendo contar com todo o conforto da hospedagem em suítes e também em alojamentos.',
                                      'O Acampamento Terra do Saber conta com alojamentos com beliches, refeitórios, salões para reunião, janelas com tela de proteção contra insetos, banheiros com aquecimento central a gás, reservatórios de água, poços artesianos e muito mais.',
                                      'O FURCAMP oferece várias atividades emocionantes para os participantes durante todo o evento, como Batalha no Campo e Gincana, Show de Talentos e Balada Furry, com cada atividade tendo uma pontuação para o participante ou equipe do participante!',
                                      'Se você sabe atuar, dançar, cantar, tocar um instrumento, fazer truques de mágica ou tem qualquer habilidade maluca, este é o lugar para mostrá-las. Que tal contar uma piada ruim, fazer o público chorar ou rir com um stand-up? No Show de Talentos, vale tudo!',
                                      'Prepare-se para dançar, agitar, pular e se divertir na boate do FURCAMP com música eletrizante e um show de luzes, junto com um set incrível dos DJs Furries!',
                                      'Você perdeu a nossa livestream especial no dia 19? Quer saber tudo que rolou sobre as atualizações do evento e informações cruciais que não pode deixar passar? Não se preocupe! Assista ao VOD da live no nosso canal do YouTube e fique por dentro de tudo! 🎥✨'])
        pic = bloblist_furcamp[random.randint(0, len(bloblist_furcamp)-1)].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days + 1
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b> Faltam {number_to_emojis(daysremaining)} dias para o FurCamp! </b>\n\n<i> {calltoaction} </i>\n🐾🌲🐾🌳🐾🌲🐾🌳🐾🌲🐾🌳\n\n📆 {day} a {day+4}/{month}, Acampamento Terra do Saber - Cajamar - SP\n💻 Ingressos em: furcamp.com\n📲 Grupo do evento: @FurcampOficial"
    elif msg['text'].lower().startswith('/pawstral'):
        day, month, year = 29, 8, 2025
        calltoaction = random.choice(['The furry convention that will fill the city of Santiago with color and energy!',
                                      'Pawstral is more than just a convention; it is a space for furries, artists, and fans of furry culture to come together, celebrate, and share their passion.',
                                      'There will be activities for everyone, from workshops and presentations to an amazing fursuiting space, art, and much more.',
                                      'Santiago awaits you with its urban charm, surrounded by mountains and beautiful landscapes, perfect for enjoying the last days of winter.',
                                      'With modern design and a privileged location in the district of Las Condes, you will find it at Alonso de Córdova #6050, Santiago de Chile. Just steps away from the Manquehue Metro Station.',
                                      'Gastronomic proposals at ICON Hotel are designed to complete a unique and total experience during your stay, as well as to delight everyone who visits as a client or guest at an event.'])
        pic = bloblist_pawstral[random.randint(0, len(bloblist_pawstral)-1)].generate_signed_url(datetime.timedelta(minutes=15), method='GET')
        daysremaining = (datetime.datetime(year, month, day) - datetime.datetime.now()).days + 1
        if -5 <= daysremaining <= 0:
            caption = "https://www.youtube.com/watch?v=JsOVJ1PAC6s&ab_channel=TheVibeGuide"
        else:
            while daysremaining < -5:
                daysremaining += 365
            caption = f"<b> {number_to_emojis(daysremaining)} days left until Pawstral! </b>\n\n<i> {calltoaction} </i>\n🇨🇱⭐🐈🇨🇱⭐🐈🇨🇱⭐🐈🇨🇱⭐🐈🇨🇱⭐🐈\n\n📆 {day} a {day+2}/{month}, Santiago de Chile\n💻 Tickets at: https://pawstral.cl/\n📲 Event chat: @PawstralFurcon"
    else:
        text = "Evento não encontrado!" if language == 'pt' else "¡Evento no encontrado!" if language == 'es' else "Event not found!"
        send_message(cookiebot, chat_id, text, msg)
        return
    send_photo(cookiebot, chat_id, pic, caption=caption, msg_to_reply=msg, is_alternate_bot=is_alternate_bot)

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
        caption += random.choice([' IS DEAD', ' IS GONE', ' DECEASED']) + '! 💀💀💀'
    with open(f'Static/death/death_{language}.txt', 'r', encoding='utf-8') as f:
        line = random.choice(f.readlines())
        line = line.replace('\n', '')
    additional = '\nMotivo: <b> ' + line + ' </b> 🔥\nF no chat. 🫡' if language == 'pt' else '\nReason: <b> ' + line + ' </b> 🔥\nF in chat. 🫡'
    caption += additional
    if filename.endswith('.gif'):
        send_animation(cookiebot, chat_id, fileurl, caption=caption, msg_to_reply=msg)
    else:
        send_photo(cookiebot, chat_id, fileurl, caption=caption, msg_to_reply=msg)

def fortune_cookie(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    anim_id = send_animation(cookiebot, chat_id, 'https://s12.gifyu.com/images/S5e9b.gif', msg_to_reply=msg)
    with open(f'Static/Sorte/sorte_{language}.txt', 'r', encoding='utf-8') as f:
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
    answer = f'Sua sorte:\n 🥠 <span class="tg-spoiler">" {line} "</span> 🥠\nSeus números da sorte: <span class="tg-spoiler">{numbers_str}</span>' if language == 'pt' else f'Tu suerte:\n 🥠 <span class="tg-spoiler">" {line} "</span> 🥠\nTus números de la suerte: <span class="tg-spoiler">{numbers_str}</span>' if language == 'es' else f'Your luck:\n 🥠 <span class="tg-spoiler">" {line} "</span> 🥠\nYour lucky numbers: <span class="tg-spoiler">{numbers_str}</span>'
    time.sleep(3)
    delete_message(cookiebot, (str(chat_id), str(anim_id)))
    send_chat_action(cookiebot, chat_id, 'typing')
    send_message(cookiebot, chat_id, answer, msg_to_reply=msg, parse_mode='HTML')

def destroy(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    instru = "Responda a uma foto, audio ou sticker com o comando para distorcer (ou use /zoar pfp)" if language == 'pt' else "Responde a una foto, audio o sticker con el comando para distorsionar (o usa /zoar pfp)" if language == 'es' else "Reply to a photo, audio or sticker with the command to distort (or use /destroy pfp)"
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
        send_message(cookiebot, chat_id, instru, msg)
    elif 'video' in msg['reply_to_message']:
        text = "A distorção de vídeo está desativada no momento." if language == 'pt' else "La distorsión de video está desactivada en este momento." if language == 'es' else "Video distortioning is currently disabled."
        send_message(cookiebot, chat_id, text, msg)
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
        if msg['reply_to_message']['sticker']['is_animated'] or msg['reply_to_message']['sticker']['is_video']:
            text = "A distorção de GIF está desativada no momento." if language == 'pt' else "La distorsión de GIF está desactivada en este momento." if language == 'es' else "GIF distortioning is currently disabled."
            send_message(cookiebot, chat_id, text, msg)
            return
        send_chat_action(cookiebot, chat_id, 'upload_photo')
        sticker_file = get_media_content(cookiebot, msg['reply_to_message'], 'sticker', is_alternate_bot=is_alternate_bot, downloadfile=True)
        Distortioner.process_image(sticker_file, 'distorted.png', 25)
        with open('distorted.png', 'rb') as sticker:
            cookiebot.sendSticker(chat_id, sticker, reply_to_message_id=msg['message_id'])
        os.remove('distorted.png')
        os.remove(sticker_file)
    elif 'animation' in msg['reply_to_message']:
        text = "A distorção de GIF está desativada no momento." if language == 'pt' else "La distorsión de GIF está desactivada en este momento." if language == 'es' else "GIF distortioning is currently disabled."
        send_message(cookiebot, chat_id, text, msg)
    else:
        send_message(cookiebot, chat_id, instru, msg)
