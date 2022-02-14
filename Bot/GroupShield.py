from universal_funcs import *
from captcha.image import ImageCaptcha
captcha = ImageCaptcha()
import json, requests

def Bemvindo(cookiebot, msg, chat_id, limbotimespan):
    cookiebot.sendChatAction(chat_id, 'typing')
    if limbotimespan > 0:
        try:
            cookiebot.restrictChatMember(chat_id, msg['from']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + limbotimespan))
            cookiebot.sendMessage(chat_id, "ATENÇÃO! Você está limitado por {} minutos. Por favor se apresente e se enturme na conversa com os demais membros.\nUse o /regras para ver as regras do grupo".format(str(round(limbotimespan/60))))
        except Exception as e:
            print(e)
    if os.path.exists("Welcome/Welcome_" + str(chat_id)+".txt"):
        wait_open("Welcome/Welcome_" + str(chat_id)+".txt")
        with open("Welcome/Welcome_" + str(chat_id)+".txt", encoding='utf-8') as file:
            welcome = file.read()
            cookiebot.sendMessage(chat_id, welcome)
            file.close()
    else:
        try:
            cookiebot.sendMessage(chat_id, "Olá! Seja bem-vinde ao grupo {}!".format(msg['chat']['title']))
        except:
            cookiebot.sendMessage(chat_id, "Olá! Seja bem-vinde ao grupo!")

def CheckCAS(cookiebot, msg, chat_id):
    r = requests.get("https://api.cas.chat/check?user_id={}".format(msg['new_chat_participant']['id']), timeout=10)
    in_banlist = json.loads(r.text)['ok']
    if in_banlist == True:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        cookiebot.sendMessage(chat_id, "Bani o usuário recém-chegado por ser flagrado pelo sistema anti-ban CAS https://cas.chat/")
        return True
    return False


def CheckRaider(cookiebot, msg, chat_id):
    r = requests.post('https://burrbot.xyz/noraid.php', data={'id': '{}'.format(msg['new_chat_participant']['id'])}, timeout=10)
    is_raider = json.loads(r.text)['raider']
    if is_raider == True:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        cookiebot.sendMessage(chat_id, "Bani o usuário recém-chegado por ser flagrado como raider em outros chats\n\nSe isso foi um erro, favor entrar em contato com um administrador do grupo.")
        return True
    return False

def Captcha(cookiebot, msg, chat_id, captchatimespan):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    caracters = ['0', '2', '3', '4', '5', '6', '8', '9']
    password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
    captcha.write(password, 'CAPTCHA.png')
    photo = open('CAPTCHA.png', 'rb')
    captchaspawnID = cookiebot.sendPhoto(chat_id, photo, caption="Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo te removerei do chat\n(OBS: Se não aparecem 4 digitos, abra a foto completa)".format(str(round(captchatimespan/60))), reply_to_message_id=msg['message_id'], reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ADMINS: Aprovar",callback_data='CAPTCHA')]]))['message_id']
    photo.close()
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'a+', encoding='utf-8')
    text.write(str(chat_id) + " " + str(msg['new_chat_participant']['id']) + " " + str(datetime.datetime.now()) + " " + password + " " + str(captchaspawnID) + "\n")
    text.close()

def CheckCaptcha(cookiebot, msg, chat_id, captchatimespan):
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
                cookiebot.kickChatMember(chat, user)
                cookiebot.sendMessage(chat, "Bani o usuário com id {} por não solucionar o captcha a tempo.\nSe isso foi um erro, peça para um staff adicioná-lo de volta".format(user))
                DeleteMessage(cookiebot, (line.split()[0], line.split()[5]))
            elif chat == chat_id and user == msg['from']['id']:
                text.write(line)
                DeleteMessage(cookiebot, telepot.message_identifier(msg))
            else:    
                text.write(line)
        else:
            pass
    text.close()

def SolveCaptcha(cookiebot, msg, chat_id, button, limbotimespan=0):
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
                Bemvindo(cookiebot, msg, chat_id, limbotimespan)
            elif str(chat_id) == line.split()[0] and str(msg['from']['id']) == line.split()[1]:
                cookiebot.sendChatAction(chat_id, 'typing')
                if "".join(msg['text'].upper().split()) == line.split()[4]:
                    DeleteMessage(cookiebot, (line.split()[0], line.split()[5]))
                    DeleteMessage(cookiebot, telepot.message_identifier(msg))
                    Bemvindo(cookiebot, msg, chat_id, limbotimespan)
                else:
                    DeleteMessage(cookiebot, telepot.message_identifier(msg))
                    cookiebot.sendMessage(chat_id, "Senha incorreta, por favor tente novamente.")
                    text.write(line)
            else:
                text.write(line)
    text.close()

def left_chat_member(msg, chat_id):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()