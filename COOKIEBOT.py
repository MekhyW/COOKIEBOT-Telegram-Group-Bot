import os
import subprocess
import sys
import random
import json
import requests
import datetime
import googletrans
translator = googletrans.Translator()
from google_images_download import google_images_download
google_images_response = google_images_download.googleimagesdownload()
import spotipy
spotipyCLIENT_ID = ''
spotipyCLIENT_SECRET = ''
spotify = spotipy.Spotify(spotipy.oauth2.SpotifyClientCredentials(client_id=spotipyCLIENT_ID, client_secret=spotipyCLIENT_SECRET).get_access_token())
import speech_recognition
recognizer = speech_recognition.Recognizer()
import geopy
import wolframalpha
WolframAPP_ID = ''
WolframCLIENT = wolframalpha.Client(WolframAPP_ID)
DeepaiTOKEN = ''
import telepot
from telepot.loop import MessageLoop
cookiebotTOKEN = ''
cookiebot = telepot.Bot(cookiebotTOKEN)
import logging
import threading
threads = list()
import time
firstpass = True
start_time = time.time()
lastmessagedate = "1-1-1"
lastmessagetime = "0"
sentcooldownmessage = False
stickerspamlimit = 5
intrometerpercentage = 1
intrometerminimumwords = 6
lowresolutionarea = 76800

#STRING IN FILE CHECKER
def check_if_string_in_file(file_name, string_to_search):
    for line in file_name:
        if string_to_search in line:
            return True
    return False


