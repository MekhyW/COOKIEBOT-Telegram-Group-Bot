# coding=utf8
import threading
import json
import time
import re
import random
import datetime
import urllib.request
import requests
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from universal_funcs import spamwatch_token, get_bot_token, send_photo, delete_message, ban_and_blacklist, wait_open, logger
from UserRegisters import get_request_backend, send_message, send_chat_action
from captcha.image import ImageCaptcha
import spamwatch
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

captcha = ImageCaptcha()
recently_kicked_checkhuman = {}
KICK_CACHE_DURATION = 300
try:
    spamwatch_client = spamwatch.Client(spamwatch_token)
except Exception as e:
    logger.log_text(f"Error initializing Spamwatch client: {e}", severity="WARNING")
    spamwatch_client = None

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

def open_telegram_image(cookiebot, token, photo_id):
    photo_info = cookiebot.getFile(photo_id)
    photo_url = f"https://api.telegram.org/file/bot{token}/{photo_info['file_path']}"
    resp = urllib.request.urlopen(photo_url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def substitute_user_tags(text, msg):
    user = msg['new_chat_member'] if 'new_chat_member' in msg else msg['from']
    usertags = ['{user}', '{username}', '{mention}', '$user', '$username', '$(user)', '$(username)', '<user>', '<username>', '<name>']
    for usertag in usertags:
        if usertag in text:
            if 'username' in user:
                text = text.replace(usertag, f"@{user['username']}")
            else:
                text = text.replace(usertag, f"{user['first_name']}")
    return text

def rules_message(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    rules = get_request_backend(f"rules/{chat_id}")
    if 'error' in rules and rules['error'] == "Not Found":
        send_message(cookiebot, chat_id, "Ainda não há regras colocadas para esse grupo\n<blockquote> Se você é um admin e quer colocar regras, use /novasregras </blockquote>", msg, language)
    else:
        regras = rules['rules'].replace('\\n', '\n')
        regras = substitute_user_tags(regras, msg)
        if not len(regras):
            return
        if not regras.endswith("@MekhyW"):
            if language == 'pt':
                regras += "\n\nDúvidas em relação ao bot? Mande para @MekhyW"
            elif language == 'es':
                regras += "\n\n¿Preguntas sobre el bot? Envíalo a @MekhyW"
            else:
                regras += "\n\nQuestions about the bot? Send to @MekhyW"
        cookiebot.sendMessage(chat_id, regras, reply_to_message_id=msg['message_id'])
    logger.log_text(f"Rules message sent to chat with ID {chat_id}", severity="INFO")

def welcome_card(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    user = msg['new_chat_member'] if 'new_chat_member' in msg else msg['from']
    # Get base images
    token = get_bot_token(is_alternate_bot)
    try:
        photo_id = cookiebot.getUserProfilePhotos(user['id'])['photos'][0][-1]['file_id']
        user_img = open_telegram_image(cookiebot, token, photo_id)
    except (KeyError, IndexError):
        user_img = cv2.imread('Static/No_Image_Available.jpg', cv2.IMREAD_COLOR)
    try:
        url = f'https://api.telegram.org/bot{token}/getChat?chat_id={chat_id}'
        data = requests.get(url).json()
        photo_id = data['result']['photo']['big_file_id']
        chat_img = open_telegram_image(cookiebot, token, photo_id)
    except (KeyError, IndexError):
        chat_img = cv2.imread('Static/No_Image_Available.jpg', cv2.IMREAD_COLOR)
    # Insert card background
    size = (1067, 483)
    scale = size[0]/chat_img.shape[1]
    rescaled_chat_img = cv2.resize(chat_img, (int(chat_img.shape[1] * scale), int(chat_img.shape[0] * scale)))
    cx, cy, offx, offy = int(rescaled_chat_img.shape[1]/2), int(rescaled_chat_img.shape[0]/2), int(size[1]/2), int(size[0]/2)
    cropped_chat_img = rescaled_chat_img[(cx - offx):(cx + offx), (cy - offy):(cy + offy)]
    blurred_chat_img = cv2.blur(cropped_chat_img, (17, 17))
    circle_center = (cx, int(cy/3))
    circle_radius = int(size[1]*0.28)
    cv2.circle(blurred_chat_img, circle_center, int(circle_radius*1.1), (255, 255, 255), -1)
    # Insert user profile picture
    user_img = cv2.resize(user_img, (circle_radius*2, circle_radius*2))
    y, x = np.ogrid[:user_img.shape[0], :user_img.shape[1]]
    mask = ((x - circle_radius)**2 + (y - circle_radius)**2) <= circle_radius**2
    target_slice = blurred_chat_img[
        circle_center[1] - circle_radius:circle_center[1] + circle_radius,
        circle_center[0] - circle_radius:circle_center[0] + circle_radius
    ]
    target_slice[mask] = user_img[mask]
    # Insert text
    cv2.rectangle(blurred_chat_img, (0, int(size[0]*0.36)), (size[1]*10, int(size[0]*0.40)), (0, 0, 0), -1)
    welcome = {'pt': 'Bem-vinde ao', 'es': 'Bienvenido a'}.get(language, 'Welcome to')
    font = ImageFont.truetype('Static/Roadgeek2005Engschrift-lgJw.ttf', 32)
    img_pil = Image.fromarray(blurred_chat_img)
    draw = ImageDraw.Draw(img_pil)
    chat_title = emoji_pattern.sub(r'', cookiebot.getChat(chat_id)['title'].strip())
    user_firstname = emoji_pattern.sub(r'', user['first_name'].strip())
    text = f'{welcome} {chat_title}, {user_firstname}!'
    text_w, text_h = draw.textbbox((0, 0), text, font=font)[2:]
    text_x, text_y = int(((size[1]*2.2) - text_w) / 2), int(((size[0]*0.69) + text_h) / 2)
    draw.text((text_x, text_y), text, font = font, fill = (255, 255, 255, 0))
    final_img = np.array(img_pil)
    # Save image and return
    cv2.imwrite("welcome_card.png", final_img)
    final_img = open("welcome_card.png", 'rb')
    return final_img

def welcome_message(cookiebot, msg, chat_id, limbotimespan, language, is_alternate_bot=0):
    if str(chat_id) in ['-1001063487371', '-1001649779623', '-1001582063371', '-1002048063981', '-1002193913344']: # Groups where the bot should not welcome new members
        return
    send_chat_action(cookiebot, chat_id, 'typing')
    user = msg['new_chat_member'] if 'new_chat_member' in msg else msg['from']
    if limbotimespan > 0:
        try:
            cookiebot.restrictChatMember(chat_id, user['id'], permissions={'can_send_messages': True, 'can_send_media_messages': True, 'can_send_other_messages': True, 'can_add_web_page_previews': True})
            cookiebot.restrictChatMember(chat_id, user['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + limbotimespan))
            send_message(cookiebot, chat_id, f"ATENÇÃO! Suas mídias estão restritas por <b> {round(limbotimespan/60)} minutos </b>. Por favor se apresente e se enturme na conversa com os membros.\n<blockquote> Aperte o botão abaixo ou use o /regras para ver as regras do grupo </blockquote>", language=language)
        except Exception as e:
            logger.log_text(f"Could not restrict chat member media: {e}", severity="INFO")
    welcome = get_request_backend(f'welcomes/{chat_id}')
    if type(welcome) is str or (type(welcome) is not str and 'error' in welcome and welcome['error'] == "Not Found") or 'message' not in welcome:
        welcome = f"Olá! As boas-vindas ao grupo {msg['chat']['title']}!" if 'chat' in msg and 'title' in msg['chat'] else "Olá! As boas-vindas ao grupo!"
    elif len(welcome['message']) > 0:
        welcome = welcome['message'].replace('\\n', '\n')
        welcome = substitute_user_tags(welcome, msg)
    try:
        rulesbuttontext = {'pt': 'Veja as Regras!', 'es': 'Ver las Reglas!'}.get(language, 'See the Rules!')
        welcome_card_image = welcome_card(cookiebot, msg, chat_id, language, is_alternate_bot)
        send_photo(cookiebot, chat_id, welcome_card_image, caption=welcome, language=language,
                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=rulesbuttontext,callback_data=f'RULES {language}')]]))
        logger.log_text(f"Welcome card message sent to chat with ID {chat_id}", severity="INFO")
    except Exception as e:
        send_message(cookiebot, chat_id, welcome, language=language)
        logger.log_text(f"Error sending welcome card, sent text only to chat with ID {chat_id}", severity="INFO")
    for thread in threading.enumerate():
        if isinstance(thread, threading.Timer) and 'chat_id' in thread.kwargs and thread.kwargs['chat_id'] == chat_id and 'msg' in thread.kwargs and thread.kwargs['msg']['new_chat_participant']['id'] == msg['from']['id']:
            thread.cancel()

def check_human(cookiebot, msg, chat_id, language):
    user_id = msg['new_chat_participant']['id']
    current_time = time.time()
    cache_key = (chat_id, user_id)
    expired = [(c, u) for (c, u), timestamp in recently_kicked_checkhuman.items() if current_time - timestamp > KICK_CACHE_DURATION]
    for key in expired:
        del recently_kicked_checkhuman[key]
    if cache_key in recently_kicked_checkhuman:
        return False
    if 'username' not in msg['new_chat_participant']:
        userphotos = cookiebot.getUserProfilePhotos(user_id)
        if userphotos['total_count'] == 0:
            cookiebot.kickChatMember(chat_id, user_id)
            send_message(cookiebot, chat_id, "Kickei o novo usuário por <b> suspeita de ser um robô </b>\n<blockquote> Se isso foi um erro, peça para ele adicionar um username (@) ou foto de perfil e um ADM adicioná-lo de volta </blockquote>", language=language)
            cookiebot.unbanChatMember(chat_id, user_id)
            recently_kicked_checkhuman[cache_key] = current_time
            logger.log_text(f"Kicked user with ID {user_id} in chat with ID {chat_id} for suspicion of being a bot", severity="INFO")
            return True
    return False

def check_cas(cookiebot, msg, chat_id, language):
    try:
        r = requests.get(f"https://api.cas.chat/check?user_id={msg['new_chat_participant']['id']}", timeout=2)
        in_banlist = json.loads(r.text)['ok']
    except Exception as e:
        logger.log_text(f"Error checking CAS: {e}", severity="WARNING")
        return False
    if in_banlist:
        ban_and_blacklist(cookiebot, chat_id, msg['new_chat_participant']['id'])
        send_message(cookiebot, chat_id, "Bani o usuário recém-chegado por <b> ser flagrado pelo sistema anti-spam CAS (https://cas.chat/) </b>", language=language)
        logger.log_text(f"Banned user with ID {msg['new_chat_participant']['id']} in chat with ID {chat_id} by CAS", severity="INFO")
        return True
    return False

def check_spamwatch(cookiebot, msg, chat_id, language):
    try:
        isbanned = spamwatch_client.get_ban(int(msg['new_chat_participant']['id']))
    except Exception as e:
        logger.log_text(f"Error checking Spamwatch: {e}", severity="WARNING")
        return False
    if isbanned:
        ban_and_blacklist(cookiebot, chat_id, msg['new_chat_participant']['id'])
        send_message(cookiebot, chat_id, "Bani o usuário recém-chegado por <b> ser flagrado pelo sistema anti-spam Spamwatch </b>", language=language)
        logger.log_text(f"Banned user with ID {msg['new_chat_participant']['id']} in chat with ID {chat_id} by Spamwatch", severity="INFO")
        return True
    return False

def check_banlist(cookiebot, msg, chat_id, language):
    is_blacklisted = get_request_backend(f"blacklist/{msg['new_chat_participant']['id']}")
    is_blacklisted_username = get_request_backend(f"blacklist/username/{msg['new_chat_participant']['username']}") if 'username' in msg['new_chat_participant'] else {'error': 'no username'}
    fullname = f"{msg['new_chat_participant']['first_name']} {msg['new_chat_participant']['last_name']}" if 'last_name' in msg['new_chat_participant'] else msg['new_chat_participant']['first_name']
    if ('id' in is_blacklisted and is_blacklisted['id'] == str(msg['new_chat_participant']['id'])) or ('id' in is_blacklisted_username and is_blacklisted_username['id'] == msg['new_chat_participant']['username']) or '卐' in fullname:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        send_message(cookiebot, chat_id, "Bani o usuário recém-chegado por <b> ser flagrado como conta falsa/spam em outros chats </b>", language=language)
        logger.log_text(f"Banned user with ID {msg['new_chat_participant']['id']} in chat with ID {chat_id} by blacklist", severity="INFO")
        return True
    return False

def captcha_message(cookiebot, msg, chat_id, captchatimespan, limbotimespan, language, is_alternate_bot=0):
    user_id = msg['new_chat_participant']['id']
    try:
        cookiebot.restrictChatMember(chat_id, user_id, permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + captchatimespan))
    except Exception as e:
        logger.log_text(f"Could not restrict chat member for captcha: {e}", severity="INFO")
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    caracters = ['0', '2', '3', '4', '5', '6', '8', '9']
    password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
    captcha.write(password, 'CAPTCHA.png')
    with open('CAPTCHA.png', 'rb') as photo:
        caption = f"⚠️Digite o código acima OU aperte o botão abaixo⚠️\n\nVocê tem {round(captchatimespan/60)} minutos, se não resolver nesse tempo te removerei do chat ⏳\n(Se não aparecem 4 digitos, abra a foto completa)"
        captchaspawnID = send_photo(cookiebot, chat_id, photo, caption=caption, language=language, msg_to_reply=msg, reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ADMINS: Approve",callback_data=f'CAPTCHAAPPROVE {language} 0')],
            [InlineKeyboardButton(text="I'm not a Robot!",callback_data=f'CAPTCHASELF {language} {msg["new_chat_participant"]["id"]}')]
        ]))
    wait_open("Captcha.txt")
    with open("Captcha.txt", 'r', encoding='utf-8') as text:
        lines = text.readlines()
    with open("Captcha.txt", 'w+', encoding='utf-8') as text:
        for line in lines:
            if len(line.split()) >= 5:
                _, _, _, _, chat, user, password, _, _ = parse_line_captcha(line)
                if chat == chat_id and user == user_id:
                    for thread in threading.enumerate():
                        if isinstance(thread, threading.Timer) and thread.kwargs['chat_id'] == chat_id and thread.kwargs['msg']['new_chat_participant']['id'] == user_id:
                            thread.cancel()
                else:
                    text.write(line)
        text.write(f"{chat_id} {user_id} {datetime.datetime.now()} {password} {captchaspawnID} 5\n")
    timer = threading.Timer(captchatimespan+1, check_captcha, kwargs={'cookiebot': cookiebot, 'msg': msg, 'chat_id': chat_id, 'captchatimespan': captchatimespan, 'language': language})
    timer.start()
    logger.log_text(f"Captcha message sent to chat with ID {chat_id}", severity="INFO")

