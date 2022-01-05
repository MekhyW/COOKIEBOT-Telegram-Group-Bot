WolframAPP_ID = ''
googleAPIkey = ''
searchEngineCX = ''
cookiebotTOKEN = ''
#bombotTOKEN = ''
from Configurations import *
from GroupShield import *
from Publisher import *
import math, os, subprocess, random, json, requests, datetime, time, threading, traceback, gc
import googletrans
import google_images_search, io, PIL
import speech_recognition, ShazamAPI, wolframalpha, unidecode
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, Message
from telepot.delegate import (per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
translator = googletrans.Translator()
googleimagesearcher = google_images_search.GoogleImagesSearch(googleAPIkey, searchEngineCX, validate_images=False)
recognizer = speech_recognition.Recognizer()
WolframCLIENT = wolframalpha.Client(WolframAPP_ID)
cookiebot = telepot.Bot(cookiebotTOKEN)
mekhyID = 780875868
unnatended_threads = list()
lastmessagedate, lastmessagetime = "1-1-1", "0"
sentcooldownmessage = False

#IGNORE UPDATES PRIOR TO BOT ACTIVATION
updates = cookiebot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    cookiebot.getUpdates(offset=last_update_id+1)

def wait_open(filename):
    if os.path.exists(filename):
        while True:
            try:
                text = open(filename, 'r')
                text.close()
                break
            except IOError:
                pass


def check_if_string_in_file(file_name, string_to_search):
    for line in file_name:
        if string_to_search in line:
            return True
    return False

def DeleteMessage(identifier):
    try:
        cookiebot.deleteMessage(identifier)
    except Exception as e:
        print(e)


def Sticker_anti_spam(msg, chat_id, stickerspamlimit):
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
        DeleteMessage(telepot.message_identifier(msg))

def Identify_music(msg, chat_id, AUDIO_FILE):
    shazam = ShazamAPI.Shazam(open(AUDIO_FILE, 'rb').read())
    recognize_generator = shazam.recognizeSong()
    response = next(recognize_generator)
    if('track' in response[1]):
        cookiebot.sendMessage(chat_id, "MÚSICA: 🎵 " + response[1]['track']['title'] + " - " + response[1]['track']['subtitle'] + " 🎵", reply_to_message_id=msg['message_id'])

def Speech_to_text(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    r = requests.get("https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, cookiebot.getFile(msg['voice']['file_id'])['file_path']), allow_redirects=True)
    open('VOICEMESSAGE.oga', 'wb').write(r.content)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', 'VOICEMESSAGE.oga', "VOICEMESSAGE.wav", '-y'])
    AUDIO_FILE = "VOICEMESSAGE.wav"
    try:
        with speech_recognition.AudioFile(AUDIO_FILE) as source:
            audio = recognizer.record(source)
        voicetext_ptbr = recognizer.recognize_google(audio, language="pt-BR", show_all=True)['alternative'][0]
        #voicetext_enus = recognizer.recognize_google(audio, language="en-US", show_all=True)['alternative'][0]
        Text = voicetext_ptbr['transcript'].capitalize()
        cookiebot.sendMessage(chat_id, "Texto: \n"+'"'+Text+'"', reply_to_message_id=msg['message_id'])
    except Exception as e:
        print(e)
    Identify_music(msg, chat_id, AUDIO_FILE)

def CooldownAction(msg, chat_id):
    global sentcooldownmessage
    if sentcooldownmessage == False:
        cookiebot.sendMessage(chat_id, "Você está em Cooldown!\nApenas use um comando '/' por minuto\nIsso é feito como medida de anti-spam :c\n(OBS: o cooldown foi resetado agora)", reply_to_message_id=msg['message_id'])
        sentcooldownmessage = True
    elif sentcooldownmessage == True:
        DeleteMessage(telepot.message_identifier(msg))

def Dado(msg, chat_id):
    if msg['text'].startswith("/dado"):
        cookiebot.sendMessage(chat_id, "Rodo um dado de 1 até x, n vezes\nEXEMPLO: /d20 5\n(Roda um d20 5 vezes)")
    else:
        if len(msg['text'].split()) == 1:
            vezes = 1
        else:
            vezes = int(msg['text'].replace("@CookieMWbot", '').split()[1])
            vezes = max(min(20, vezes), 1)
        limite = int(msg['text'].replace("@CookieMWbot", '').split()[0][2:])
        resposta = "(d{}) ".format(limite)
        if vezes == 1:
            resposta += "🎲 -> {}".format(random.randint(1, limite))
        else:
            for vez in range(vezes):
                resposta += "\n{}º Lançamento: 🎲 -> {}".format(vez+1, random.randint(1, limite))
        cookiebot.sendMessage(chat_id, resposta, reply_to_message_id=msg['message_id'])

def Idade(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if not " " in msg['text']:
        cookiebot.sendMessage(chat_id, "Digite um nome, vou dizer a sua idade!\n\nEx: '/idade Mekhy'\n(obs: só o primeiro nome conta)", reply_to_message_id=msg['message_id'])
    else:
        Nome = msg['text'].replace("/idade ", '').split()[0]
        response = json.loads(requests.get("https://api.agify.io?name={}".format(Nome)).text)
        Idade = response['age']
        Contagem = response['count']
        if Contagem == 0:
            cookiebot.sendMessage(chat_id, "Não conheço esse nome!", reply_to_message_id=msg['message_id'])
        else:
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
        if Contagem == 0:
            cookiebot.sendMessage(chat_id, "Não conheço esse nome!", reply_to_message_id=msg['message_id'])
        elif Genero == 'male':
            cookiebot.sendMessage(chat_id, "É um menino! 👨\n\nProbabilidade --> {}%\nRegistrado {} vezes".format(Probabilidade*100, Contagem), reply_to_message_id=msg['message_id'])
        elif Genero == 'female':
            cookiebot.sendMessage(chat_id, "É uma menina! 👩\n\nProbabilidade --> {}%\nRegistrado {} vezes".format(Probabilidade*100, Contagem), reply_to_message_id=msg['message_id'])


def AtualizaBemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Welcome/Welcome_" + str(chat_id)+".txt")
    text_file = open("Welcome/Welcome_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Mensagem de Boas Vindas atualizada! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    DeleteMessage(telepot.message_identifier(msg['reply_to_message']))

def NovoBemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Se vc é um admin, DÊ REPLY NESTA MENSAGEM com a mensagem que será exibida quando alguém entrar no grupo", reply_to_message_id=msg['message_id'])

def AtualizaRegras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Rules/Regras_" + str(chat_id)+".txt")
    text_file = open("Rules/Regras_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Mensagem de regras atualizada! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    DeleteMessage(telepot.message_identifier(msg['reply_to_message']))

def NovasRegras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Se vc é um admin, DÊ REPLY NESTA MENSAGEM com a mensagem que será exibida com o /regras", reply_to_message_id=msg['message_id'])

def Regras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Rules/Regras_" + str(chat_id)+".txt")
    if os.path.exists("Rules/Regras_" + str(chat_id)+".txt"):
        with open("Rules/Regras_" + str(chat_id)+".txt", encoding='utf-8') as file:
            regras = file.read()
        cookiebot.sendMessage(chat_id, regras+"\n\nDúvidas em relação ao bot? Mande para @MekhyW", reply_to_message_id=msg['message_id'])
    else:    
        cookiebot.sendMessage(chat_id, "Ainda não há regras colocadas para esse grupo\nPara tal, use o /novasregras", reply_to_message_id=msg['message_id'])

def TaVivo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Estou vivo\n\nPing enviado em:\n" + str(datetime.datetime.now()))

def Everyone(msg, chat_id, listaadmins):
    cookiebot.sendChatAction(chat_id, 'typing')
    if str(msg['from']['username']) not in listaadmins:
        cookiebot.sendMessage(chat_id, "Você não tem permissão para chamar todos os membros do grupo.", reply_to_message_id=msg['message_id'])
    else:
        wait_open("Registers/"+str(chat_id)+".txt")
        text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf8')
        lines = text_file.readlines()
        result = ""
        for line in lines:
            username = line.split()[0]
            result += ("@"+username+" ")
        text_file.close()
        cookiebot.sendMessage(chat_id, result, reply_to_message_id=msg['message_id'])

def Adm(msg, chat_id, listaadmins):
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
        if len(line.split()) != 3:
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
    photo.close()

def Contato(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, '💌 Email: felipe_catapano@yahoo.com.br\n🔵 Telegram: @MekhyW\n🟦 LinkedIn: https://www.linkedin.com/in/felipe-catapano/\n⚛️ GitHub: https://github.com/MekhyW')

def PromptQualquerCoisa(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Troque o 'qualquercoisa' por algo, vou mandar uma foto desse algo\n\nEXEMPLO: /fennec\n(acentos, letras maiusculas e espaços não funcionam)", reply_to_message_id=msg['message_id'])

def CustomCommand(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    images = os.listdir("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", ''))
    imageID = random.randint(0, len(images)-1)
    photo = open("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')+'/'+images[imageID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])
    photo.close()

def QualquerCoisa(msg, chat_id, sfw):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    searchterm = msg['text'].split("@")[0].replace("/", '').replace("@CookieMWbot", '')
    if sfw == 0:
        googleimagesearcher.search({'q': searchterm, 'num': 10, 'safe':'off', 'filetype':'jpg|png'})
    else:
        googleimagesearcher.search({'q': searchterm, 'num': 10, 'safe':'medium', 'filetype':'jpg|png'})
    images = googleimagesearcher.results()
    random.shuffle(images)
    my_bytes_io = io.BytesIO()
    for image in images:
        my_bytes_io.seek(0)
        my_bytes_io.truncate(0)
        image.copy_to(my_bytes_io)
        my_bytes_io.seek(0)
        try:
            temp_img = PIL.Image.open(my_bytes_io)
            temp_img.save(my_bytes_io, format="png")
            my_bytes_io.seek(0)
            cookiebot.sendPhoto(chat_id, ('x.png', my_bytes_io), reply_to_message_id=msg['message_id'])
            my_bytes_io.close()
            temp_img.close()
            return 1
        except:
            try:
                my_bytes_io.seek(0)
                my_bytes_io.truncate(0)
                temp_img = PIL.Image.open(my_bytes_io)
                temp_img.save(my_bytes_io, format="jpg")
                my_bytes_io.seek(0)
                cookiebot.sendPhoto(chat_id, ('x.jpg', my_bytes_io), reply_to_message_id=msg['message_id'])
                my_bytes_io.close()
                temp_img.close()
                return 1
            except Exception as e:
                print(e)
    cookiebot.sendMessage(chat_id, "Não consegui achar uma imagem (ou era NSFW e eu filtrei)", reply_to_message_id=msg['message_id'])
    my_bytes_io.close()
    temp_img.close()

def Quem(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
    wait_open("Registers/"+str(chat_id)+".txt")
    text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf-8')
    lines = text_file.readlines()
    target = None
    while len(lines)>1 and target in (None, ''):
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
    message = ""
    Answer = ""
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
        r = requests.get('https://api.simsimi.net/v2/?text={}&lc=pt&cf=true'.format(message))
        try:
            Answer = json.loads(r.text)['messages'][0]['response'].capitalize()
        except:
            print(r.text)
            if len(str(r.text).split("{")) > 1:
                Answer = str(r.text).split("{")[1]
                Answer = "{" + Answer
                Answer = json.loads(Answer)['messages'][0]['response'].capitalize()
        Answer = translator.translate(Answer, dest='pt').text
        cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])


def AddtoRandomDatabase(msg, chat_id):
    wait_open("Random_Database.txt")
    text = open("Random_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Random_Database.txt", 'w', encoding='utf-8')
    if len(lines) > 1000:
        i = len(lines) - 1000
    else:
        i = 0
    while i < len(lines):
        if not lines[i] == "\n":
            text.write(lines[i])
        i += 1
    i = 0
    text.write(str(chat_id) + " " + str(msg['message_id']) + "\n")
    text.close()

def ReplyAleatorio(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    wait_open("Random_Database.txt")
    text = open("Random_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    while True:
        try:
            target = random.choice(lines).replace("\n", '')
            cookiebot.forwardMessage(chat_id, int(target.split()[0]), int(target.split()[1]))
            break
        except Exception as e:
            print(e)
        

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




#MAIN THREAD FUNCTION
def thread_function(msg):
    try:
        if any(key in msg for key in ['dice', 'poll', 'voice_chat_started', 'voice_chat_ended']) or 'from' not in msg:
            return
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id, msg['message_id'])
        publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions = 1, 0, 1, 5, 600, 300, 1, 1
        if chat_type == 'private' and 'reply_to_message' not in msg:
            if 'text' in msg and msg['text'] == "/stop" and msg['from']['id'] == mekhyID:
                os._exit(0)
            elif content_type in ['photo', 'video', 'document']:
                ReceivePublisher(cookiebot, msg, chat_id)
            else:
                cookiebot.sendMessage(chat_id, "Olá, sou o CookieBot!\n\n**Para agendar uma postagem, envie a sua mensagem por aqui (lembrando que deve conter uma foto, vídeo, gif ou documento)**\n\nSou um bot com IA de conversa, conteúdo infinito, conteúdo customizado e speech-to-text.\nSe quiser me adicionar no seu chat ou obter a lista de comandos comentada, mande uma mensagem para o @MekhyW")
        else:
            if chat_type != 'private':
                #BEGGINING OF ADMINISTRATORS GATHERING
                listaadmins, listaadmins_id = [], []
                if not os.path.exists("GranularAdmins/GranularAdmins_" + str(chat_id) + ".txt"):
                    text = open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt", 'w').close()
                wait_open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt")
                text_file = open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt", 'r', encoding='utf-8')
                lines = text_file.readlines()
                text_file.close()
                if lines != []:
                    for username in lines:
                        listaadmins.append(username.replace("\n", ''))
                else:
                    for admin in cookiebot.getChatAdministrators(chat_id):
                        if 'username' in admin['user']:
                            listaadmins.append(str(admin['user']['username']))
                        listaadmins_id.append(str(admin['user']['id']))
                #END OF ADMINISTRATORS GATHERING
                #BEGGINING OF NEW NAME GATHERING
                if not os.path.isfile("Registers/"+str(chat_id)+".txt"):
                    open("Registers/"+str(chat_id)+".txt", 'a', encoding='utf-8').close() 
                wait_open("Registers/"+str(chat_id)+".txt")
                text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf-8')
                if 'username' in msg['from'] and (check_if_string_in_file(text_file, msg['from']['username']) == False):
                    text_file.write("\n"+msg['from']['username'])
                text_file.close()
                #END OF NEW NAME GATHERING
                publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions = GetConfig(chat_id)
                #BEGINNING OF CALENDAR SYNC AND FURBOTS CHECK
                wait_open("Registers/"+str(chat_id)+".txt")
                text_file = open("Registers/"+str(chat_id)+".txt", "r", encoding='utf-8')
                lines = text_file.read().split("\n")
                text_file.close()
                text_file = open("Registers/"+str(chat_id)+".txt", "w", encoding='utf-8')
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
                PublisherController(msg, chat_id, publisher)
            if content_type == "new_chat_member":
                if CheckCAS(cookiebot, msg, chat_id) == False and CheckRaider(cookiebot, msg, chat_id) == False:
                    Limbo(msg, chat_id)
                    if captchatimespan > 0 and ("CookieMWbot" in listaadmins or "MekhysBombot" in listaadmins):
                        Captcha(cookiebot, msg, chat_id, captchatimespan)
                    else:
                        Bemvindo(cookiebot, msg, chat_id, limbotimespan)
            elif content_type == "left_chat_member":
                left_chat_member(msg, chat_id)
            elif content_type == "voice":
                if utilityfunctions == True:
                    Speech_to_text(msg, chat_id)
            elif content_type == "audio":
                pass
            elif content_type == "photo":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
                CheckLimbo(msg, chat_id, limbotimespan)
            elif content_type == "video":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
                CheckLimbo(msg, chat_id, limbotimespan)
            elif content_type == "document":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                    ReplySticker(msg, chat_id)
            elif content_type == "sticker":
                CheckLimbo(msg, chat_id, limbotimespan)
                Sticker_anti_spam(msg, chat_id, stickerspamlimit)
                if sfw == 1:
                    AddtoStickerDatabase(msg, chat_id)
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                    ReplySticker(msg, chat_id)
            elif 'text' in msg:
                if (msg['text'].startswith("/aleatorio") or msg['text'].startswith("/aleatório")) and funfunctions == True:
                    ReplyAleatorio(msg, chat_id)
                #elif msg['text'].startswith("/") and " " not in msg['text'] and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and str(datetime.date.today()) == lastmessagedate and float(lastmessagetime)+60 >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                #    CooldownAction(msg, chat_id)
                elif (msg['text'].startswith("/dado") or (msg['text'].lower().startswith("/d") and msg['text'].replace("@CookieMWbot", '').split()[0][2:].isnumeric())) and funfunctions == True:
                    Dado(msg, chat_id)
                elif msg['text'].startswith("/idade") and funfunctions == True:
                    Idade(msg, chat_id)
                elif msg['text'].startswith("/genero") and funfunctions == True:
                    Genero(msg, chat_id)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, DÊ REPLY NESTA MENSAGEM com a mensagem que será exibida quando alguém entrar no grupo":
                    if str(msg['from']['username']) in listaadmins:
                        AtualizaBemvindo(msg, chat_id)
                    else:
                        cookiebot.sendMessage(chat_id, "Você não é um admin do grupo!", reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith("/novobemvindo"):
                    NovoBemvindo(msg, chat_id)
                elif FurBots == False and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, DÊ REPLY NESTA MENSAGEM com a mensagem que será exibida com o /regras":
                    if str(msg['from']['username']) in listaadmins:
                        AtualizaRegras(msg, chat_id)
                    else:
                        cookiebot.sendMessage(chat_id, "Você não é um admin do grupo!", reply_to_message_id=msg['message_id'])
                elif FurBots == False and msg['text'].startswith("/novasregras"):
                    NovasRegras(msg, chat_id)
                elif FurBots == False and msg['text'].startswith("/regras"):
                    Regras(msg, chat_id)
                elif msg['text'].startswith("/tavivo"):
                    TaVivo(msg, chat_id)
                elif msg['text'].startswith("/everyone"):
                    Everyone(msg, chat_id, listaadmins)
                elif msg['text'].startswith("/adm"):
                    Adm(msg, chat_id, listaadmins)
                elif msg['text'].startswith("/comandos"):
                    Comandos(msg, chat_id)
                elif FurBots == False and (msg['text'].startswith("/hoje") or msg['text'].startswith("/today")) and funfunctions == True:
                    Hoje(msg, chat_id)
                elif FurBots == False and (msg['text'].startswith("/cheiro") or msg['text'].startswith("/smell")) and funfunctions == True:
                    Cheiro(msg, chat_id)
                elif FurBots == False and ('eu faço' in msg['text'] or 'eu faco' in msg['text']) and '?' in msg['text'] and funfunctions == True:
                    QqEuFaço(msg, chat_id)
                elif msg['text'].startswith("/ideiadesenho") and utilityfunctions == True:
                    IdeiaDesenho(msg, chat_id)
                elif msg['text'].startswith("/contato"):
                    Contato(msg, chat_id)
                elif msg['text'].startswith("/qualquercoisa") and utilityfunctions == True:
                    PromptQualquerCoisa(msg, chat_id)
                elif msg['text'].startswith("/configurar"):
                    Configurar(cookiebot, msg, chat_id, listaadmins)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "DÊ REPLY NESTA MENSAGEM com o novo valor da variável" in msg['reply_to_message']['text']:
                    ConfigurarSettar(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/") and " " not in msg['text'] and os.path.exists("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')) and utilityfunctions == True:
                    CustomCommand(msg, chat_id)
                elif msg['text'].startswith("/") and " " not in msg['text'] and (len(msg['text'].split('@')) < 2 or msg['text'].split('@')[1] in ['CookieMWbot', 'MekhysBombot']) and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and utilityfunctions == True:
                    QualquerCoisa(msg, chat_id, sfw)
                elif (msg['text'].startswith("Cookiebot") or msg['text'].startswith("cookiebot") or 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') and ("quem" in msg['text'] or "Quem" in msg['text']) and ("?" in msg['text']):
                    Quem(msg, chat_id)
                elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and msg['reply_to_message']['caption'] == "Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo te removerei do chat\n(OBS: Se não aparecem 4 digitos, abra a foto completa)".format(str(round(captchatimespan/60))):
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan)
                elif (('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') or "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']) and funfunctions == True:
                    if not OnSay(msg, chat_id):
                        InteligenciaArtificial(msg, chat_id)
                else:
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan)
                    CheckCaptcha(cookiebot, msg, chat_id, captchatimespan)
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
            run_unnatendedthreads()
    except:
        if 'ConnectionResetError' not in traceback.format_exc():
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
            cookiebot.sendMessage(mekhyID, str(msg))

def run_unnatendedthreads():
    global unnatended_threads
    num_running_threads = threading.active_count()
    num_max_threads = 10
    for unnatended_thread in unnatended_threads:
        if unnatended_thread.is_alive():
            unnatended_threads.remove(unnatended_thread)
        elif num_running_threads < num_max_threads:
            unnatended_thread.start()
            num_running_threads += 1
            unnatended_threads.remove(unnatended_thread)
    if len(unnatended_threads) > 0:
        print("{} threads are still unnatended".format(len(unnatended_threads)))
    gc.collect()

def handle(msg):
    try:
        global unnatended_threads
        new_thread = threading.Thread(target=thread_function, args=(msg,))
        unnatended_threads.append(new_thread)
        run_unnatendedthreads()
    except:
        if 'ConnectionResetError' not in traceback.format_exc():
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
            cookiebot.sendMessage(mekhyID, str(msg))

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    if 'CONFIG' in query_data:
        ConfigVariableButton(cookiebot, msg, query_data)
    elif 'PUBLISHER' in query_data:
        PublisherQuery(cookiebot, msg, query_data, mekhyID)
    elif 'PUBLISH' in query_data:
        PublishQuery(cookiebot, msg, query_data, mekhyID)
    else:
        listaadmins_id = []
        for admin in cookiebot.getChatAdministrators(msg['message']['reply_to_message']['chat']['id']):
            listaadmins_id.append(str(admin['user']['id']))
        if query_data == 'CAPTCHA' and str(from_id) in listaadmins_id:
            SolveCaptcha(cookiebot, msg, msg['message']['reply_to_message']['chat']['id'], True)
            DeleteMessage(telepot.message_identifier(msg['message']))
    run_unnatendedthreads()
        

MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()