def thread_function(msg):
    try:
        global firstpass
        if time.time() - start_time > 3:
            firstpass = False
        if firstpass == False:
            content_type, chat_type, chat_id = telepot.glance(msg)
            print(content_type, chat_type, chat_id, msg['message_id'])
            if chat_type == 'private':
                if msg['text'] == "/stop" and msg['from']['username'] == 'MekhyW':
                    os._exit(0)
                cookiebot.sendMessage(chat_id, "Olá, sou o Cookiebot!\n\nSou um bot com AI de conversa, de assistência, conteúdo infinito e conteúdo customizado.\nSe quiser me adicionar no seu chat ou obter a lista de comandos comentada, mande uma mensagem para o @MekhyW\n\nSe está procurando um bot com proteção para grupos e administração, use o @burrsobot\n\nSe está procurando o bot de controle da minha fursuit, use o @mekhybot")
            elif "MekhyW" not in str(cookiebot.getChatAdministrators(chat_id)):
                cookiebot.sendMessage(chat_id, "Posso apenas ficar no grupo se o @MekhyW estiver nele, e for um admin!\n\nIsso é feito para evitar spam e raids, me desculpem")
                cookiebot.leaveChat(chat_id)
            elif "CookieMWbot" in str(cookiebot.getChatAdministrators(chat_id)):
                #BEGGINING OF NEW NAME GATHERING
                if not os.path.isfile(str(chat_id)+".txt"):
                    open(str(chat_id)+".txt", 'a').close() 
                text_file = open(str(chat_id)+".txt", "r+")
                if (check_if_string_in_file(text_file, msg['from']['username']) == False):
                    text_file.write("\n"+msg['from']['username'])
                text_file.close()
                #END OF NEW NAME GATHERING
                #BEGINNING OF CALENDAR SYNC AND BURRBOT CHECK
                text_file = open("Burrbot chats.txt", "r")
                if check_if_string_in_file(text_file, str(chat_id)):
                    Burrbot = True
                else:
                    Burrbot = False
                text_file.close()
                text_file = open(str(chat_id)+".txt", "r")
                lines = text_file.read().split("\n")
                text_file.close()
                text_file = open(str(chat_id)+".txt", "w")
                for line in lines:
                    if line == '':
                        pass
                    elif line.startswith("EVENT"):
                        eventarr = line.split(" ")
                        day, month, year = line.split(" ")[len(eventarr)-2].split("/")
                        if datetime.date.today() < datetime.date(int(year), int(month), int(day)):
                            text_file.write(line+"\n")
                        elif datetime.date.today() == datetime.date(int(year), int(month), int(day)):
                            hojeID = cookiebot.sendMessage(chat_id, "FALTA POUCO!\n--> "+line.replace("EVENT ", '')+' 🎉')['message_id']
                            cookiebot.pinChatMessage(chat_id, hojeID, True)
                            for file in os.listdir():
                                if file.startswith("-"):
                                    chatid = file.split(".txt")[0]
                                    if chatid.split("-")[1].isdigit():
                                        cookiebot.forwardMessage(chatid, chat_id, hojeID)
                    elif line.startswith(msg['from']['username']):
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
                #END OF CALENDAR SYNC AND BURRBOT CHECK
                if content_type == "new_chat_member":
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, "Seja bem vindo(a)!", reply_to_message_id=msg['message_id'])
                elif content_type == "left_chat_member":
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, "Perdemos um soldado\n\nF 😔", reply_to_message_id=msg['message_id'])
                    photo = open('Brasil_flag.gif', 'rb')
                    cookiebot.sendPhoto(chat_id, photo)
                elif content_type == "voice":
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
                elif content_type == "audio":
                    pass
                elif content_type == "photo":
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
                elif content_type == "document":
                    pass
                elif content_type == "sticker":
                    text_file = open("Stickers.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    text_file.close()
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
                elif content_type == "location":
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
                elif 'text' in msg and msg['text'].startswith("/") and (Burrbot==False or msg['text'] not in open("Burrbot functions.txt", "r+").read()) and str(datetime.date.today()) == lastmessagedate and float(lastmessagetime)+60 >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                    if sentcooldownmessage == False:
                        cookiebot.sendMessage(chat_id, "Você está em Cooldown!\nApenas use um comando '/' por minuto\nIsso é feito como medida de anti-spam :c\n(OBS: o cooldown foi resetado agora)", reply_to_message_id=msg['message_id'])
                        sentcooldownmessage = True
                    elif sentcooldownmessage == True:
                        cookiebot.deleteMessage(telepot.message_identifier(msg))
                elif 'text' in msg and msg['text'].startswith("/escolha"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    if len(msg['text'].split()) == 1:
                        cookiebot.sendMessage(chat_id, "Envie os termos pra escolher\nEXEMPLO: '/escolher A, B, C'", reply_to_message_id=msg['message_id'])
                    else:
                        terms = msg['text'].split(",")
                        cookiebot.sendMessage(chat_id, terms[random.randint(1, len(terms)-1)].capitalize(), reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/idade"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    if not " " in msg['text']:
                        cookiebot.sendMessage(chat_id, "Digite um nome, vou dizer a sua idade!\n\nEx: '/idade Mekhy'\n(obs: só o primeiro nome conta)", reply_to_message_id=msg['message_id'])
                    else:
                        Nome = msg['text'].replace("/idade ", '').split()[0]
                        response = json.loads(requests.get("https://api.agify.io?name={}".format(Nome)).text)
                        Idade = response['age']
                        Contagem = response['count']
                        cookiebot.sendMessage(chat_id, "Sua idade é {} anos! 👴\nRegistrado {} vezes".format(Idade, Contagem), reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/genero"):
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
                elif 'text' in msg and msg['text'].startswith("/completar"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    if 'reply_to_message' in msg and 'text' in msg['reply_to_message']:
                        target = msg['reply_to_message']['text']
                    else:
                        target = msg['text'].replace("/completar ", '')
                    r = requests.post("https://api.deepai.org/api/text-generator",data={'text': translator.translate(target, dest='en').pronunciation,},headers={'api-key': DeepaiTOKEN})
                    Answer = translator.translate(r.json()['output'], dest='pt').text
                    cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/startup"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    r = requests.get("http://itsthisforthat.com/api.php?text")
                    startup = translator.translate(r.text, dest='pt').text
                    cookiebot.sendMessage(chat_id, "{} Criou uma startup!\nO slogan é:\n'{}'".format(msg['from']['username'], startup))
                elif 'text' in msg and msg['text'].startswith("/addhoje"):
                    if 'reply_to_message' in msg:
                        cookiebot.sendChatAction(chat_id, 'typing')
                        text_file = open("Hoje.txt", "a+", encoding='utf8')
                        text_file.write("\n"+msg['reply_to_message']['text'].replace("\n", "\\n"))
                        text_file.close()
                        cookiebot.sendMessage(chat_id, "Coisa idiota pra fazer adicionada! ✅", reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/addcheiro"):
                    if 'reply_to_message' in msg:
                        cookiebot.sendChatAction(chat_id, 'typing')
                        text_file = open("Cheiro.txt", "a+", encoding='utf8')
                        text_file.write("\n"+msg['reply_to_message']['text'].replace("\n", "\\n"))
                        text_file.close()
                        cookiebot.sendMessage(chat_id, "Cheirin exótico adicionado! ✅", reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/adddadjoke"):
                    if 'reply_to_message' in msg:
                        cookiebot.sendChatAction(chat_id, 'typing')
                        text_file = open("DadJokes.txt", "a+", encoding='utf8')
                        text_file.write("\n"+msg['reply_to_message']['text'].replace("\n", "\\n"))
                        text_file.close()
                        cookiebot.sendMessage(chat_id, "Piada bosta de boomer adicionada! ✅", reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/addsabedoria"):
                    if 'reply_to_message' in msg:
                        cookiebot.sendChatAction(chat_id, 'typing')
                        text_file = open("Sabedoria.txt", "a+", encoding='utf8')
                        text_file.write("\n"+msg['reply_to_message']['text'].replace("\n", "\\n"))
                        text_file.close()
                        cookiebot.sendMessage(chat_id, "Frase toppen adicionada! ✅", reply_to_message_id=msg['message_id'])
                elif Burrbot == False and 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida com o /regras" and msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
                    text_file = open("Regras_" + str(chat_id)+".txt", 'w', encoding='utf-8')
                    text_file.write(msg['text'])
                    cookiebot.sendMessage(chat_id, "Mensagem de regras atualizada! ✅", reply_to_message_id=msg['message_id'])
                elif Burrbot == False and 'text' in msg and msg['text'].startswith("/novasregras"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida com o /regras", reply_to_message_id=msg['message_id'])
                elif Burrbot == False and 'text' in msg and msg['text'].startswith("/regras"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    if os.path.exists("Regras_" + str(chat_id)+".txt"):
                        with open("Regras_" + str(chat_id)+".txt", encoding='utf-8') as file:
                            regras = file.read()
                        cookiebot.sendMessage(chat_id, regras, reply_to_message_id=msg['message_id'])
                    else:    
                        cookiebot.sendMessage(chat_id, "Ainda não há regras colocadas para esse grupo\nPara tal, use o /novasregras", reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/removeevento"):
                    if msg['text'] == "/removeevento" or msg['text'] == "/removeevento@CookieMWbot":
                        cookiebot.sendChatAction(chat_id, 'typing')
                        cookiebot.sendMessage(chat_id, "Se vc é um admin, Mande o nome do evento pra remover\nExemplo: /removeevento Invasão da área 51", reply_to_message_id=msg['message_id'])
                    elif msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
                        cookiebot.sendChatAction(chat_id, 'typing')
                        text_file = open(str(chat_id)+".txt", "r")
                        lines = text_file.read().split("\n")
                        text_file.close()
                        text_file = open(str(chat_id)+".txt", "w")
                        found = False
                        for line in lines:
                            query = msg['text'].replace("/removeevento", '')
                            if line.startswith("EVENT") and (query in line or query.capitalize() in line):
                                cookiebot.sendMessage(chat_id, "Evento "+line.replace("EVENT", '')+" Removido!", reply_to_message_id=msg['message_id'])
                                found = True
                                break
                            else:
                                text_file.write(line+"\n")
                        if found == False:
                            cookiebot.sendMessage(chat_id, "Não foi possível encontrar o evento "+line.replace("EVENT", ''), reply_to_message_id=msg['message_id'])
                    text_file.close()
                elif 'text' in msg and msg['text'].startswith("/addevento"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, "Se vc é um admin, Responda ESTA mensagem com um evento e data\n\nExemplo: 'Comissões do Ark 31/02/2077 06:21\n(horário de Brasília pls)'", reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/eventos"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    text_file = open(str(chat_id)+".txt", "r+")
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
                        if line.startswith("EVENT"):
                            events.append(line)
                            eventarr = line.split(" ")
                            day, month, year = line.split(" ")[len(eventarr)-2].split("/")
                            dates.append([year, month, day])
                    text_file.close()
                    bubbleSort(dates, events)
                    answer = "📅 PROXIMOS EVENTOS REGISTRADOS: 📅\n\n"
                    x = 1
                    for event in events:
                        answer += (str(x) + ") " + event.replace("EVENT ", '') + "\n")
                        x += 1
                    cookiebot.sendMessage(chat_id, answer, reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/nada"):
                    pass
                elif 'text' in msg and msg['text'].startswith("/naoclique"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    number = random.randint(1, 3)
                    if number == 1:
                        cookiebot.sendMessage(chat_id, "VOCÊ SÓ TINHA UMA MISSÃO CARA", reply_to_message_id=msg['message_id'])
                    elif number == 2:
                        cookiebot.sendMessage(chat_id, "VOCÊ É A VERGONHA DA FAMILIA", reply_to_message_id=msg['message_id'])
                    elif number == 3:
                        cookiebot.sendMessage(chat_id, "VOCÊ FALHOU MISERAVELMENTE", reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/tavivo"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, "Estou vivo (não recomendo)\n\nPing enviado em:\n" + str(datetime.datetime.now()))
                elif 'text' in msg and msg['text'].startswith("/everyone"):
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
                elif 'text' in msg and msg['text'].startswith("/comandos"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    text_file = open("Cookiebot functions.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    string = ""
                    for line in lines:
                        string += str(line)
                    cookiebot.sendMessage(chat_id, string, reply_to_message_id=msg['message_id'])
                elif Burrbot == False and 'text' in msg and (msg['text'].startswith("/hoje") or msg['text'].startswith("/today")):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    text_file = open("Hoje.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
                    cookiebot.sendMessage(chat_id, "Hoje pra você é dia de "+target, reply_to_message_id=msg['message_id'])
                    text_file.close()
                elif Burrbot == False and 'text' in msg and (msg['text'].startswith("/cheiro") or msg['text'].startswith("/smell")):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    text_file = open("Cheiro.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
                    cookiebot.sendMessage(chat_id, "*sniff* *sniff*\nHmmmmmm\n\nVocê está com um cheirin de "+target, reply_to_message_id=msg['message_id'])
                    text_file.close()
                elif Burrbot == False and 'text' in msg and ('eu faço' in msg['text'] or 'eu faco' in msg['text']) and '?' in msg['text']:
                    cookiebot.sendChatAction(chat_id, 'typing')
                    text_file = open("Hoje.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
                    cookiebot.sendMessage(chat_id, "Vai "+target, reply_to_message_id=msg['message_id'])
                    text_file.close()
                elif 'text' in msg and msg['text'].startswith("/portugues"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    if 'reply_to_message' not in msg:
                        cookiebot.sendMessage(chat_id, "Responda uma mensagem, vou traduzir ela para o português \n(FUNCIONA COM QUALQUER LINGUA)", reply_to_message_id=msg['message_id'])
                    else:
                        translation = translator.translate(msg['reply_to_message']['text'], dest='pt').text
                        cookiebot.sendMessage(chat_id, "Tradução para pt/br:\n\n'{}'".format(translation), reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/ingles"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    if 'reply_to_message' not in msg:
                        cookiebot.sendMessage(chat_id, "Responda uma mensagem, vou traduzir ela para o inglês \n(FUNCIONA COM QUALQUER LINGUA)", reply_to_message_id=msg['message_id'])
                    else:
                        translation = translator.translate(msg['reply_to_message']['text'], dest='en').text
                        cookiebot.sendMessage(chat_id, "Tradução para inglês:\n\n'{}'".format(translation), reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/fodase"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    if 'reply_to_message' not in msg:
                        cookiebot.sendMessage(chat_id, "Responda alguém com esse comando, vou xingar ela", reply_to_message_id=msg['message_id'])
                    else:
                        operations = json.loads(requests.get('https://www.foaas.com/operations').text)
                        urlcomplement = operations[random.randint(0, len(operations)-1)]['url'].replace(':from', '@'+msg['from']['username']).replace(':name', '@'+msg['reply_to_message']['from']['username'])
                        url = 'https://www.foaas.com{}'.format(urlcomplement)
                        response = requests.get(url).text
                        desired_text = response.split("<!DOCTYPE html> <html> <head> <title>FOAAS - ")[1].split("</title>")[0]
                        desired_text_ptbr = translator.translate(desired_text, dest='pt').text
                        cookiebot.sendMessage(chat_id, desired_text_ptbr, reply_to_message_id=msg['reply_to_message']['message_id'])
                elif 'text' in msg and msg['text'].startswith("/insulto"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    insult = json.loads(requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json').text)['insult']
                    insulto = translator.translate(insult, dest='pt').text
                    cookiebot.sendMessage(chat_id, insulto, reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/numero"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    if len(msg['text'].split()) == 1:
                        cookiebot.sendMessage(chat_id, "Mande um número, vou dizer fatos sobre ele!\nExemplo: /numero 42", reply_to_message_id=msg['message_id'])
                    else:
                        number = msg['text'].replace("/numero ", '')
                        historical_fact = translator.translate(requests.get('http://numbersapi.com/{}'.format(number)).text, dest='pt').text
                        mathematical_fact = translator.translate(requests.get('http://numbersapi.com/{}/math'.format(number)).text, dest='pt').text
                        final_text = historical_fact+"\n\nAlém disso, "+mathematical_fact
                        cookiebot.sendMessage(chat_id, final_text, reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/dadjoke"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    text_file = open("DadJokes.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
                    cookiebot.sendMessage(chat_id, target, reply_to_message_id=msg['message_id'])
                    text_file.close()
                elif 'text' in msg and msg['text'].startswith("/biblia"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    text_file = open("Biblia.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
                    cookiebot.sendMessage(chat_id, target, reply_to_message_id=msg['message_id'])
                    text_file.close()
                elif 'text' in msg and msg['text'].startswith("/sabedoria"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    text_file = open("Sabedoria.txt", "r+", encoding='utf8')
                    lines = text_file.readlines()
                    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
                    cookiebot.sendMessage(chat_id, target, reply_to_message_id=msg['message_id'])
                    text_file.close()
                elif 'text' in msg and msg['text'].startswith("/ideiadesenho"):
                    cookiebot.sendChatAction(chat_id, 'upload_photo')
                    ideiasdesenho = os.listdir('IdeiaDesenho')
                    ideiaID = random.randint(0, len(ideiasdesenho)-1)
                    photo = open('IdeiaDesenho'+'/'+ideiasdesenho[ideiaID], 'rb')
                    cookiebot.sendPhoto(chat_id, photo, caption="Referência com ID {}\n\nNão trace sem dar créditos! (use a busca reversa do google images)".format(ideiaID), reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/portal"):
                    cookiebot.sendChatAction(chat_id, 'upload_photo')
                    portal = os.listdir('portal')
                    portalID = random.randint(0, len(portal)-1)
                    photo = open('portal'+'/'+portal[portalID], 'rb')
                    cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/contato"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, '\nAre you a business or sponsor?\n💌 Email: felipe_catapano@yahoo.com.br')
                    cookiebot.sendMessage(chat_id, 'Want to message me? Or Report a problem?\n🔵 Telegram: @MekhyW\n')
                    cookiebot.sendMessage(chat_id, '\nGet in touch with what I´m doing\n🐦 Twitter: https://twitter.com/MekhyW\n')
                    cookiebot.sendMessage(chat_id, '\nWant a match with a like?\n⚪ Howlr: Mekhy W.!\n')
                    cookiebot.sendMessage(chat_id, '\nDo you use LinkedIn?\n🟦 LinkedIn: https://www.linkedin.com/in/felipe-catapano/\n')
                    cookiebot.sendMessage(chat_id, '\nCheck out my other projects!\n⚛️ GitHub: https://github.com/MekhyW\n')
                elif 'text' in msg and msg['text'].startswith("/qualquercoisa"):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, "Troque o 'qualquercoisa' por algo, vou mandar uma foto desse algo\n\nEXEMPLO: /fennec\n(acentos, letras maiusculas e espaços não funcionam)", reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/") and " " not in msg['text'] and os.path.exists(msg['text'].replace('/', '').replace("@CookieMWbot", '')):
                    cookiebot.sendChatAction(chat_id, 'upload_photo')
                    images = os.listdir(msg['text'].replace('/', '').replace("@CookieMWbot", ''))
                    imageID = random.randint(0, len(images)-1)
                    photo = open(msg['text'].replace('/', '').replace("@CookieMWbot", '')+'/'+images[imageID], 'rb')
                    cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])
                elif 'text' in msg and msg['text'].startswith("/") and " " not in msg['text'] and (Burrbot==False or msg['text'] not in open("Burrbot functions.txt", "r+").read()):
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
                elif 'text' in msg and (msg['text'].startswith("Cookiebot") or msg['text'].startswith("cookiebot") or 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') and ("quem" in msg['text'] or "Quem" in msg['text']) and ("?" in msg['text']):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
                    text_file = open(str(chat_id)+".txt", "r+")
                    lines = text_file.readlines()
                    target = None
                    while len(lines)>1 and (target in (None, '') or target.startswith("EVENT")):
                        target = lines[random.randint(0, len(lines)-1)].replace("\n", '')
                        target = target.split()[0]
                    cookiebot.sendMessage(chat_id, LocucaoAdverbial+"@"+target, reply_to_message_id=msg['message_id'])
                    text_file.close()
                elif 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, Responda ESTA mensagem com um evento e data\n\nExemplo: 'Comissões do Ark 31/02/2077 06:21\n(horário de Brasília pls)'" and msg['from']['username'] in str(cookiebot.getChatAdministrators(chat_id)):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    Event = msg['text'].split(" ")
                    if len(Event) >= 3:
                        Date = Event[len(Event)-2].split("/")
                        Time = Event[len(Event)-1].split(":")
                        if len(Date) == 3 and len(Time) == 2 and Date[0].isnumeric() and Date[1].isnumeric() and Date[2].isnumeric() and Time[0].isnumeric() and Time[1].isnumeric():
                            text_file = open(str(chat_id)+".txt", "a")
                            text_file.write("\n"+"EVENT "+msg['text'])
                            text_file.close()
                            cookiebot.sendMessage(chat_id, "Evento Adicionado! ✅\nUse /eventos para checar", reply_to_message_id=msg['message_id'])
                        else:
                            cookiebot.sendMessage(chat_id, "Formato inválido", reply_to_message_id=msg['message_id'])
                    else:
                        cookiebot.sendMessage(chat_id, "Faltam informações", reply_to_message_id=msg['message_id'])
                elif 'text' in msg and ((random.randint(1, 100)<=intrometerpercentage and len(msg['text'].split())>=intrometerminimumwords) or ('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') or "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text']):
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
                            print("SENT WOLFRAM MESSAGE")
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
                        print("SENT SIMSIMI MESSAGE")
                elif 'text' in msg and len(msg['text'].split()) >= intrometerminimumwords:
                    spotify = spotipy.Spotify(spotipy.oauth2.SpotifyClientCredentials(client_id=spotipyCLIENT_ID, client_secret=spotipyCLIENT_SECRET).get_access_token())
                    results = spotify.search(q=msg['text'], type="track", limit=1, offset=0)
                    if results['tracks']['total']:
                        names = ''
                        for artist in results['tracks']['items'][0]['album']['artists']:
                            names += ", {}".format(artist['name'])
                        names = names[2:]
                        cookiebot.sendAudio(chat_id, results['tracks']['items'][0]['preview_url'], caption=results['tracks']['items'][0]['name'], title=results['tracks']['items'][0]['name'], performer=names, reply_to_message_id=msg['message_id'])
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
    except:
        pass

#MESSAGE HANDLER
def handle(msg):
    global threads
    messagehandle = threading.Thread(target=thread_function, args=(msg,))
    threads.append(messagehandle)
    messagehandle.start()

MessageLoop(cookiebot, handle).run_forever()