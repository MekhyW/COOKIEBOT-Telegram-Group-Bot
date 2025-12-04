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
from universal_funcs import get_bot_token, send_photo, delete_message, ban_and_blacklist, wait_open
from UserRegisters import get_request_backend, send_message, send_chat_action
from captcha.image import ImageCaptcha
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from loc import i18n

captcha = ImageCaptcha()
recently_kicked_checkhuman = {}
join_tracker = {}
join_tracker_lock = threading.Lock()
raid_banned_users = set()
KICK_CACHE_DURATION = 300
JOIN_WINDOW = 10
JOIN_LIMIT = 5
EMOJI_PATTERN = re.compile("[" + u"\U0001F600-\U0001F64F" + u"\U0001F300-\U0001F5FF" + u"\U0001F680-\U0001F6FF" + u"\U0001F1E0-\U0001F1FF" + "]+", flags=re.UNICODE)

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
    if (type(rules) is str and not len(rules)) or ('error' in rules and rules['error'] == "Not Found"):
        text = i18n.get("no_rules", lang=language)
        send_message(cookiebot, chat_id, text, msg, language)
    else:
        regras = rules['rules'].replace('\\n', '\n')
        regras = substitute_user_tags(regras, msg)
        if not len(regras):
            return
        if not regras.endswith("@MekhyW"):
            additional = i18n.get("questions", lang=language)
            regras += additional
        cookiebot.sendMessage(chat_id, regras, reply_to_message_id=msg['message_id'])

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
    chat_title = EMOJI_PATTERN.sub(r'', cookiebot.getChat(chat_id)['title'].strip())
    user_firstname = EMOJI_PATTERN.sub(r'', user['first_name'].strip())
    text = f'{welcome} {chat_title}, {user_firstname}!'
    text_w, text_h = draw.textbbox((0, 0), text, font=font)[2:]
    text_x, text_y = int(((size[1]*2.2) - text_w) / 2), int(((size[0]*0.69) + text_h) / 2)
    draw.text((text_x, text_y), text, font = font, fill = (255, 255, 255, 0))
    final_img = np.array(img_pil)
    # Save image and return
    cv2.imwrite("welcome_card.png", final_img)
    final_img = open("welcome_card.png", 'rb')
    return final_img

def check_raid(cookiebot, msg, chat_id, language):
    current_time = time.time()
    with join_tracker_lock:
        if chat_id not in join_tracker:
            join_tracker[chat_id] = []
        join_tracker[chat_id] = [(uid, t) for uid, t in join_tracker[chat_id] if current_time - t <= JOIN_WINDOW] # Clean old entries
        join_tracker[chat_id].append((msg['new_chat_participant']['id'], current_time))
        if(len(join_tracker[chat_id]) <= JOIN_LIMIT):
            return False
        # It's a raid - ban all users who joined in this window
        users_to_ban = [(uid, t) for uid, t in join_tracker[chat_id] if uid not in raid_banned_users]
        for uid, _ in users_to_ban:
            try:
                ban_and_blacklist(cookiebot, chat_id, uid)
                raid_banned_users.add(uid)
            except Exception as e:
                print(f"Failed to ban user {uid}: {e}")
        join_tracker[chat_id] = []
        text = i18n.get("blocked_raid", lang=language)
        send_message(cookiebot, chat_id, text)
        return True

def welcome_message(cookiebot, msg, chat_id, limbotimespan, language, is_alternate_bot=0):
    if str(chat_id) in ['-1001063487371', '-1001649779623', '-1001582063371', '-1002048063981', '-1002193913344']: # Groups where the bot should not welcome new members
        return
    send_chat_action(cookiebot, chat_id, 'typing')
    user = msg['new_chat_member'] if 'new_chat_member' in msg else msg['from']
    if limbotimespan > 0:
        try:
            cookiebot.restrictChatMember(chat_id, user['id'], permissions={'can_send_messages': True, 'can_send_media_messages': True, 'can_send_other_messages': True, 'can_add_web_page_previews': True})
            cookiebot.restrictChatMember(chat_id, user['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + limbotimespan))
            text = i18n.get("restrict_message", lang=language, time = round(limbotimespan/60))
            send_message(cookiebot, chat_id, text, language=language)
        except Exception as e:
            print(e)
    welcome = get_request_backend(f'welcomes/{chat_id}')
    if type(welcome) is str or (type(welcome) is not str and 'error' in welcome and welcome['error'] == "Not Found") or 'message' not in welcome:
        if 'chat' in msg and 'title' in msg['chat']:
            welcome = i18n.get("welcome_user", lang=language,user = msg['chat']['title'])
        else:
            welcome = i18n.get("welcome", lang=language)
    elif len(welcome['message']) > 0:
        welcome = welcome['message'].replace('\\n', '\n')
        welcome = substitute_user_tags(welcome, msg)
    try:
        rulesbuttontext = i18n.get("rules", lang=language)
        welcome_card_image = welcome_card(cookiebot, msg, chat_id, language, is_alternate_bot)
        send_photo(cookiebot, chat_id, welcome_card_image, caption=welcome, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=rulesbuttontext,callback_data=f'RULES {language}')]]))
    except Exception as e:
        send_message(cookiebot, chat_id, welcome)
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
            text = i18n.get("kick", lang=language)
            send_message(cookiebot, chat_id, text)
            timer_unban = threading.Timer(30, cookiebot.unbanChatMember, [chat_id, user_id])
            timer_unban.start()
            recently_kicked_checkhuman[cache_key] = current_time
            return True
    return False