def parse_line_captcha(line):
    #CHATID userID yy-mm-dd hr:min:sec password captcha_id attempts
    hour = int(line.split()[3].split(":")[0])
    minute = int(line.split()[3].split(":")[1])
    second = float(line.split()[3].split(":")[2])
    captchasettime = (hour*3600) + (minute*60) + (second)
    chat = int(line.split()[0])
    user = int(line.split()[1])
    password = line.split()[4]
    captcha_id = int(line.split()[5])
    attempts = int(line.split()[6])
    return hour, minute, second, captchasettime, chat, user, password, captcha_id, attempts

def check_captcha(cookiebot, msg, chat_id, captchatimespan, language):
    wait_open("Captcha.txt")
    with open("Captcha.txt", 'r', encoding='utf-8') as text:
        lines = text.readlines()
    with open("Captcha.txt", 'w+', encoding='utf-8') as text:
        for line in lines:
            if len(line.split()) >= 5:
                _, _, _, captchasettime, chat, user, _, captcha_id, attempts = parse_line_captcha(line)
                if chat == chat_id and (captchasettime+captchatimespan <= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)) or attempts <= 0):
                    reason = "exceder o limite de tentativas para resolver o captcha" if attempts <= 0 else "não solucionar o captcha a tempo"
                    try:
                        cookiebot.kickChatMember(chat_id, user)
                        send_message(cookiebot, chat_id, f"Kickei o usuário com id <b> {user} </b> por <b> {reason} </b>.\n<blockquote> Se isso foi um erro, peça para um staff adicioná-lo de volta </blockquote>", language=language)
                        cookiebot.unbanChatMember(chat_id, user)
                        logger.log_text(f"Kicked user with ID {user} in chat with ID {chat_id} by captcha", severity="INFO")
                    except Exception as e:
                        send_message(cookiebot, chat_id, f"Erro ao kickar o usuário com id <b> {user} </b> por <b> {reason} </b>.\n<blockquote> Usuário não está mais no chat, ou não tenho permissão para kickar </blockquote>", language=language)
                        logger.log_text(f"Could not kick user with ID {user} in chat with ID {chat_id}: {e}", severity="INFO")
                    delete_message(cookiebot, (str(chat), str(captcha_id)))
                elif chat == chat_id and user == msg['from']['id']:
                    text.write(line)
                    delete_message(cookiebot, telepot.message_identifier(msg))
                else:
                    text.write(line)

