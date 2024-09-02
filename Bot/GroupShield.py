# coding=utf8
from universal_funcs import *
from captcha.image import ImageCaptcha
import spamwatch
import threading
import json, requests
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

captcha = ImageCaptcha()
evildb_ids, evildb_usernames = [], []
try:
    spamwatch_client = spamwatch.Client(spamwatch_token)
except Exception as e:
    print(e)
    spamwatch_client = None

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

def openTelegramImage(cookiebot, token, photo_id):
    photo_info = cookiebot.getFile(photo_id)
    photo_url = f"https://api.telegram.org/file/bot{token}/{photo_info['file_path']}"
    resp = urllib.request.urlopen(photo_url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def SubstituteUsertags(text, msg):
    if 'new_chat_member' in msg:
        user = msg['new_chat_member']
    else:
        user = msg['from']
    usertags = ['{user}', '{username}', '{mention}', '$user', '$username', '$(user)', '$(username)', '<user>', '<username>', '<name>']
    for usertag in usertags:
        if usertag in text:
            if 'username' in user:
                text = text.replace(usertag, f"@{user['username']}")
            else:
                text = text.replace(usertag, f"{user['first_name']}")
    return text

def Regras(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    rules = GetRequestBackend(f"rules/{chat_id}")
    if 'error' in rules and rules['error'] == "Not Found":    
        Send(cookiebot, chat_id, "Ainda não há regras colocadas para esse grupo\n<blockquote>Para colocar regras, use o /novasregras</blockquote>", msg, language)
    else:
        regras = rules['rules'].replace('\\n', '\n')
        regras = SubstituteUsertags(regras, msg)
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

def WelcomeCard(cookiebot, msg, chat_id, language, isAlternate=0):
    if 'new_chat_member' in msg:
        user = msg['new_chat_member']
    else:
        user = msg['from']
    # Get base images
    token = GetBotToken(isAlternate)
    try:
        photo_id = cookiebot.getUserProfilePhotos(user['id'])['photos'][0][-1]['file_id']
        user_img = openTelegramImage(cookiebot, token, photo_id)
    except (KeyError, IndexError):
        user_img = cv2.imread('Static/No_Image_Available.jpg', cv2.IMREAD_COLOR)
    try:
        url = 'https://api.telegram.org/bot{}/getChat?chat_id={}'.format(token, chat_id)
        data = requests.get(url).json()
        photo_id = data['result']['photo']['big_file_id']
        chat_img = openTelegramImage(cookiebot, token, photo_id)
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
    for i in range(0, user_img.shape[0]):
        for j in range(0, user_img.shape[1]):
            if math.sqrt((i - circle_radius)**2 + (j - circle_radius)**2) < circle_radius:
                blurred_chat_img[circle_center[1] - circle_radius + i, circle_center[0] - circle_radius + j] = user_img[i, j]
    # Insert text
    cv2.rectangle(blurred_chat_img, (0, int(size[0]*0.36)), (size[1]*10, int(size[0]*0.40)), (0, 0, 0), -1)
    if language == 'pt':
        welcome = 'Bem-vinde ao'
    elif language == 'es':
        welcome = 'Bienvenido a'
    else:
        welcome = 'Welcome to'
    font = ImageFont.truetype('Static/Roadgeek2005Engschrift-lgJw.ttf', 32)
    img_pil = Image.fromarray(blurred_chat_img)
    draw = ImageDraw.Draw(img_pil)    
    chat_title = emoji_pattern.sub(r'', cookiebot.getChat(chat_id)['title'].strip())
    user_firstname = emoji_pattern.sub(r'', user['first_name'].strip())             
    text = f'{welcome} {chat_title}, {user_firstname}!'
    textW, textH = draw.textbbox((0, 0), text, font=font)[2:]
    textX = int(((size[1]*2.2) - textW) / 2)
    textY = int(((size[0]*0.69) + textH) / 2)
    draw.text((textX, textY), text, font = font, fill = (255, 255, 255, 0))
    final_img = np.array(img_pil)
    # Save image and return
    cv2.imwrite("welcome_card.png", final_img)
    final_img = open("welcome_card.png", 'rb')
    return final_img

def Bemvindo(cookiebot, msg, chat_id, limbotimespan, language, isAlternate=0):
    if str(chat_id) in ['-1001063487371', '-1001649779623', '-1001582063371', '-1002048063981', '-1002193913344']: # Groups where the bot should not welcome new members
        return
    SendChatAction(cookiebot, chat_id, 'typing')
    if limbotimespan > 0:
        try:
            cookiebot.restrictChatMember(chat_id, msg['from']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': True, 'can_send_other_messages': True, 'can_add_web_page_previews': True})
            cookiebot.restrictChatMember(chat_id, msg['from']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + limbotimespan))
            Send(cookiebot, chat_id, f"ATENÇÃO! Suas mídias estão restritas por <b>{round(limbotimespan/60)} minutos</b>. Por favor se apresente e se enturme na conversa com os membros.\n<blockquote>Use o /regras para ver as regras do grupo</blockquote>", language=language)
        except Exception as e:
            print(e)
    welcome = GetRequestBackend(f'welcomes/{chat_id}')
    if 'error' in welcome and welcome['error'] == "Not Found":
        try:
            welcome = f"Olá! As boas-vindas ao grupo {msg['chat']['title']}!"
        except Exception as e:
            print(e)
            welcome = f"Olá! As boas-vindas ao grupo!"
    elif len(welcome['message']) > 0:
        welcome = welcome['message'].replace('\\n', '\n')
        welcome = SubstituteUsertags(welcome, msg)
    try:
        if language=='pt':
            rulesbuttontext = 'Veja as Regras!'
        elif language=='es':
            rulesbuttontext = 'Ver las Reglas!'
        else:
            rulesbuttontext = 'See the Rules!'
        welcome_card = WelcomeCard(cookiebot, msg, chat_id, language, isAlternate)
        SendPhoto(cookiebot, chat_id, welcome_card, caption=welcome, language=language, 
                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=rulesbuttontext,callback_data=f'RULES {language}')]]))
    except Exception as e:
        print(e)
        Send(cookiebot, chat_id, welcome, language=language)
    for thread in threading.enumerate():
        if isinstance(thread, threading.Timer) and 'chat_id' in thread.kwargs and thread.kwargs['chat_id'] == chat_id and 'msg' in thread.kwargs and thread.kwargs['msg']['new_chat_participant']['id'] == msg['from']['id']:
            thread.cancel()

