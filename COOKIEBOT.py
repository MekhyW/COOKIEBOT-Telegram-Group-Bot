DeepaiTOKEN = ''
spotipyCLIENT_ID = ''
spotipyCLIENT_SECRET = ''
WolframAPP_ID = ''
cookiebotTOKEN = ''
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
import spotipy
import speech_recognition
import geopy
import wolframalpha
import unidecode
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
captcha = ImageCaptcha()
translator = googletrans.Translator()
google_images_response = google_images_download.googleimagesdownload()
spotify = spotipy.Spotify(spotipy.oauth2.SpotifyClientCredentials(client_id=spotipyCLIENT_ID, client_secret=spotipyCLIENT_SECRET).get_access_token())
recognizer = speech_recognition.Recognizer()
WolframCLIENT = wolframalpha.Client(WolframAPP_ID)
cookiebot = telepot.Bot(cookiebotTOKEN)
threads = list()
firstpass = True
start_time = time.time()
lastmessagedate = "1-1-1"
lastmessagetime = "0"
FurBots = 0
sentcooldownmessage = False
stickerspamlimit = 5
limbotimespan = 600
captchatimespan = 300
intrometerpercentage = 1
intrometerminimumwords = 6
lowresolutionarea = 76800
funfunctions = 1

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

def Captcha(msg, chat_id):
    caracters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
    captcha.write(password, 'CAPTCHA.png')
    photo = open('CAPTCHA.png', 'rb')
    captchaspawnID = cookiebot.sendPhoto(chat_id, photo, caption="Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo vc será expulso".format(str(captchatimespan/60)), reply_to_message_id=msg['message_id'])['message_id']
    photo.close()
    text = open("Captcha.txt", 'a+', encoding='utf-8')
    text.write(str(chat_id) + " " + str(msg['new_chat_participant']['id']) + " " + str(datetime.datetime.now()) + " " + password + " " + str(captchaspawnID) + "\n")
    text.close()

def CheckCaptcha(msg, chat_id):
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            #CHATID userID 2021-05-13 11:45:29.027116 password
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
            elif chat == chat_id and user == msg['from']['id']:
                cookiebot.deleteMessage(telepot.message_identifier(msg))
                text.write(line)
            else:    
                text.write(line)
        else:
            pass
    text.close()

def SolveCaptcha(msg, chat_id):
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            if str(chat_id) == line.split()[0] and str(msg['from']['id']) == line.split()[1]:
                cookiebot.sendChatAction(chat_id, 'typing')
                if "".join(msg['text'].upper().split()) == line.split()[4]:
                    cookiebot.sendMessage(chat_id, "Parabéns, você não é um robô!\nDivirta-se no chat!!", reply_to_message_id=msg['message_id'])
                    cookiebot.deleteMessage((line.split()[0], line.split()[5]))
                else:
                    cookiebot.sendMessage(chat_id, "Senha incorreta, por favor tente novamente.", reply_to_message_id=msg['message_id'])
                    text.write(line)
            else:
                text.write(line)
    text.close()

def Limbo(msg, chat_id):
    text = open("Limbo.txt", 'a+', encoding='utf-8')
    text.write(str(chat_id) + " " + str(msg['new_chat_participant']['id']) + " " + str(datetime.datetime.now()) + "\n")
    text.close()

