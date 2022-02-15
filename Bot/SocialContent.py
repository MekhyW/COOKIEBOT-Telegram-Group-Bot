from universal_funcs import *
import google_images_search, io, PIL
googleimagesearcher = google_images_search.GoogleImagesSearch(googleAPIkey, searchEngineCX, validate_images=False)
import cv2
qrDecoder = cv2.QRCodeDetector()

def PromptQualquerCoisa(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Troque o 'qualquercoisa' por algo, vou mandar uma foto desse algo\n\nEXEMPLO: /fennec\n(acentos, letras maiusculas e espaços não funcionam)", reply_to_message_id=msg['message_id'])

def QualquerCoisa(cookiebot, msg, chat_id, sfw):
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

def ReplyAleatorio(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    wait_open("Random_Database.txt")
    text = open("Random_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    for attempt in range(10):
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

def ReplySticker(cookiebot, msg, chat_id):
    wait_open("Sticker_Database.txt")
    text = open("Sticker_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    cookiebot.sendSticker(chat_id, random.choice(lines).replace("\n", ''), reply_to_message_id=msg['message_id'])