def CheckHumanFactor(cookiebot, msg, chat_id, language):
    if 'username' not in msg['new_chat_participant']:
        userphotos = cookiebot.getUserProfilePhotos(msg['new_chat_participant']['id'])
        if userphotos['total_count'] == 0:
            cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
            Send(cookiebot, chat_id, "Kickei o novo usuário por <b>suspeita de ser um robô</b>\n<blockquote>Se isso foi um erro, peça para ele adicionar um username (@) ou foto de perfil e um ADM adicioná-lo de volta</blockquote>", language=language)
            cookiebot.unbanChatMember(chat_id, msg['new_chat_participant']['id'])
            return True
    return False

def CheckCAS(cookiebot, msg, chat_id, language):
    try:
        r = requests.get(f"https://api.cas.chat/check?user_id={msg['new_chat_participant']['id']}", timeout=2)
        in_banlist = json.loads(r.text)['ok']
    except Exception as e:
        print(e)
        return False
    if in_banlist:
        BanAndBlacklist(cookiebot, chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por <b>ser flagrado pelo [sistema anti-ban CAS](https://cas.chat/)</b>", language=language)
        return True
    return False

def CheckSpamwatch(cookiebot, msg, chat_id, language):
    try:
        isbanned = spamwatch_client.get_ban(int(msg['new_chat_participant']['id']))
    except Exception as e:
        print(e)
        return False
    if isbanned:
        BanAndBlacklist(cookiebot, chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por <b>ser flagrado pelo sistema anti-ban Spamwatch</b>", language=language)
        return True
    return False

def CheckBlacklist(cookiebot, msg, chat_id, language):
    isBlacklisted = GetRequestBackend(f"blacklist/{msg['new_chat_participant']['id']}")
    if 'error' in isBlacklisted:
        return False
    else:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por <b>ser flagrado como conta falsa/spam em outros chats</b>", language=language)
        return True

def Captcha(cookiebot, msg, chat_id, captchatimespan, language):
    try:
        cookiebot.restrictChatMember(chat_id, msg['new_chat_participant']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + captchatimespan))
    except Exception as e:
        print(e)
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    caracters = ['0', '2', '3', '4', '5', '6', '8', '9']
    password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
    captcha.write(password, 'CAPTCHA.png')
    with open('CAPTCHA.png', 'rb') as photo:
        caption = f"⚠️Digite o código acima OU aperte o botão abaixo⚠️\n\nVocê tem {round(captchatimespan/60)} minutos, se não resolver nesse tempo te removerei do chat ⏳\n(Se não aparecem 4 digitos, abra a foto completa)"
        captchaspawnID = SendPhoto(cookiebot, chat_id, photo, caption=caption, language=language, msg_to_reply=msg, reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ADMINS: Approve",callback_data=f'CAPTCHAAPPROVE {language} 0')],
            [InlineKeyboardButton(text="I'm not a Robot!",callback_data=f'CAPTCHASELF {language} {msg["new_chat_participant"]["id"]}')]
        ]))
    wait_open("Captcha.txt")
    with open("Captcha.txt", 'r', encoding='utf-8') as text:
        lines = text.readlines()
    with open("Captcha.txt", 'w+', encoding='utf-8') as text:
        for line in lines:
            if len(line.split()) >= 5:
                hour, minute, second, captchasettime, chat, user, password, captcha_id, attempts = parseLineCaptcha(line)
                if chat == chat_id and user == msg['new_chat_participant']['id']:
                    for thread in threading.enumerate():
                        if isinstance(thread, threading.Timer) and thread.kwargs['chat_id'] == chat_id and thread.kwargs['msg']['new_chat_participant']['id'] == msg['new_chat_participant']['id']:
                            thread.cancel()
                else:
                    text.write(line)
        text.write(f"{chat_id} {msg['new_chat_participant']['id']} {datetime.datetime.now()} {password} {captchaspawnID} 5\n")
    timer = threading.Timer(captchatimespan+1, CheckCaptcha, kwargs={'cookiebot': cookiebot, 'msg': msg, 'chat_id': chat_id, 'captchatimespan': captchatimespan, 'language': language})
    timer.start()