def CheckLimbo(msg, chat_id):
    text = open("Limbo.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Limbo.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) == 4:
            #CHATID userID 2021-05-13 11:45:29.027116
            year = int(line.split()[2].split("-")[0])
            month = int(line.split()[2].split("-")[1])
            day = int(line.split()[2].split("-")[2])
            hour = int(line.split()[3].split(":")[0])
            minute = int(line.split()[3].split(":")[1])
            second = float(line.split()[3].split(":")[2])
            limbosettime = (hour*3600) + (minute*60) + (second)
            if str(chat_id) != line.split()[0] or str(msg['new_chat_participant']['id']) != line.split()[1]:
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
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Perdemos um soldado\n\nF 😔", reply_to_message_id=msg['message_id'])
    photo = open('Brasil_flag.gif', 'rb')
    cookiebot.sendPhoto(chat_id, photo)

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
    text_file = open("Stickers.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    text_file.close()
    counter_new = 0
    for line in lines:
        if str(chat_id) in line:
            counter_new = int(line.split()[1])+1
            break
        elif line == lines[len(lines)-1]:
            text_file = open("Stickers.txt", "a+", encoding='utf8')
            text_file.write("\n"+str(chat_id)+" 0")
            text_file.close()
    text_file = open("Stickers.txt", "w", encoding='utf8')
    for line in lines:
        if str(chat_id) in line:
            text_file.write(line.split()[0] + " " + str(int(line.split()[1])+1) + "\n")
        else:
            text_file.write(line)
    text_file.close()
    if counter_new == stickerspamlimit:
        cookiebot.sendMessage(chat_id, "Flood de stickers detectado\nMantenha o chat com texto!", reply_to_message_id=msg['message_id'])
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
    cookiebot.sendChatAction(chat_id, 'typing')
    r = requests.get("https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, cookiebot.getFile(msg['voice']['file_id'])['file_path']), allow_redirects=True)
    open('VOICEMESSAGE.oga', 'wb').write(r.content)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', 'VOICEMESSAGE.oga', "VOICEMESSAGE.wav", '-y'])
    AUDIO_FILE = "VOICEMESSAGE.wav"
    with speech_recognition.AudioFile(AUDIO_FILE) as source:
        audio = recognizer.record(source)
    voicetext_ptbr = recognizer.recognize_google(audio, language="pt-BR", show_all=True)['alternative'][0]
    voicetext_enus = recognizer.recognize_google(audio, language="en-US", show_all=True)['alternative'][0]
    if 'confidence' in voicetext_ptbr and 'confidence' in voicetext_enus:
        if voicetext_ptbr['confidence'] > voicetext_enus['confidence']:
            Text = voicetext_ptbr['transcript'].capitalize()
        else:
            Text = voicetext_enus['transcript'].capitalize()
    elif 'confidence' in voicetext_ptbr:
        Text = voicetext_ptbr['transcript'].capitalize()
    else:
        Text = voicetext_enus['transcript'].capitalize()
    cookiebot.sendMessage(chat_id, "Texto: \n\n"+'"'+Text+'"', reply_to_message_id=msg['message_id'])

def CooldownAction(msg, chat_id):
    global sentcooldownmessage
    if sentcooldownmessage == False:
        cookiebot.sendMessage(chat_id, "Você está em Cooldown!\nApenas use um comando '/' por minuto\nIsso é feito como medida de anti-spam :c\n(OBS: o cooldown foi resetado agora)", reply_to_message_id=msg['message_id'])
        sentcooldownmessage = True
    elif sentcooldownmessage == True:
        cookiebot.deleteMessage(telepot.message_identifier(msg))

def Escolha(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if len(msg['text'].split()) == 1:
        cookiebot.sendMessage(chat_id, "Envie os termos pra escolher\nEXEMPLO: '/escolher A, B, C'", reply_to_message_id=msg['message_id'])
    else:
        terms = msg['text'].split(",")
        cookiebot.sendMessage(chat_id, terms[random.randint(1, len(terms)-1)].capitalize(), reply_to_message_id=msg['message_id'])

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

def Startup(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    r = requests.get("http://itsthisforthat.com/api.php?text")
    startup = translator.translate(r.text, dest='pt').text
    cookiebot.sendMessage(chat_id, "{} Criou uma startup!\nO slogan é:\n'{}'".format(msg['from']['username'], startup))

def AddHoje(msg, chat_id):
    if 'reply_to_message' in msg:
        cookiebot.sendChatAction(chat_id, 'typing')
        text_file = open("Hoje.txt", "a+", encoding='utf8')
        text_file.write("\n"+msg['reply_to_message']['text'].replace("\n", "\\n"))
        text_file.close()
        cookiebot.sendMessage(chat_id, "Coisa idiota pra fazer adicionada! ✅", reply_to_message_id=msg['message_id'])

def AddCheiro(msg, chat_id):
    if 'reply_to_message' in msg:
        cookiebot.sendChatAction(chat_id, 'typing')
        text_file = open("Cheiro.txt", "a+", encoding='utf8')
        text_file.write("\n"+msg['reply_to_message']['text'].replace("\n", "\\n"))
        text_file.close()
        cookiebot.sendMessage(chat_id, "Cheirin exótico adicionado! ✅", reply_to_message_id=msg['message_id'])


def AtualizaBemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
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
    if os.path.exists("Welcome_" + str(chat_id)+".txt"):
        with open("Welcome_" + str(chat_id)+".txt", encoding='utf-8') as file:
            regras = file.read()
        cookiebot.sendMessage(chat_id, regras + "\n\nATENÇÃO! Nos primeiros {} minutos, você NÃO PODERÁ MANDAR IMAGENS no grupo\nUse o /regras para ver as regras do grupo".format(str(limbotimespan/60)), reply_to_message_id=msg['message_id'])
    else:    
        cookiebot.sendMessage(chat_id, "Seja bem vindo(a)!\n\nATENÇÃO! Nos primeiros {} minutos, você NÃO PODERÁ MANDAR IMAGENS no grupo\nUse o /regras para ver as regras do grupo".format(str(limbotimespan/60)), reply_to_message_id=msg['message_id'])

def AtualizaRegras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
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
    elif msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
        cookiebot.sendChatAction(chat_id, 'typing')
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
    elif msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
        try:
            time = datetime.datetime.strptime(msg['text'].replace("/addevento ", ''), '%d/%m/%Y %H:%M')
            text = open("Events.txt", 'a+', encoding='utf-8')
            event = str(chat_id) + " " + str(msg['reply_to_message']['message_id']) + " " + str(datetime.datetime.now()) + " " + str(time) + "\n"
            text.write(event)
            while not str(time - datetime.datetime.now() - datetime.timedelta(hours=24)).startswith("-"):
                time = time - datetime.timedelta(hours=24)
                event = str(chat_id) + " " + str(msg['reply_to_message']['message_id']) + " " + str(datetime.datetime.now()) + " " + str(time) + " REPEAT" + "\n"
                text.write(event)
            cookiebot.sendMessage(chat_id, "Evento com ID {} adicionado!".format(str(msg['reply_to_message']['message_id'])), reply_to_message_id=msg['message_id'])
            text.close()
        except:
            cookiebot.sendMessage(chat_id, "Formato incorreto, deveria ser /addevento DIA/MES/ANO HORA:MINUTO", reply_to_message_id=msg['message_id'])

def Eventos(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
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
    if msg['from']['username'] not in str(cookiebot.getChatAdministrators(chat_id)):
        cookiebot.sendMessage(chat_id, "Apenas admins podem chamar todos os membros do grupo.", reply_to_message_id=msg['message_id'])
    else:
        text_file = open(str(chat_id)+".txt", "r+", encoding='utf8')
        lines = text_file.readlines()
        result = ""
        for line in lines:
            username = line.split()[0]
            if username != "EVENT":
                result += ("@"+username+" ")
        text_file.close()
        cookiebot.sendMessage(chat_id, result, reply_to_message_id=msg['message_id'])

def Comandos(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    text_file = open("Cookiebot functions.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    string = ""
    for line in lines:
        string += str(line)
    cookiebot.sendMessage(chat_id, string, reply_to_message_id=msg['message_id'])

def Hoje(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    text_file = open("Hoje.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "Hoje pra você é dia de "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def Cheiro(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    text_file = open("Cheiro.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "*sniff* *sniff*\nHmmmmmm\n\nVocê está com um cheirin de "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def QqEuFaço(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    text_file = open("Hoje.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "Vai "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def Portugues(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if 'reply_to_message' not in msg:
        cookiebot.sendMessage(chat_id, "Responda uma mensagem, vou traduzir ela para o português \n(FUNCIONA COM QUALQUER LINGUA)", reply_to_message_id=msg['message_id'])
    else:
        translation = translator.translate(msg['reply_to_message']['text'], dest='pt').text
        cookiebot.sendMessage(chat_id, "Tradução para pt/br:\n\n'{}'".format(translation), reply_to_message_id=msg['message_id'])

def Ingles(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if 'reply_to_message' not in msg:
        cookiebot.sendMessage(chat_id, "Responda uma mensagem, vou traduzir ela para o inglês \n(FUNCIONA COM QUALQUER LINGUA)", reply_to_message_id=msg['message_id'])
    else:
        translation = translator.translate(msg['reply_to_message']['text'], dest='en').text
        cookiebot.sendMessage(chat_id, "Tradução para inglês:\n\n'{}'".format(translation), reply_to_message_id=msg['message_id'])

def Insulto(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    insult = json.loads(requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json').text)['insult']
    insulto = translator.translate(insult, dest='pt').text
    cookiebot.sendMessage(chat_id, insulto, reply_to_message_id=msg['message_id'])

def Numero(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if len(msg['text'].split()) == 1:
        cookiebot.sendMessage(chat_id, "Mande um número, vou dizer fatos sobre ele!\nExemplo: /numero 42", reply_to_message_id=msg['message_id'])
    else:
        number = msg['text'].replace("/numero ", '')
        historical_fact = translator.translate(requests.get('http://numbersapi.com/{}'.format(number)).text, dest='pt').text
        mathematical_fact = translator.translate(requests.get('http://numbersapi.com/{}/math'.format(number)).text, dest='pt').text
        final_text = historical_fact+"\n\nAlém disso, "+mathematical_fact
        cookiebot.sendMessage(chat_id, final_text, reply_to_message_id=msg['message_id'])

def DadJoke(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    text_file = open("DadJokes.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, target, reply_to_message_id=msg['message_id'])
    text_file.close()

def IdeiaDesenho(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    ideiasdesenho = os.listdir('IdeiaDesenho')
    ideiaID = random.randint(0, len(ideiasdesenho)-1)
    photo = open('IdeiaDesenho'+'/'+ideiasdesenho[ideiaID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, caption="Referência com ID {}\n\nNão trace sem dar créditos! (use a busca reversa do google images)".format(ideiaID), reply_to_message_id=msg['message_id'])

def Portal(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    portal = os.listdir('portal')
    portalID = random.randint(0, len(portal)-1)
    photo = open('portal'+'/'+portal[portalID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])

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
    if "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text']:
        message = msg['text'].replace("Cookiebot", '').replace("cookiebot", '').replace("@CookieMWbot", '').replace("COOKIEBOT", '').replace("\n", '').capitalize()
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

def IdentificaMusica(msg, chat_id):
    spotify = spotipy.Spotify(spotipy.oauth2.SpotifyClientCredentials(client_id=spotipyCLIENT_ID, client_secret=spotipyCLIENT_SECRET).get_access_token())
    results = spotify.search(q=msg['text'], type="track", limit=1, offset=0)
    if results['tracks']['total']:
        names = ''
        for artist in results['tracks']['items'][0]['album']['artists']:
            names += ", {}".format(artist['name'])
        names = names[2:]
        cookiebot.sendAudio(chat_id, results['tracks']['items'][0]['preview_url'], caption=results['tracks']['items'][0]['name'], title=results['tracks']['items'][0]['name'], performer=names, reply_to_message_id=msg['message_id'])

def AddtoStickerDatabase(msg, chat_id):
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
    text = open("Sticker_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    cookiebot.sendSticker(chat_id, random.choice(lines).replace("\n", ''), reply_to_message_id=msg['message_id'])

def Configurar(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
        text = open("Config_"+str(chat_id)+".txt", 'r', encoding='utf-8')
        variables = text.read()
        text.close()
        cookiebot.sendMessage(chat_id,"Configuração atual:\n\n" + variables + '\n\nEscolha a variável que vc gostaria de alterar', reply_to_message_id=msg['message_id'], reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text="FurBots",callback_data='a'), InlineKeyboardButton(text="Limite Stickers",callback_data='b'),InlineKeyboardButton(text="🕒 Limbo",callback_data='c'), InlineKeyboardButton(text="🕒 CAPTCHA",callback_data='d')],
                                   [InlineKeyboardButton(text="% Intrometer",callback_data='e'), InlineKeyboardButton(text="N Intrometer",callback_data='f'), InlineKeyboardButton(text="Área Ampliar",callback_data='g'), InlineKeyboardButton(text="Diversão",callback_data='h')]
                               ]
                           ))
    else:
        cookiebot.sendMessage(chat_id, "Apenas admins podem configurar o bot!", reply_to_message_id=msg['message_id'])

def ConfigurarSettar(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
        if msg['text'].isdigit():
            variable_to_be_altered = ""
            if msg['reply_to_message']['text'].startswith("Use 1 para não interferir com outros furbots caso eles estejam no grupo, ou 0 se eu for o único.\nResponda ESTA mensagem com o novo valor da variável"):
                variable_to_be_altered = "FurBots"
            elif msg['reply_to_message']['text'].startswith("Este é o limite máximo de stickers permitidos em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo."):
                variable_to_be_altered = "Sticker_Spam_Limit"
            elif msg['reply_to_message']['text'].startswith("Este é o tempo pelo qual novos usuários no grupo não poderão mandar imagens (o bot apaga automaticamente)."):
                variable_to_be_altered = "Tempo_sem_poder_mandar_imagem"
            elif msg['reply_to_message']['text'].startswith("Este é o tempo que novos usuários dispõem para resolver o Captcha. USE 0 PARA DESLIGAR O CAPTCHA!"):
                variable_to_be_altered = "Tempo_Captcha"
            elif msg['reply_to_message']['text'].startswith("Esta é a porcentagem de chance em porcentagem de eu responder a uma mensagem aleatoriamente, se ela for grande o suficiente."):
                variable_to_be_altered = "Intrometer_Percentage"
            elif msg['reply_to_message']['text'].startswith("Este é o mínimo de termos necessários em uma mensagem para eu responder de forma aleatória."):
                variable_to_be_altered = "Intrometer_minimum_words"
            elif msg['reply_to_message']['text'].startswith("Esta é a área máxima, em píxeis quadrados, que eu vou levar em consideração ao ampliar imagens de baixa resolução."):
                variable_to_be_altered = "Low_resolution_area"
            elif msg['reply_to_message']['text'].startswith("Use 1 para permitir comandos e funcionalidades de diversão, ou 0 para apenas as funções de controle/gerenciamento."):
                variable_to_be_altered = "Funções_Diversão"
            text_file = open("Config_"+str(chat_id)+".txt", 'r', encoding='utf-8')
            lines = text_file.readlines()
            text_file.close()
            text_file = open("Config_"+str(chat_id)+".txt", 'w', encoding='utf-8')
            for line in lines:
                if variable_to_be_altered in line:
                    text_file.write(variable_to_be_altered + ": " + msg['text'] + "\n")
                    cookiebot.sendMessage(chat_id, "Variável configurada! ✔️")
                    cookiebot.deleteMessage(telepot.message_identifier(msg['reply_to_message']))
                    cookiebot.deleteMessage(telepot.message_identifier(msg))
                elif len(line.split()) > 1:
                    text_file.write(line)
            text_file.close()
        else:
            cookiebot.sendMessage(chat_id, "Apenas números naturais são aceitos!", reply_to_message_id=msg['message_id'])
    else:
        cookiebot.sendMessage(chat_id, "Apenas admins podem configurar o bot!", reply_to_message_id=msg['message_id'])




#MAIN THREAD FUNCTION
def thread_function(msg):
        global firstpass
        if time.time() - start_time > 3:
            firstpass = False
        if firstpass == False:
            content_type, chat_type, chat_id = telepot.glance(msg)
            print(content_type, chat_type, chat_id, msg['message_id'], msg['from']['id'])
            if chat_type == 'private':
                if msg['text'] == "/stop" and 'username' in msg['from'] and msg['from']['username'] == 'MekhyW':
                    os._exit(0)
                cookiebot.sendMessage(chat_id, "Olá, sou o Cookiebot!\n\nSou um bot com AI de conversa, de assistência, conteúdo infinito e conteúdo customizado.\nSe quiser me adicionar no seu chat ou obter a lista de comandos comentada, mande uma mensagem para o @MekhyW\n\nSe está procurando um bot com proteção para grupos e administração, use o @burrsobot\n\nSe está procurando o bot de controle da minha fursuit, use o @mekhybot")
            elif "MekhyW" not in str(cookiebot.getChatAdministrators(chat_id)):
                cookiebot.sendMessage(chat_id, "Posso apenas ficar no grupo se o @MekhyW estiver nele, e for um admin!\n\nIsso é feito para evitar spam e raids, me desculpem")
                cookiebot.leaveChat(chat_id)
            elif "CookieMWbot" in str(cookiebot.getChatAdministrators(chat_id)):
                #BEGGINING OF NEW NAME GATHERING
                if not os.path.isfile(str(chat_id)+".txt"):
                    open(str(chat_id)+".txt", 'a', encoding='utf-8').close() 
                text_file = open(str(chat_id)+".txt", "r+", encoding='utf-8')
                if 'username' in msg['from'] and (check_if_string_in_file(text_file, msg['from']['username']) == False):
                    text_file.write("\n"+msg['from']['username'])
                text_file.close()
                #END OF NEW NAME GATHERING
                #BEGGINNING OF CONFIG GATHERING
                global FurBots
                global stickerspamlimit
                global limbotimespan
                global captchatimespan
                global intrometerpercentage
                global intrometerminimumwords
                global lowresolutionarea
                global funfunctions
                if not os.path.isfile("Config_"+str(chat_id)+".txt"):
                    open("Config_"+str(chat_id)+".txt", 'a', encoding='utf-8').close()
                    text_file = open("Config_"+str(chat_id)+".txt", "w", encoding='utf-8')
                    text_file.write("FurBots: 0\nSticker_Spam_Limit: 5\nTempo_sem_poder_mandar_imagem: 600\nTempo_Captcha: 300\nIntrometer_Percentage: 1\nIntrometer_minimum_words: 6\nLow_resolution_area: 76800\nFunções_Diversão: 1")
                    text_file.close()
                text_file = open("Config_"+str(chat_id)+".txt", "r", encoding='utf-8')
                lines = text_file.readlines()
                text_file.close()
                for line in lines:
                    if line.split()[0] == "FurBots:":
                        FurBots = int(line.split()[1])
                    elif line.split()[0] == "Sticker_Spam_Limit:":
                        stickerspamlimit = int(line.split()[1])
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
                    if CheckCAS(msg, chat_id) == False:
                        Bemvindo(msg, chat_id)
                        Limbo(msg, chat_id)
                        if captchatimespan > 0:
                            Captcha(msg, chat_id)
                elif content_type == "voice":
                    Speech_to_text(msg, chat_id)
                elif content_type == "audio":
                    pass
                elif content_type == "photo":
                    CheckLimbo(msg, chat_id)
                    Upscaler(msg, chat_id)
                elif content_type == "document":
                    pass
                elif content_type == "sticker":
                    Sticker_anti_spam(msg, chat_id)
                    AddtoStickerDatabase(msg, chat_id)
                    if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                        ReplySticker(msg, chat_id)
                elif content_type == "location":
                    Location_to_text(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/") and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and str(datetime.date.today()) == lastmessagedate and float(lastmessagetime)+60 >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)) and 'username' in msg['from'] and msg['from']['username'] not in str(cookiebot.getChatAdministrators(chat_id)):
                    CooldownAction(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/escolha") and funfunctions == True:
                    Escolha(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/idade") and funfunctions == True:
                    Idade(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/genero") and funfunctions == True:
                    Genero(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/completar") and funfunctions == True:
                    Completar(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/startup") and funfunctions == True:
                    Startup(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/addhoje") and funfunctions == True:
                    AddHoje(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/addcheiro") and funfunctions == True:
                    AddCheiro(msg, chat_id)
                elif 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida quando alguém entrar no grupo" and msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
                    AtualizaBemvindo(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/novobemvindo"):
                    NovoBemvindo(msg, chat_id)
                elif FurBots == False and 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida com o /regras" and msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
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
                elif 'text' in msg and msg['text'].startswith("/nada"):
                    pass
                elif 'text' in msg and msg['text'].startswith("/tavivo"):
                    TaVivo(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/everyone"):
                    Everyone(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/comandos"):
                    Comandos(msg, chat_id)
                elif FurBots == False and 'text' in msg and (msg['text'].startswith("/hoje") or msg['text'].startswith("/today")) and funfunctions == True:
                    Hoje(msg, chat_id)
                elif FurBots == False and 'text' in msg and (msg['text'].startswith("/cheiro") or msg['text'].startswith("/smell")) and funfunctions == True:
                    Cheiro(msg, chat_id)
                elif FurBots == False and 'text' in msg and ('eu faço' in msg['text'] or 'eu faco' in msg['text']) and '?' in msg['text'] and funfunctions == True:
                    QqEuFaço(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/portugues"):
                    Portugues(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/ingles"):
                    Ingles(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/insulto") and funfunctions == True:
                    Insulto(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/numero") and funfunctions == True:
                    Numero(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/dadjoke") and funfunctions == True:
                    DadJoke(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/ideiadesenho") and funfunctions == True:
                    IdeiaDesenho(msg, chat_id)
                elif 'text' in msg and msg['text'].startswith("/portal") and funfunctions == True:
                    Portal(msg, chat_id)
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
                elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and msg['reply_to_message']['caption'] == "Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo vc será expulso".format(str(captchatimespan/60)):
                    SolveCaptcha(msg, chat_id)
                elif 'text' in msg and not msg['text'].startswith("@") and ((random.randint(1, 100)<=intrometerpercentage and len(msg['text'].split())>=intrometerminimumwords) or ('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') or "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text']) and funfunctions == True:
                    if not OnSay(msg, chat_id):
                        InteligenciaArtificial(msg, chat_id)
                elif 'text' in msg and len(msg['text'].split()) >= intrometerminimumwords and funfunctions == True:
                    if not OnSay(msg, chat_id):
                        IdentificaMusica(msg, chat_id)
                elif 'text' in msg:
                    CheckEventos(msg, chat_id)
                    SolveCaptcha(msg, chat_id)
                    CheckCaptcha(msg, chat_id)
                    OnSay(msg, chat_id)
                #BEGGINNING OF COOLDOWN UPDATES
                if 'text' in msg:
                    if float(lastmessagetime)+60 < ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                        sentcooldownmessage = False
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
    global threads
    messagehandle = threading.Thread(target=thread_function, args=(msg,))
    threads.append(messagehandle)
    messagehandle.start()

def handle_query(msg):
    cookiebot.sendChatAction(msg['message']['reply_to_message']['chat']['id'], 'typing')
    cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    cookiebot.answerCallbackQuery(query_id, text='Agora marque a mensagem com o novo valor')
    if query_data == 'a':
       cookiebot.sendMessage(msg['message']['reply_to_message']['chat']['id'], 'Use 1 para não interferir com outros furbots caso eles estejam no grupo, ou 0 se eu for o único.\nResponda ESTA mensagem com o novo valor da variável', reply_to_message_id=msg['message']['reply_to_message']['message_id'])
    elif query_data == 'b':
        cookiebot.sendMessage(msg['message']['reply_to_message']['chat']['id'], 'Este é o limite máximo de stickers permitidos em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo.\nResponda ESTA mensagem com o novo valor da variável', reply_to_message_id=msg['message']['reply_to_message']['message_id'])
    elif query_data == 'c':
        cookiebot.sendMessage(msg['message']['reply_to_message']['chat']['id'], 'Este é o tempo pelo qual novos usuários no grupo não poderão mandar imagens (o bot apaga automaticamente).\nResponda ESTA mensagem com o novo valor da variável', reply_to_message_id=msg['message']['reply_to_message']['message_id'])
    elif query_data == 'd':
        cookiebot.sendMessage(msg['message']['reply_to_message']['chat']['id'], 'Este é o tempo que novos usuários dispõem para resolver o Captcha. USE 0 PARA DESLIGAR O CAPTCHA!\nResponda ESTA mensagem com o novo valor da variável', reply_to_message_id=msg['message']['reply_to_message']['message_id'])
    elif query_data == 'e':
        cookiebot.sendMessage(msg['message']['reply_to_message']['chat']['id'], 'Esta é a porcentagem de chance em porcentagem de eu responder a uma mensagem aleatoriamente, se ela for grande o suficiente.\nResponda ESTA mensagem com o novo valor da variável', reply_to_message_id=msg['message']['reply_to_message']['message_id'])
    elif query_data == 'f':
        cookiebot.sendMessage(msg['message']['reply_to_message']['chat']['id'], 'Este é o mínimo de termos necessários em uma mensagem para eu responder de forma aleatória.\nResponda ESTA mensagem com o novo valor da variável', reply_to_message_id=msg['message']['reply_to_message']['message_id'])
    elif query_data == 'g':
        cookiebot.sendMessage(msg['message']['reply_to_message']['chat']['id'], 'Esta é a área máxima, em píxeis quadrados, que eu vou levar em consideração ao ampliar imagens de baixa resolução.\nResponda ESTA mensagem com o novo valor da variável', reply_to_message_id=msg['message']['reply_to_message']['message_id'])
    elif query_data == 'h':
        cookiebot.sendMessage(msg['message']['reply_to_message']['chat']['id'], "Use 1 para permitir comandos e funcionalidades de diversão, ou 0 para apenas as funções de controle/gerenciamento.\nResponda ESTA mensagem com o novo valor da variável", reply_to_message_id=msg['message']['reply_to_message']['message_id'])

MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()