def solve_captcha(cookiebot, msg, chat_id, button, limbotimespan=0, language='pt', is_alternate_bot=0):
    wait_open("Captcha.txt")
    with open("Captcha.txt", 'r', encoding='utf-8') as text:
        lines = text.readlines()
    if len(lines) == 0 and button:
        delete_message(cookiebot, telepot.message_identifier(msg['message']))
        return
    with open("Captcha.txt", 'w+', encoding='utf-8') as text:
        for line in lines:
            if len(line.split()) >= 5:
                _, _, _, _, chat, user, password, captcha_id, attempts = parse_line_captcha(line)
                if str(chat_id) == str(chat) and button:
                    send_chat_action(cookiebot, chat_id, 'typing')
                    delete_message(cookiebot, (str(chat), str(captcha_id)))
                    msg['new_chat_member'] = cookiebot.getChatMember(chat, str(user))['user']
                    welcome_message(cookiebot, msg, chat, limbotimespan, language, is_alternate_bot)
                elif str(chat_id) == str(chat) and str(msg['from']['id']) == str(user):
                    send_chat_action(cookiebot, chat_id, 'typing')
                    solveattempt = "".join(msg['text'].upper().split())
                    if solveattempt.isnumeric() and len(solveattempt) == 4:
                        delete_message(cookiebot, (str(chat), str(captcha_id)))
                        delete_message(cookiebot, telepot.message_identifier(msg))
                        welcome_message(cookiebot, msg, chat_id, limbotimespan, language, is_alternate_bot)
                        logger.log_text(f"Captcha attempt for user with ID {user} in chat with ID {chat_id} solved", severity="INFO")
                    else:
                        delete_message(cookiebot, telepot.message_identifier(msg))
                        attempts -= 1
                        if attempts > 0:
                            send_message(cookiebot, chat_id, "Senha incorreta, por favor tente novamente.", language=language)
                        line = f"{chat} {user} {datetime.datetime.now()} {password} {captcha_id} {attempts}\n"
                        text.write(line)
                        logger.log_text(f"Captcha attempt for user with ID {user} in chat with ID {chat_id} failed", severity="INFO")
                else:
                    text.write(line)