def parseLineCaptcha(line):
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

def CheckCaptcha(cookiebot, msg, chat_id, captchatimespan, language):
    wait_open("Captcha.txt")
    with open("Captcha.txt", 'r', encoding='utf-8') as text:
        lines = text.readlines()
    with open("Captcha.txt", 'w+', encoding='utf-8') as text:
        for line in lines:
            if len(line.split()) >= 5:
                hour, minute, second, captchasettime, chat, user, password, captcha_id, attempts = parseLineCaptcha(line)
                if chat == chat_id and (captchasettime+captchatimespan <= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)) or attempts <= 0):
                    if attempts <= 0:
                        reason = "exceder o limite de tentativas para resolver o captcha"
                    else:
                        reason = "não solucionar o captcha a tempo"
                    try:
                        cookiebot.kickChatMember(chat_id, user)
                    except Exception as e:
                        print(e)
                    Send(cookiebot, chat, f"Kickei o usuário com id <b>{user}</b> por <b>{reason}</b>.\n<blockquote>Se isso foi um erro, peça para um staff adicioná-lo de volta</blockquote>", language=language)
                    cookiebot.unbanChatMember(chat_id, user)
                    DeleteMessage(cookiebot, (str(chat), str(captcha_id)))
                elif chat == chat_id and user == msg['from']['id']:
                    text.write(line)
                    DeleteMessage(cookiebot, telepot.message_identifier(msg))
                else:    
                    text.write(line)

def SolveCaptcha(cookiebot, msg, chat_id, button, limbotimespan=0, language='pt', isAlternate=0):
    wait_open("Captcha.txt")
    with open("Captcha.txt", 'r', encoding='utf-8') as text:
        lines = text.readlines()
    if len(lines) == 0 and button:
        DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
        return
    with open("Captcha.txt", 'w+', encoding='utf-8') as text:
        for line in lines:
            if len(line.split()) >= 5:
                hour, minute, second, captchasettime, chat, user, password, captcha_id, attempts = parseLineCaptcha(line)
                if str(chat_id) == str(chat) and button:
                    SendChatAction(cookiebot, chat_id, 'typing')
                    DeleteMessage(cookiebot, (str(chat), str(captcha_id)))
                    msg['new_chat_member'] = cookiebot.getChatMember(chat, str(user))['user']
                    Bemvindo(cookiebot, msg, chat, limbotimespan, language, isAlternate)
                elif str(chat_id) == str(chat) and str(msg['from']['id']) == str(user):
                    SendChatAction(cookiebot, chat_id, 'typing')
                    solveattempt = "".join(msg['text'].upper().split())
                    if solveattempt.isnumeric() and len(solveattempt) == 4:
                        DeleteMessage(cookiebot, (str(chat), str(captcha_id)))
                        DeleteMessage(cookiebot, telepot.message_identifier(msg))
                        Bemvindo(cookiebot, msg, chat_id, limbotimespan, language, isAlternate)
                    else:
                        DeleteMessage(cookiebot, telepot.message_identifier(msg))
                        attempts -= 1
                        if attempts > 0:
                            Send(cookiebot, chat_id, "Senha incorreta, por favor tente novamente.", language=language)
                        line = f"{chat} {user} {datetime.datetime.now()} {password} {captcha_id} {attempts}\n"
                        text.write(line)
                else:
                    text.write(line)