# coding=utf8
from universal_funcs import *
from captcha.image import ImageCaptcha
captcha = ImageCaptcha()
import json, requests

def Bemvindo(cookiebot, msg, chat_id, limbotimespan, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    if limbotimespan > 0:
        try:
            cookiebot.restrictChatMember(chat_id, msg['from']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': True, 'can_send_other_messages': True, 'can_add_web_page_previews': True})
            cookiebot.restrictChatMember(chat_id, msg['from']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + limbotimespan))
            Send(cookiebot, chat_id, f"ATENÇÃO! Você está limitado por {round(limbotimespan/60)} minutos. Por favor se apresente e se enturme na conversa com os demais membros.\nUse o /regras para ver as regras do grupo", language=language)
        except Exception as e:
            print(e)
    welcome = GetRequestBackend(f'welcomes/{chat_id}')
    if 'error' in welcome and welcome['error'] == "Not Found":
        try:
            Send(cookiebot, chat_id, f"Olá! As boas-vindas ao grupo {msg['chat']['title']}!", language=language)
        except Exception as e:
            print(e)
            Send(cookiebot, chat_id, "Olá! As boas-vindas ao grupo!", language=language)
    elif len(welcome['message']) > 0:
        welcome = welcome['message'].replace('\\n', '\n')
        cookiebot.sendMessage(chat_id, welcome)
        

def CheckHumanFactor(cookiebot, msg, chat_id, language):
    if 'username' not in msg['new_chat_participant']:
        userphotos = cookiebot.getUserProfilePhotos(msg['new_chat_participant']['id'])
        if userphotos['total_count'] == 0:
            cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
            cookiebot.unbanChatMember(chat_id, msg['new_chat_participant']['id'])
            Send(cookiebot, chat_id, "Bani o novo usuário por suspeita de ser um robô\nSe isso foi um erro, peça para ela adicionar um username (@) e um ADM adicioná-la de volta", language=language)
            return True
    return False

def CheckCAS(cookiebot, msg, chat_id, language):
    try:
        r = requests.get(f"https://api.cas.chat/check?user_id={msg['new_chat_participant']['id']}", timeout=10)
        in_banlist = json.loads(r.text)['ok']
    except Exception as e:
        print(e)
        return False
    if in_banlist == True:
        BanAndBlacklist(cookiebot, chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por ser flagrado pelo sistema anti-ban CAS https://cas.chat/", language=language)
        return True
    return False

def CheckRaider(cookiebot, msg, chat_id, language):
    try:
        r = requests.post('https://burrbot.xyz/noraid.php', data={'id': str(msg['new_chat_participant']['id'])}, timeout=10)
        is_raider = json.loads(r.text)['raider']
    except Exception as e:
        print(e)
        return False
    if is_raider == True:
        BanAndBlacklist(cookiebot, chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por ser flagrado como raider em outros chats\n\nSe isso foi um erro, favor entrar em contato com um administrador do grupo.", language=language)
        return True
    return False

def CheckBlacklist(cookiebot, msg, chat_id, language):
    isBlacklisted = GetRequestBackend(f"blacklist/{msg['new_chat_participant']['id']}")
    if 'error' in isBlacklisted:
        return False
    else:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por ser flagrado como raider em outros chats\n\nSe isso foi um erro, favor entrar em contato com um administrador do grupo.", language=language)
        return True

def Captcha(cookiebot, msg, chat_id, captchatimespan, language):
    try:
        cookiebot.restrictChatMember(chat_id, msg['new_chat_participant']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + captchatimespan))
    except Exception as e:
        print(e)
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    caracters = ['0', '2', '3', '4', '5', '6', '8', '9']
    password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
    captcha.write(password, 'CAPTCHA.png')
    photo = open('CAPTCHA.png', 'rb')
    if language == "pt":
        caption = f"⚠️Digite o código acima para provar que você não é um robô⚠️\n\nVocê tem {round(captchatimespan/60)} minutos, se não resolver nesse tempo te removerei do chat ⏳\n(OBS: Se não aparecem 4 digitos, abra a foto completa)"
    elif language == "es":
        caption = f"⚠️Ingresa el código de arriba para demostrar que no eres un robot⚠️\n\nTienes {round(captchatimespan/60)} minutos, si no lo resuelves en ese tiempo te eliminaré del chat ⏳\n(NOTA: Si no aparecen 4 dígitos, abrir la imagen completa)"
    else:
        caption = f"⚠️Type the code above to prove you're not a robot⚠️\n\nYou have {round(captchatimespan/60)} minutes, if you don't solve it in that time I'll remove you from the chat ⏳\n(NOTE: If 4 digits don't appear, open the full photo)"
    captchaspawnID = cookiebot.sendPhoto(chat_id, photo, caption=caption, reply_to_message_id=msg['message_id'], reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ADMINS: Approve",callback_data='CAPTCHA')]]))['message_id']
    photo.close()
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'a+', encoding='utf-8')
    text.write(str(chat_id) + " " + str(msg['new_chat_participant']['id']) + " " + str(datetime.datetime.now()) + " " + password + " " + str(captchaspawnID) + "\n")
    text.close()

def CheckCaptcha(cookiebot, msg, chat_id, captchatimespan, language):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            #CHATID userID 2021-05-13 11:45:29.027116 password captcha_id
            year = int(line.split()[2].split("-")[0])
            month = int(line.split()[2].split("-")[1])
            day = int(line.split()[2].split("-")[2])
            hour = int(line.split()[3].split(":")[0])
            minute = int(line.split()[3].split(":")[1])
            second = float(line.split()[3].split(":")[2])
            captchasettime = (hour*3600) + (minute*60) + (second)
            chat = int(line.split()[0])
            user = int(line.split()[1])
            if chat == chat_id and captchasettime+captchatimespan <= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                cookiebot.kickChatMember(chat_id, user)
                cookiebot.unbanChatMember(chat_id, user)
                Send(cookiebot, chat, f"Bani o usuário com id {user} por não solucionar o captcha a tempo.\nSe isso foi um erro, peça para um staff adicioná-lo de volta", language=language)
                DeleteMessage(cookiebot, (line.split()[0], line.split()[5]))
            elif chat == chat_id and user == msg['from']['id']:
                text.write(line)
                DeleteMessage(cookiebot, telepot.message_identifier(msg))
            else:    
                text.write(line)
        else:
            pass
    text.close()

def SolveCaptcha(cookiebot, msg, chat_id, button, limbotimespan=0, language='pt'):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            if str(chat_id) == line.split()[0] and button == True:
                cookiebot.sendChatAction(chat_id, 'typing')
                DeleteMessage(cookiebot, (line.split()[0], line.split()[5]))
                Bemvindo(cookiebot, msg, chat_id, limbotimespan, language)
            elif str(chat_id) == line.split()[0] and str(msg['from']['id']) == line.split()[1]:
                cookiebot.sendChatAction(chat_id, 'typing')
                if "".join(msg['text'].upper().split()) == line.split()[4]:
                    DeleteMessage(cookiebot, (line.split()[0], line.split()[5]))
                    DeleteMessage(cookiebot, telepot.message_identifier(msg))
                    Bemvindo(cookiebot, msg, chat_id, limbotimespan, language)
                else:
                    DeleteMessage(cookiebot, telepot.message_identifier(msg))
                    Send(cookiebot, chat_id, "Senha incorreta, por favor tente novamente.", language=language)
                    text.write(line)
            else:
                text.write(line)
    text.close()