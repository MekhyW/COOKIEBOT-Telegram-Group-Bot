DeepaiTOKEN = ''
WolframAPP_ID = ''
OpenAIkey = ''
cookiebotTOKEN = ''
#bombotTOKEN = ''
import os
import subprocess
import sys
import random
import json
import requests
import datetime
import time
import logging
import threading
from captcha.image import ImageCaptcha
import googletrans
from google_images_download import google_images_download
import speech_recognition
import geopy
import wolframalpha
import openai
import unidecode
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
captcha = ImageCaptcha()
translator = googletrans.Translator()
google_images_response = google_images_download.googleimagesdownload()
recognizer = speech_recognition.Recognizer()
WolframCLIENT = wolframalpha.Client(WolframAPP_ID)
openai.api_key = OpenAIkey
cookiebot = telepot.Bot(cookiebotTOKEN)
threads = list()
firstpass = True
start_time = time.time()
lastmessagedate = "1-1-1"
lastmessagetime = "0"
sentcooldownmessage = False
listaadmins = []
listaadmins_id = []
FurBots = 0
stickerspamlimit = 5
messagespamlimit = 10
limbotimespan = 600
captchatimespan = 300
intrometerpercentage = 1
intrometerminimumwords = 12
lowresolutionarea = 10000
funfunctions = 1

#WAIT FOR ANOTHER THREAD/SCRIPT TO FINISH USING FILE
def wait_open(filename):
    if os.path.exists(filename):
        while True:
            try:
                text = open(filename, 'r')
                text.close()
                break
            except IOError:
                pass

#STRING IN FILE CHECKER
def check_if_string_in_file(file_name, string_to_search):
    for line in file_name:
        if string_to_search in line:
            return True
    return False


def CheckCAS(msg, chat_id):
    r = requests.get("https://api.cas.chat/check?user_id={}".format(msg['new_chat_participant']['id']))
    in_banlist = json.loads(r.text)['ok']
    if in_banlist == True:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        cookiebot.sendMessage(chat_id, "Bani o usuário recém-chegado por ser flagrado pelo sistema anti-ban CAS https://cas.chat/")
        return True
    return False


def CheckRaider(msg, chat_id):
    r = requests.post('https://burrbot.xyz/noraid.php', data={'id': '{}'.format(msg['new_chat_participant']['id'])})
    is_raider = json.loads(r.text)['raider']
    if is_raider == True:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        cookiebot.sendMessage(chat_id, "Bani o usuário recém-chegado por ser flagrado como raider em outros chats\n\nSe isso foi um erro, favor entrar em contato com um administrador do grupo.")
        return True
    return False

def Captcha(msg, chat_id):
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

def CheckCaptcha(msg, chat_id):
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
                cookiebot.deleteMessage((line.split()[0], line.split()[5]))
            elif chat == chat_id and user == msg['from']['id']:
                text.write(line)
                try:
                    cookiebot.deleteMessage(telepot.message_identifier(msg))
                except:
                    pass
            else:    
                text.write(line)
        else:
            pass
    text.close()

def SolveCaptcha(msg, chat_id, button):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            if str(chat_id) == line.split()[0] and button == True:
                cookiebot.sendChatAction(chat_id, 'typing')
                cookiebot.sendMessage(chat_id, "Parabéns, você não é um robô!\nDivirta-se no chat!!\nUse o /regras para ver as regras do grupo")
                Bemvindo(msg, chat_id)
                cookiebot.deleteMessage((line.split()[0], line.split()[5]))
            elif str(chat_id) == line.split()[0] and str(msg['from']['id']) == line.split()[1]:
                cookiebot.sendChatAction(chat_id, 'typing')
                if "".join(msg['text'].upper().split()) == line.split()[4]:
                    cookiebot.sendMessage(chat_id, "Parabéns, você não é um robô!\nDivirta-se no chat!!\nUse o /regras para ver as regras do grupo")
                    Bemvindo(msg, chat_id)
                    try:
                        cookiebot.deleteMessage((line.split()[0], line.split()[5]))
                        cookiebot.deleteMessage(telepot.message_identifier(msg))
                    except:
                        pass
                else:
                    cookiebot.sendMessage(chat_id, "Senha incorreta, por favor tente novamente.")
                    text.write(line)
                    try:
                        cookiebot.deleteMessage(telepot.message_identifier(msg))
                    except:
                        pass
            else:
                text.write(line)
    text.close()

def Limbo(msg, chat_id):
    wait_open("Limbo.txt")
    text = open("Limbo.txt", 'a+', encoding='utf-8')
    text.write(str(chat_id) + " " + str(msg['new_chat_participant']['id']) + " " + str(datetime.datetime.now()) + "\n")
    text.close()