def check_cas(cookiebot, msg, chat_id, language):
    try:
        r = requests.get(f"https://api.cas.chat/check?user_id={msg['new_chat_participant']['id']}", timeout=2)
        in_banlist = json.loads(r.text)['ok']
    except Exception as e:
        return False
    if in_banlist:
        ban_and_blacklist(cookiebot, chat_id, msg['new_chat_participant']['id'])
        text = i18n.get("ban_cas", lang=language)
        send_message(cookiebot, chat_id, text)
        return True
    return False

def check_banlist(cookiebot, msg, chat_id, language):
    is_blacklisted = get_request_backend(f"blacklist/{msg['new_chat_participant']['id']}")
    is_blacklisted_username = get_request_backend(f"blacklist/username/{msg['new_chat_participant']['username']}") if 'username' in msg['new_chat_participant'] else {'error': 'no username'}
    fullname = f"{msg['new_chat_participant']['first_name']} {msg['new_chat_participant']['last_name']}" if 'last_name' in msg['new_chat_participant'] else msg['new_chat_participant']['first_name']
    if ('id' in is_blacklisted and is_blacklisted['id'] == str(msg['new_chat_participant']['id'])) or ('id' in is_blacklisted_username and is_blacklisted_username['id'] == msg['new_chat_participant']['username']) or any(forbidden_char in fullname for forbidden_char in ['卐','ζ','𝛇']):
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        text = i18n.get("ban", lang=language)
        send_message(cookiebot, chat_id, text)
        return True
    return False

def check_banlist_public(cookiebot, msg, chat_id, language):
    is_blacklisted = requests.post("https://burrbot.xyz/noraid.php", data={"id": str(msg['new_chat_participant']['id'])})
    raider = json.loads(is_blacklisted.text.replace('""', '"'))['raider']
    if raider:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        text = i18n.get("ban", lang=language)
        send_message(cookiebot, chat_id, text)
        return True
    return False

def captcha_message(cookiebot, msg, chat_id, captchatimespan, language):
    if check_raid(cookiebot, msg, chat_id, language):
        return
    user_id = msg['new_chat_participant']['id']
    try:
        cookiebot.restrictChatMember(chat_id, user_id, permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + captchatimespan))
    except Exception as e:
        print(e)
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    caracters = ['0', '2', '3', '4', '5', '6', '8', '9']
    password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
    captcha.write(password, 'CAPTCHA.png')
    with open('CAPTCHA.png', 'rb') as photo:
        caption = i18n.get("captcha.title", lang=language, name = msg['new_chat_participant']['first_name'], time = round(captchatimespan/60))
        captchaspawnID = send_photo(cookiebot, chat_id, photo, caption=caption, msg_to_reply=msg, reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=i18n.get("captcha.button_approve", lang=language),callback_data=f'CAPTCHAAPPROVE {language} 0')],
            [InlineKeyboardButton(text=i18n.get("captcha.button_call_admin", lang=language),callback_data=f'CAPTCHACALLADMIN {language}')],
            [InlineKeyboardButton(text=i18n.get("captcha.button_not_robot", lang=language),callback_data=f'CAPTCHASELF {language} {msg["new_chat_participant"]["id"]}')]
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
                    if attempts <= 0:
                        reason = i18n.get("captcha.limit", lang=language)
                    else:
                        reason = i18n.get("captcha.time", lang=language)
                    ctx= {
                        "user": user,
                        "reason": reason
                    }
                    try:
                        cookiebot.kickChatMember(chat_id, user)
                        text = i18n.get("captcha.kick", lang=language, **ctx)
                        send_message(cookiebot, chat_id, text)
                        timer_unban = threading.Timer(30, cookiebot.unbanChatMember, [chat_id, user])
                        timer_unban.start()
                    except Exception as e:
                        text = i18n.get("captcha.error_kick", lang=language, **ctx)
                        send_message(cookiebot, chat_id, text)
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
                    else:
                        delete_message(cookiebot, telepot.message_identifier(msg))
                        attempts -= 1
                        if attempts > 0:
                            send_message(cookiebot, chat_id, "Senha incorreta, por favor tente novamente.", language=language)
                        line = f"{chat} {user} {datetime.datetime.now()} {password} {captcha_id} {attempts}\n"
                        text.write(line)
                else:
                    text.write(line)