def CheckLimbo(msg, chat_id):
    wait_open("Limbo.txt")
    text = open("Limbo.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Limbo.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 4:
            #CHATID userID 2021-05-13 11:45:29.027116
            year = int(line.split()[2].split("-")[0])
            month = int(line.split()[2].split("-")[1])
            day = int(line.split()[2].split("-")[2])
            hour = int(line.split()[3].split(":")[0])
            minute = int(line.split()[3].split(":")[1])
            second = float(line.split()[3].split(":")[2])
            limbosettime = (hour*3600) + (minute*60) + (second)
            if str(chat_id) != line.split()[0] or str(msg['from']['id']) != line.split()[1]:
                text.write(line)
            elif datetime.date.today() == datetime.date(year, month, day) and limbosettime+limbotimespan >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                cookiebot.deleteMessage(telepot.message_identifier(msg))
                text.write(line)
            else:
                pass
        else:
            pass
    text.close()

def left_chat_member(msg, chat_id):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Limbo.txt", 'w+', encoding='utf-8')
    for line in lines:
        if line.split()[0] != str(chat_id) or line.split()[1] != msg['left_chat_member']['id']:
            text.write(line)


def Upscaler(msg, chat_id):
    Area = 0
    for photo in msg['photo']:
        if photo['width'] * photo['height'] > Area:
            Area = photo['width'] * photo['height']
            Fileid = photo['file_id']
    if Area < lowresolutionarea:
        cookiebot.sendChatAction(chat_id, 'upload_photo')
        path = cookiebot.getFile(Fileid)['file_path']
        url = 'https://api.telegram.org/file/bot{}/{}'.format(cookiebotTOKEN, path)
        r = requests.post("https://api.deepai.org/api/torch-srgan", data={'image': '{}'.format(url),},headers={'Api-Key': '{}'.format(DeepaiTOKEN)})
        output_url = r.json()['output_url']
        cookiebot.sendPhoto(chat_id, output_url, caption="Imagem ampliada".format(Area), reply_to_message_id=msg['message_id'])

def Sticker_anti_spam(msg, chat_id):
    wait_open("Stickers.txt")
    text_file = open("Stickers.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    if any(str(chat_id) in string for string in lines):
        pass
    else:
        lines.append("\n"+str(chat_id)+" 0")
    text_file.close()
    counter_new = 0
    for line in lines:
        if str(chat_id) in line:
            counter_new = int(line.split()[1])+1
            break
    text_file = open("Stickers.txt", "w", encoding='utf8')
    for line in lines:
        if str(chat_id) in line:
            text_file.write(line.split()[0] + " " + str(int(line.split()[1])+1) + "\n")
        else:
            text_file.write(line)
    text_file.close()
    if counter_new == stickerspamlimit:
        cookiebot.sendMessage(chat_id, "Cuidado com o flood de stickers.\nMantenham o chat com textos!")
    if counter_new > stickerspamlimit:
        cookiebot.deleteMessage(telepot.message_identifier(msg))

def Location_to_text(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    Latitude = str(msg['location']['latitude'])
    Longitude = str(msg['location']['longitude'])
    Coordinate = Latitude + ", " + Longitude
    location = geopy.geocoders.Nominatim(user_agent="Cookiebot").reverse(Coordinate)
    address = ""
    vector = location.address.split(",")
    i = 0
    while i < len(vector)-7:
        address += vector[i]
        address += ","
        i += 1
    address = address[:-1]
    cookiebot.sendMessage(chat_id, "Endereço: \n\n"+address, reply_to_message_id=msg['message_id'])

def Speech_to_text(msg, chat_id):
    try:
        cookiebot.sendChatAction(chat_id, 'typing')
        r = requests.get("https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, cookiebot.getFile(msg['voice']['file_id'])['file_path']), allow_redirects=True)
        open('VOICEMESSAGE.oga', 'wb').write(r.content)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', 'VOICEMESSAGE.oga', "VOICEMESSAGE.wav", '-y'])
        AUDIO_FILE = "VOICEMESSAGE.wav"
        with speech_recognition.AudioFile(AUDIO_FILE) as source:
            audio = recognizer.record(source)
        voicetext_ptbr = recognizer.recognize_google(audio, language="pt-BR", show_all=True)['alternative'][0]
        #voicetext_enus = recognizer.recognize_google(audio, language="en-US", show_all=True)['alternative'][0]
        Text = voicetext_ptbr['transcript'].capitalize()
        cookiebot.sendMessage(chat_id, "Texto: \n"+'"'+Text+'"', reply_to_message_id=msg['message_id'])
    except:
        pass

def CooldownAction(msg, chat_id):
    global sentcooldownmessage
    if sentcooldownmessage == False:
        cookiebot.sendMessage(chat_id, "Você está em Cooldown!\nApenas use um comando '/' por minuto\nIsso é feito como medida de anti-spam :c\n(OBS: o cooldown foi resetado agora)", reply_to_message_id=msg['message_id'])
        sentcooldownmessage = True
    elif sentcooldownmessage == True:
        cookiebot.deleteMessage(telepot.message_identifier(msg))

def Idade(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if not " " in msg['text']:
        cookiebot.sendMessage(chat_id, "Digite um nome, vou dizer a sua idade!\n\nEx: '/idade Mekhy'\n(obs: só o primeiro nome conta)", reply_to_message_id=msg['message_id'])
    else:
        Nome = msg['text'].replace("/idade ", '').split()[0]
        response = json.loads(requests.get("https://api.agify.io?name={}".format(Nome)).text)
        Idade = response['age']
        Contagem = response['count']
        cookiebot.sendMessage(chat_id, "Sua idade é {} anos! 👴\nRegistrado {} vezes".format(Idade, Contagem), reply_to_message_id=msg['message_id'])

def Genero(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if not " " in msg['text']:
        cookiebot.sendMessage(chat_id, "Digite um nome, vou dizer o seu gênero!\n\nEx: '/genero Mekhy'\n(obs: só o primeiro nome conta)\n(obs 2: POR FAVOR NÃO LEVAR ISSO A SÉRIO, É ZUERA)", reply_to_message_id=msg['message_id'])
    else:
        Nome = msg['text'].replace("/genero ", '').split()[0]
        response = json.loads(requests.get("https://api.genderize.io?name={}".format(Nome)).text)
        Genero = response['gender']
        Probabilidade = response['probability']
        Contagem = response['count']
        if Genero == 'male':
            cookiebot.sendMessage(chat_id, "É um menino! 👨\n\nProbabilidade --> {}%\nRegistrado {} vezes".format(Probabilidade*100, Contagem), reply_to_message_id=msg['message_id'])
        elif Genero == 'female':
            cookiebot.sendMessage(chat_id, "É uma menina! 👩\n\nProbabilidade --> {}%\nRegistrado {} vezes".format(Probabilidade*100, Contagem), reply_to_message_id=msg['message_id'])

def Completar(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if 'reply_to_message' in msg and 'text' in msg['reply_to_message']:
        target = msg['reply_to_message']['text']
    else:
        target = msg['text'].replace("/completar ", '')
    r = requests.post("https://api.deepai.org/api/text-generator",data={'text': translator.translate(target, dest='en').pronunciation,},headers={'api-key': DeepaiTOKEN})
    Answer = translator.translate(r.json()['output'], dest='pt').text
    cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])


def AtualizaBemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Welcome_" + str(chat_id)+".txt")
    text_file = open("Welcome_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Mensagem de Boas Vindas atualizada! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    cookiebot.deleteMessage(telepot.message_identifier(msg['reply_to_message']))

def NovoBemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida quando alguém entrar no grupo", reply_to_message_id=msg['message_id'])

def Bemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Welcome_" + str(chat_id)+".txt")
    if os.path.exists("Welcome_" + str(chat_id)+".txt"):
        with open("Welcome_" + str(chat_id)+".txt", encoding='utf-8') as file:
            regras = file.read()
        cookiebot.sendMessage(chat_id, regras + "\n\nATENÇÃO! Nos primeiros {} minutos, você NÃO PODERÁ MANDAR IMAGENS OU VÍDEOS no grupo".format(str(round(limbotimespan/60))))
    else:    
        cookiebot.sendMessage(chat_id, "Seja bem-vindo(a)!\n\nATENÇÃO! Nos primeiros {} minutos, você NÃO PODERÁ MANDAR IMAGENS OU VÍDEOS no grupo".format(str(round(limbotimespan/60))))

def AtualizaRegras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Regras_" + str(chat_id)+".txt")
    text_file = open("Regras_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Mensagem de regras atualizada! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    cookiebot.deleteMessage(telepot.message_identifier(msg['reply_to_message']))

def NovasRegras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida com o /regras", reply_to_message_id=msg['message_id'])

def Regras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Regras_" + str(chat_id)+".txt")
    if os.path.exists("Regras_" + str(chat_id)+".txt"):
        with open("Regras_" + str(chat_id)+".txt", encoding='utf-8') as file:
            regras = file.read()
        cookiebot.sendMessage(chat_id, regras+"\n\nDúvidas em relação ao bot? Mande para @MekhyW", reply_to_message_id=msg['message_id'])
    else:    
        cookiebot.sendMessage(chat_id, "Ainda não há regras colocadas para esse grupo\nPara tal, use o /novasregras", reply_to_message_id=msg['message_id'])

def RemoveEvento(msg, chat_id):
    if msg['text'] == "/removeevento" or msg['text'] == "/removeevento@CookieMWbot":
        cookiebot.sendChatAction(chat_id, 'typing')
        cookiebot.sendMessage(chat_id, "Se vc é um admin, Mande o ID do evento pra remover\nExemplo: /removeevento 69420", reply_to_message_id=msg['message_id'])
    elif str(msg['from']['username']) in listaadmins:
        cookiebot.sendChatAction(chat_id, 'typing')
        wait_open("Events.txt")
        text_file = open("Events.txt", "r", encoding='utf-8')
        lines = text_file.read().split("\n")
        text_file.close()
        text_file = open("Events.txt", "w", encoding='utf-8')
        query = msg['text'].replace("/removeevento ", '')
        found = False
        for line in lines:
            if len(line.split()) >= 6:
                if query == line.split()[1]:
                    if "REPEAT" not in line:
                        cookiebot.sendMessage(chat_id, "Evento com ID "+line.split()[1]+" Removido!", reply_to_message_id=msg['message_id'])
                    found = True
                else:
                    text_file.write(line+"\n")
        if found == False:
            cookiebot.sendMessage(chat_id, "Não foi possível encontrar o evento com ID "+query, reply_to_message_id=msg['message_id'])
        text_file.close()

def AddEvento(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if not 'reply_to_message' in msg:
        cookiebot.sendMessage(chat_id, "Se vc é um admin, Responda a uma mensagem e diga uma data e hora\n\nExemplo: '31/02/2077 16:21'", reply_to_message_id=msg['message_id'])
    elif str(msg['from']['username']) in listaadmins:
        try:
            time = datetime.datetime.strptime(msg['text'].replace("/addevento ", ''), '%d/%m/%Y %H:%M')
            wait_open("Events.txt")
            text = open("Events.txt", 'a+', encoding='utf-8')
            event = str(chat_id) + " " + str(msg['reply_to_message']['message_id']) + " " + str(datetime.datetime.now()) + " " + str(time) + "\n"
            text.write(event)
            #while not str(time - datetime.datetime.now() - datetime.timedelta(hours=24)).startswith("-"):
            #    time = time - datetime.timedelta(hours=24)
            #    event = str(chat_id) + " " + str(msg['reply_to_message']['message_id']) + " " + str(datetime.datetime.now()) + " " + str(time) + " REPEAT" + "\n"
            #    text.write(event)
            cookiebot.sendMessage(chat_id, "Evento com ID {} adicionado!".format(str(msg['reply_to_message']['message_id'])), reply_to_message_id=msg['message_id'])
            text.close()
        except:
            cookiebot.sendMessage(chat_id, "Formato incorreto, deveria ser /addevento DIA/MES/ANO HORA:MINUTO", reply_to_message_id=msg['message_id'])

def Eventos(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Events.txt")
    text_file = open("Events.txt", "r+", encoding='utf-8')
    lines = text_file.read().split("\n")
    events = []
    dates = []
    def bubbleSort(sorterlist, sortedlist):
        for passnum in range(len(sorterlist)-1,0,-1):
            for i in range(passnum):
                if datetime.date(int(sorterlist[i][0]), int(sorterlist[i][1]), int(sorterlist[i][2])) > datetime.date(int(sorterlist[i+1][0]), int(sorterlist[i+1][1]), int(sorterlist[i+1][2])):
                    temp = sorterlist[i]
                    sorterlist[i] = sorterlist[i+1]
                    sorterlist[i+1] = temp
                    temp = sortedlist[i]
                    sortedlist[i] = sortedlist[i+1]
                    sortedlist[i+1] = temp
    for line in lines:
        if len(line.split()) == 6:
            events.append(line)
            year, month, day = line.split(" ")[4].split("-")
            dates.append([year, month, day])
    text_file.close()
    bubbleSort(dates, events)
    answer = "📅 PROXIMOS EVENTOS REGISTRADOS: 📅\n\n"
    x = 1
    for event in events:
        answer += (str(x) + ") " + "ID " + event.split()[1] + " --> " + event.split()[4] + " " + event.split()[5] + "\n")
        x += 1
    cookiebot.sendMessage(chat_id, answer, reply_to_message_id=msg['message_id'])

def CheckEventos(msg, chat_id):
    wait_open("Events.txt")
    text = open("Events.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Events.txt", 'w', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 6:
            year, month, day = line.split()[4].split("-")
            hour, minute, second = line.split()[5].split(":")
            if datetime.datetime.now() < datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second)):
                text.write(line+"\n")
            else:
                for file in os.listdir():
                    if file.startswith("-"):
                        chatid = file.split(".txt")[0]
                        if chatid.split("-")[1].isdigit():
                            hojeID = cookiebot.forwardMessage(chatid, line.split()[0], line.split()[1])['message_id']
                            if chatid == line.split()[0] and "REPEAT" not in line:
                                cookiebot.pinChatMessage(chatid, hojeID, True)
    text.close()

def TaVivo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Estou vivo\n\nPing enviado em:\n" + str(datetime.datetime.now()))

def Everyone(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if str(msg['from']['username']) not in listaadmins:
        cookiebot.sendMessage(chat_id, "Você não tem permissão para chamar todos os membros do grupo.", reply_to_message_id=msg['message_id'])
    else:
        wait_open(str(chat_id)+".txt")
        text_file = open(str(chat_id)+".txt", "r+", encoding='utf8')
        lines = text_file.readlines()
        result = ""
        for line in lines:
            username = line.split()[0]
            if username != "EVENT":
                result += ("@"+username+" ")
        text_file.close()
        cookiebot.sendMessage(chat_id, result, reply_to_message_id=msg['message_id'])

def Adm(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    response = ""
    for admin in listaadmins:
        response += ("@" + admin + " ")
    cookiebot.sendMessage(chat_id, response, reply_to_message_id=msg['message_id'])

def Comandos(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Cookiebot functions.txt")
    text_file = open("Cookiebot functions.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    string = ""
    for line in lines:
        string += str(line)
    cookiebot.sendMessage(chat_id, string, reply_to_message_id=msg['message_id'])

def Hoje(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Hoje.txt")
    text_file = open("Hoje.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "Hoje pra você é dia de "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def Cheiro(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Cheiro.txt")
    text_file = open("Cheiro.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "*sniff* *sniff*\nHmmmmmm\n\nVocê está com um cheirin de "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def QqEuFaço(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Hoje.txt")
    text_file = open("Hoje.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "Vai "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def IdeiaDesenho(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    ideiasdesenho = os.listdir('IdeiaDesenho')
    ideiaID = random.randint(0, len(ideiasdesenho)-1)
    photo = open('IdeiaDesenho'+'/'+ideiasdesenho[ideiaID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, caption="Referência com ID {}\n\nNão trace sem dar créditos! (use a busca reversa do google images)".format(ideiaID), reply_to_message_id=msg['message_id'])

def Contato(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, '\nAre you a business or sponsor?\n💌 Email: felipe_catapano@yahoo.com.br')
    cookiebot.sendMessage(chat_id, 'Want to message me? Or Report a problem?\n🔵 Telegram: @MekhyW\n')
    cookiebot.sendMessage(chat_id, '\nGet in touch with what I´m doing\n🐦 Twitter: https://twitter.com/MekhyW\n')
    cookiebot.sendMessage(chat_id, '\nWant a match with a like?\n⚪ Howlr: Mekhy W.!\n')
    cookiebot.sendMessage(chat_id, '\nDo you use LinkedIn?\n🟦 LinkedIn: https://www.linkedin.com/in/felipe-catapano/\n')
    cookiebot.sendMessage(chat_id, '\nCheck out my other projects!\n⚛️ GitHub: https://github.com/MekhyW\n')

def PromptQualquerCoisa(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Troque o 'qualquercoisa' por algo, vou mandar uma foto desse algo\n\nEXEMPLO: /fennec\n(acentos, letras maiusculas e espaços não funcionam)", reply_to_message_id=msg['message_id'])

def CustomCommand(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    images = os.listdir(msg['text'].replace('/', '').replace("@CookieMWbot", ''))
    imageID = random.randint(0, len(images)-1)
    photo = open(msg['text'].replace('/', '').replace("@CookieMWbot", '')+'/'+images[imageID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])

def QualquerCoisa(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    searchterm = msg['text'].split("@")[0].replace("/", '').replace("@CookieMWbot", '')
    orig_stdout = sys.stdout
    f = open('URLS.txt', 'w')
    sys.stdout = f
    arguments = {"keywords":searchterm, "limit":30, "print_urls":True, "no_download":True,  "safe_search":True}
    paths = google_images_download.googleimagesdownload().download(arguments)
    sys.stdout = orig_stdout
    f.close()
    with open('URLS.txt') as f:
        content = f.readlines()
    f.close()
    urls = []
    for j in range(len(content)):
        if content[j][:7] == 'Printed':
            urls.append(content[j-1][11:-1])
    try:
        index = random.randint(0, len(urls)-1)
        cookiebot.sendPhoto(chat_id, urls[index], reply_to_message_id=msg['message_id'])
    except:
        index = random.randint(0, len(urls)-1)
        cookiebot.sendPhoto(chat_id, urls[index], reply_to_message_id=msg['message_id'])

def Quem(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
    wait_open(str(chat_id)+".txt")
    text_file = open(str(chat_id)+".txt", "r+", encoding='utf-8')
    lines = text_file.readlines()
    target = None
    while len(lines)>1 and (target in (None, '') or target.startswith("EVENT")):
        target = lines[random.randint(0, len(lines)-1)].replace("\n", '')
        target = target.split()[0]
    cookiebot.sendMessage(chat_id, LocucaoAdverbial+"@"+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def OnSay(msg, chat_id):
    if len(msg['text'].split()) > 3:
        keyword_texts = []
        for word in msg['text'].split():
            keyword_texts.append(unidecode.unidecode(''.join(filter(str.isalnum, word.lower()))))
        print(keyword_texts)
        wait_open("Onsay_Dictionary.txt")
        text_file = open("Onsay_Dictionary.txt", 'r', encoding='utf8')
        lines = text_file.readlines()
        text_file.close()
        for line in lines:
            if len(line.split(" > ")) == 2:
                queries = json.loads(line.split(" > ")[0])
                answer = line.split(" > ")[1]
                if set(queries).issubset(keyword_texts):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, answer, reply_to_message_id=msg['message_id'])
                    return True
    return False

def InteligenciaArtificial(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']:
        message = msg['text'].replace("Cookiebot", '').replace("cookiebot", '').replace("@CookieMWbot", '').replace("COOKIEBOT", '').replace("CookieBot", '').replace("\n", '').capitalize()
    else:
        message = msg['text'].replace("\n", '').capitalize()
    try:
        r = WolframCLIENT.query(translator.translate(message, dest='en').text)
        Answer = translator.translate(next(r.results).text, dest='pt').text.capitalize()
        if len(Answer) > 200:
            raise "Flood"
        else:
            cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])
    except:
        r = requests.get('https://api.simsimi.net/v1/?text={}&lang=pt&cf=true'.format(message))
        try:
            Answer = json.loads(r.text)['messages'][0]['response'].capitalize()
        except:
            Answer = str(r.text).split("{")[1]
            Answer = "{" + Answer
            Answer = json.loads(Answer)['messages'][0]['response'].capitalize()
        Answer = translator.translate(Answer, dest='pt').text
        cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])

def InteligenciaArtificial2(msg, chat_id):
    if 'reply_to_message' in msg and 'text' in msg['reply_to_message']:
        message = msg['reply_to_message']['text'].capitalize() + ". " + msg['text'].capitalize()
    else:
        message = msg['text'].capitalize()
    message_eng = translator.translate(message, dest='en').text
    if "you" in message_eng:
        return False
    try:
        r = openai.Completion.create(
            engine="davinci",
            prompt="If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with \"Unknown\".\n\nQ: What is human life expectancy in the United States?\nA: Human life expectancy in the United States is 78 years.\n\nQ: What is the square root of banana?\nA: Unknown\n\nQ: How does a telescope work?\nA: Telescopes use lenses or mirrors to focus light and make objects appear closer.\n\nQ: Where were the 1992 Olympics held?\nA: The 1992 Olympics were held in Barcelona, Spain.\n\nQ: How many squigs are in a bonk?\nA: Unknown\n\nQ: {}\nA:".format(message_eng),
            temperature=0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n"]
        )
        Answer = r["choices"][0]["text"]
        if "Unknown" in Answer:
            return False
        else:
            cookiebot.sendChatAction(chat_id, 'typing')
            Answer = translator.translate(Answer, dest='pt').text.capitalize()
            cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])
            return True
    except:
        return False


def AddtoStickerDatabase(msg, chat_id):
    wait_open("Sticker_Database.txt")
    text = open("Sticker_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Sticker_Database.txt", 'w', encoding='utf-8')
    if len(lines) > 1000:
        i = len(lines) - 1000
    else:
        i = 0
    while i < len(lines):
        if not lines[i] == "\n":
            text.write(lines[i])
        i += 1
    i = 0
    text.write(msg['sticker']['file_id'] + "\n")
    text.close()

def ReplySticker(msg, chat_id):
    wait_open("Sticker_Database.txt")
    text = open("Sticker_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    cookiebot.sendSticker(chat_id, random.choice(lines).replace("\n", ''), reply_to_message_id=msg['message_id'])

def Configurar(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if str(msg['from']['username']) in listaadmins:
        wait_open("Config_"+str(chat_id)+".txt")
        text = open("Config_"+str(chat_id)+".txt", 'r', encoding='utf-8')
        variables = text.read()
        text.close()
        cookiebot.sendMessage(msg['from']['id'],"Configuração atual:\n\n" + variables + '\n\nEscolha a variável que vc gostaria de alterar', reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text="FurBots",callback_data='a CONFIG {}'.format(str(chat_id))), InlineKeyboardButton(text="Lim Stickers",callback_data='b CONFIG {}'.format(str(chat_id))), InlineKeyboardButton(text="Lim Msgs",callback_data='i CONFIG {}'.format(str(chat_id))),InlineKeyboardButton(text="🕒 Limbo",callback_data='c CONFIG {}'.format(str(chat_id))), InlineKeyboardButton(text="🕒 CAPTCHA",callback_data='d CONFIG {}'.format(str(chat_id)))],
                                   [InlineKeyboardButton(text="% Intrometer",callback_data='e CONFIG {}'.format(str(chat_id))), InlineKeyboardButton(text="N Intrometer",callback_data='f CONFIG {}'.format(str(chat_id))), InlineKeyboardButton(text="Área Ampliar",callback_data='g CONFIG {}'.format(str(chat_id))), InlineKeyboardButton(text="Diversão",callback_data='h CONFIG {}'.format(str(chat_id)))]
                               ]
                           ))
        cookiebot.sendMessage(chat_id,"Te mandei uma mensagem no chat privado para configurar" , reply_to_message_id=msg['message_id'])
    else:
        cookiebot.sendMessage(chat_id, "Você não tem permissão para configurar o bot!", reply_to_message_id=msg['message_id'])

def ConfigurarSettar(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if msg['text'].isdigit():
        variable_to_be_altered = ""
        if "Use 1 para não interferir com outros furbots caso eles estejam no grupo, ou 0 se eu for o único." in msg['reply_to_message']['text']:
            variable_to_be_altered = "FurBots"
        elif "Este é o limite máximo de stickers permitidos em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Sticker_Spam_Limit"
        elif "Este é o tempo pelo qual novos usuários no grupo não poderão mandar imagens (o bot apaga automaticamente)." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Tempo_sem_poder_mandar_imagem"
        elif "Este é o tempo que novos usuários dispõem para resolver o Captcha. USE 0 PARA DESLIGAR O CAPTCHA!" in msg['reply_to_message']['text']:
            variable_to_be_altered = "Tempo_Captcha"
        elif "Esta é a porcentagem de chance em porcentagem de eu responder a uma mensagem aleatoriamente, se ela for grande o suficiente." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Intrometer_Percentage"
        elif "Este é o mínimo de termos necessários em uma mensagem para eu responder de forma aleatória." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Intrometer_minimum_words"
        elif "Esta é a área máxima, em píxeis quadrados, que eu vou levar em consideração ao ampliar imagens de baixa resolução." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Low_resolution_area"
        elif "Use 1 para permitir comandos e funcionalidades de diversão, ou 0 para apenas as funções de controle/gerenciamento." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Funções_Diversão"
        elif "Este é o limite máximo de mensagens permitidas em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Message_Spam_Limit"
        chat_to_alter = msg['reply_to_message']['text'].split("\n")[0].split("= ")[1]
        wait_open("Config_"+str(chat_to_alter)+".txt")
        text_file = open("Config_"+str(chat_to_alter)+".txt", 'r', encoding='utf-8')
        lines = text_file.readlines()
        text_file.close()
        text_file = open("Config_"+str(chat_to_alter)+".txt", 'w', encoding='utf-8')
        for line in lines:
            if variable_to_be_altered in line:
                text_file.write(variable_to_be_altered + ": " + msg['text'] + "\n")
                cookiebot.sendMessage(chat_id, "Variável configurada! ✔️\nPode retornar ao chat")
                cookiebot.deleteMessage(telepot.message_identifier(msg['reply_to_message']))
                cookiebot.deleteMessage(telepot.message_identifier(msg))
            elif len(line.split()) > 1:
                text_file.write(line)
        text_file.close()
    else:
        cookiebot.sendMessage(chat_id, "Apenas números naturais são aceitos!", reply_to_message_id=msg['message_id'])




#MAIN THREAD FUNCTION
def thread_function(msg):
        global firstpass
        if time.time() - start_time > 3:
            firstpass = False
        if firstpass == False:
            content_type, chat_type, chat_id = telepot.glance(msg)
            print(content_type, chat_type, chat_id, msg['message_id'], msg['from']['id'])
            if chat_type == 'private' and 'reply_to_message' not in msg:
                if msg['text'] == "/stop" and 'username' in msg['from'] and msg['from']['username'] == 'MekhyW':
                    os._exit(0)
                cookiebot.sendMessage(chat_id, "Olá, sou o CookieBot!\n\nSou um bot com AI de conversa, de assistência, conteúdo infinito e conteúdo customizado.\nSe quiser me adicionar no seu chat ou obter a lista de comandos comentada, mande uma mensagem para o @MekhyW\n\nSe está procurando o bot de controle da minha fursuit, use o @mekhybot")
            elif chat_type != 'private' and "MekhyW" not in str(cookiebot.getChatAdministrators(chat_id)):
                cookiebot.sendMessage(chat_id, "Posso apenas ficar no grupo se o @MekhyW estiver nele, e for um admin!\n\nIsso é feito para evitar spam e raids, me desculpem")
                cookiebot.leaveChat(chat_id)
            elif chat_type == 'private' or "CookieMWbot" in str(cookiebot.getChatAdministrators(chat_id)) or "MekhysBombot" in str(cookiebot.getChatAdministrators(chat_id)):
                global listaadmins
                global listaadmins_id
                global FurBots
                global stickerspamlimit
                global messagespamlimit
                global limbotimespan
                global captchatimespan
                global intrometerpercentage
                global intrometerminimumwords
                global lowresolutionarea
                global funfunctions
                if chat_type != 'private':
                    #BEGGINING OF ADMINISTRATORS GATHERING
                    if not os.path.exists("GranularAdmins_" + str(chat_id)+".txt"):
                        text = open("GranularAdmins_" + str(chat_id)+".txt", 'w').close()
                    wait_open("GranularAdmins_" + str(chat_id)+".txt")
                    text_file = open("GranularAdmins_" + str(chat_id)+".txt", 'r', encoding='utf-8')
                    lines = text_file.readlines()
                    text_file.close()
                    if lines != []:
                        listaadmins = []
                        for username in lines:
                            listaadmins.append(username.replace("\n", ''))
                    else:
                        listaadmins = []
                        listaadmins_id = []
                        for admin in cookiebot.getChatAdministrators(chat_id):
                            if 'username' in admin['user']:
                                listaadmins.append(str(admin['user']['username']))
                            listaadmins_id.append(str(admin['user']['id']))
                    #END OF ADMINISTRATORS GATHERING
                    #BEGGINING OF NEW NAME GATHERING
                    if not os.path.isfile(str(chat_id)+".txt"):
                        open(str(chat_id)+".txt", 'a', encoding='utf-8').close() 
                    wait_open(str(chat_id)+".txt")
                    text_file = open(str(chat_id)+".txt", "r+", encoding='utf-8')
                    if 'username' in msg['from'] and (check_if_string_in_file(text_file, msg['from']['username']) == False):
                        text_file.write("\n"+msg['from']['username'])
                    text_file.close()
                    #END OF NEW NAME GATHERING
                    #BEGGINNING OF CONFIG GATHERING
                    if not os.path.isfile("Config_"+str(chat_id)+".txt"):
                        open("Config_"+str(chat_id)+".txt", 'a', encoding='utf-8').close()
                        text_file = open("Config_"+str(chat_id)+".txt", "w", encoding='utf-8')
                        text_file.write("FurBots: 0\nSticker_Spam_Limit: 5\nMessage_Spam_Limit: 10\nTempo_sem_poder_mandar_imagem: 600\nTempo_Captcha: 300\nIntrometer_Percentage: 1\nIntrometer_minimum_words: 12\nLow_resolution_area: 10000\nFunções_Diversão: 1")
                        text_file.close()
                    wait_open("Config_"+str(chat_id)+".txt")
                    text_file = open("Config_"+str(chat_id)+".txt", "r", encoding='utf-8')
                    lines = text_file.readlines()
                    text_file.close()
                    for line in lines:
                        if line.split()[0] == "FurBots:":
                            FurBots = int(line.split()[1])
                        elif line.split()[0] == "Sticker_Spam_Limit:":
                            stickerspamlimit = int(line.split()[1])
                        elif line.split()[0] == "Message_Spam_Limit:":
                            messagespamlimit = int(line.split()[1])
                        elif line.split()[0] == "Tempo_sem_poder_mandar_imagem:":
                            limbotimespan = int(line.split()[1])
                        elif line.split()[0] == "Tempo_Captcha:":
                            captchatimespan = int(line.split()[1])
                        elif line.split()[0] == "Intrometer_Percentage:":
                            intrometerpercentage = int(line.split()[1])
                        elif line.split()[0] == "Intrometer_minimum_words:":
                            intrometerminimumwords = int(line.split()[1])
                        elif line.split()[0] == "Low_resolution_area:":
                            lowresolutionarea = int(line.split()[1])
                        elif line.split()[0] == "Funções_Diversão:":
                            funfunctions = int(line.split()[1])
                    #END OF CONFIG GATHERING
                    #BEGINNING OF CALENDAR SYNC AND FURBOTS CHECK
                    wait_open(str(chat_id)+".txt")
                    text_file = open(str(chat_id)+".txt", "r", encoding='utf-8')
                    lines = text_file.read().split("\n")
                    text_file.close()
                    text_file = open(str(chat_id)+".txt", "w", encoding='utf-8')
                    for line in lines:
                        if line == '':
                            pass
                        elif 'username' in msg['from'] and line.startswith(msg['from']['username']):
                            global lastmessagedate
                            global lastmessagetime
                            global sentcooldownmessage
                            entry = line.split()
                            if 'text' in msg:
                                if msg['text'].startswith("/"):
                                    if len(entry) == 3:
                                        now = entry[2].split(":")
                                        lastmessagedate = entry[1]
                                        lastmessagetime = (float(now[0])*3600)+(float(now[1])*60)+(float(now[2])*1)
                                    else:
                                        lastmessagedate = "1-1-1"
                                        lastmessagedate = "0"
                                    if lines.index(line) == len(lines)-1:
                                        text_file.write(entry[0]+" "+str(datetime.datetime.now()))
                                    else:
                                        text_file.write(entry[0]+" "+str(datetime.datetime.now())+"\n")
                                else:
                                    if lines.index(line) == len(lines)-1:
                                        text_file.write(line)
                                    else:
                                        text_file.write(line+"\n")
                        elif lines.index(line) == len(lines)-1:
                            text_file.write(line)
                        else:
                            text_file.write(line+"\n")
                    text_file.close()
                    #END OF CALENDAR SYNC AND FURBOTS CHECK
                if content_type == "new_chat_member":
                    if CheckCAS(msg, chat_id) == False and CheckRaider(msg, chat_id) == False:
                        Limbo(msg, chat_id)
                        if captchatimespan > 0:
                            Captcha(msg, chat_id)
                        else:
                            Bemvindo(msg, chat_id)
                elif content_type == "left_chat_member":
                    left_chat_member(msg, chat_id)
                elif content_type == "voice":
                    if funfunctions == True:
                        Speech_to_text(msg, chat_id)
                elif content_type == "audio":
                    pass
                elif content_type == "photo":
                    CheckLimbo(msg, chat_id)
                    Upscaler(msg, chat_id)
                elif content_type == "video":
                    CheckLimbo(msg, chat_id)
                elif content_type == "document":
                    if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                        ReplySticker(msg, chat_id)
                elif content_type == "sticker":
                    Sticker_anti_spam(msg, chat_id)
                    AddtoStickerDatabase(msg, chat_id)
                    if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                        ReplySticker(msg, chat_id)
                elif content_type == "location":
                    Location_to_text(msg, chat_id)
                #elif 'text' in msg and msg['text'].startswith("/") and " " not in msg['text'] and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and str(datetime.date.today()) == lastmessagedate and float(lastmessagetime)+60 >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)) and 'username' in msg['from'] and str(msg['from']['username']) not in listaadmins:
                #    CooldownAction(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/idade") and funfunctions == True:
                    Idade(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/genero") and funfunctions == True:
                    Genero(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/completar") and funfunctions == True:
                    Completar(msg, chat_id)
                elif 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida quando alguém entrar no grupo" and str(msg['from']['username']) in listaadmins:
                    AtualizaBemvindo(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/novobemvindo"):
                    NovoBemvindo(msg, chat_id)
                elif FurBots == False and 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida com o /regras" and str(msg['from']['username']) in listaadmins:
                    AtualizaRegras(msg, chat_id)
                elif FurBots == False and 'text' in msg and msg['text'].startswith("/novasregras"):
                    NovasRegras(msg, chat_id)
                elif FurBots == False and 'text' in msg and msg['text'].startswith("/regras"):
                    Regras(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/removeevento"):
                    RemoveEvento(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/addevento"):
                    AddEvento(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/eventos"):
                    Eventos(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/tavivo"):
                    TaVivo(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/everyone"):
                    Everyone(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/adm"):
                    Adm(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/comandos"):
                    Comandos(msg, chat_id)
                elif FurBots == False and 'text' in msg and (msg['text'].startswith("/hoje") or msg['text'].startswith("/today")) and funfunctions == True:
                    Hoje(msg, chat_id)
                elif FurBots == False and 'text' in msg and (msg['text'].startswith("/cheiro") or msg['text'].startswith("/smell")) and funfunctions == True:
                    Cheiro(msg, chat_id)
                elif FurBots == False and 'text' in msg and ('eu faço' in msg['text'] or 'eu faco' in msg['text']) and '?' in msg['text'] and funfunctions == True:
                    QqEuFaço(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/ideiadesenho") and funfunctions == True:
                    IdeiaDesenho(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/contato"):
                    Contato(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/qualquercoisa") and funfunctions == True:
                    PromptQualquerCoisa(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/configurar"):
                    Configurar(msg, chat_id)
                elif 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "Responda ESTA mensagem com o novo valor da variável" in msg['reply_to_message']['text']:
                    ConfigurarSettar(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/") and " " not in msg['text'] and os.path.exists(msg['text'].replace('/', '').replace("@CookieMWbot", '')) and funfunctions == True:
                    CustomCommand(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/") and " " not in msg['text'] and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and funfunctions == True:
                    QualquerCoisa(msg, chat_id)
                elif 'text' in msg and (msg['text'].startswith("Cookiebot") or msg['text'].startswith("cookiebot") or 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') and ("quem" in msg['text'] or "Quem" in msg['text']) and ("?" in msg['text']):
                    Quem(msg, chat_id)
                elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and msg['reply_to_message']['caption'] == "Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo te removerei do chat\n(OBS: Se não aparecem 4 digitos, abra a foto completa)".format(str(round(captchatimespan/60))):
                    SolveCaptcha(msg, chat_id, False)
                elif 'text' in msg and ((random.randint(1, 100)<=intrometerpercentage and len(msg['text'].split())>=intrometerminimumwords) or ('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') or "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']) and funfunctions == True:
                    if not OnSay(msg, chat_id):
                        InteligenciaArtificial(msg, chat_id)
                elif 'text' in msg and "?" in msg['text'] and len(msg['text'].split()) >= intrometerminimumwords and funfunctions == True and InteligenciaArtificial2(msg, chat_id):
                    pass
                elif 'text' in msg:
                    CheckEventos(msg, chat_id)
                    SolveCaptcha(msg, chat_id, False)
                    CheckCaptcha(msg, chat_id)
                    OnSay(msg, chat_id)
                #BEGGINNING OF COOLDOWN UPDATES
                if 'text' in msg:
                    if float(lastmessagetime)+60 < ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                        sentcooldownmessage = False
                    wait_open("Stickers.txt")
                    text_file = open("Stickers.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    text_file.close()
                    text_file = open("Stickers.txt", "w", encoding='utf8')
                    for line in lines:
                        if str(chat_id) in line:
                            text_file.write(line.split()[0] + " " + "0" + "\n")
                        else:
                            text_file.write(line)
                    text_file.close()
                #END OF COOLDOWN UPDATES

#MESSAGE HANDLER
def handle(msg):
    try:
        global threads
        messagehandle = threading.Thread(target=thread_function, args=(msg,))
        threads.append(messagehandle)
        messagehandle.start()
    except:
        pass

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    if query_data.startswith('a CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nUse 1 para não interferir com outros furbots caso eles estejam no grupo, ou 0 se eu for o único.\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('b CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o limite máximo de stickers permitidos em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo.\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('c CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o tempo pelo qual novos usuários no grupo não poderão mandar imagens (o bot apaga automaticamente).\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('d CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o tempo que novos usuários dispõem para resolver o Captcha. USE 0 PARA DESLIGAR O CAPTCHA!\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('e CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEsta é a porcentagem de chance em porcentagem de eu responder a uma mensagem aleatoriamente, se ela for grande o suficiente.\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('f CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o mínimo de termos necessários em uma mensagem para eu responder de forma aleatória.\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('g CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEsta é a área máxima, em píxeis quadrados, que eu vou levar em consideração ao ampliar imagens de baixa resolução.\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('h CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 para permitir comandos e funcionalidades de diversão, ou 0 para apenas as funções de controle/gerenciamento.\nResponda ESTA mensagem com o novo valor da variável".format(query_data.split()[2]))
    elif query_data.startswith('i CONFIG'):
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nEste é o limite máximo de mensagens permitidas em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo.\nResponda ESTA mensagem com o novo valor da variável".format(query_data.split()[2]))
    else:
        global listaadmins_id
        listaadmins_id = []
        for admin in cookiebot.getChatAdministrators(msg['message']['reply_to_message']['chat']['id']):
            listaadmins_id.append(str(admin['user']['id']))
        if query_data == 'CAPTCHA' and str(from_id) in listaadmins_id:
            cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
            SolveCaptcha(msg, msg['message']['reply_to_message']['chat']['id'], True)
        

MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()