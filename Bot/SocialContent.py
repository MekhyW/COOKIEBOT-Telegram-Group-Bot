from universal_funcs import *
import google_images_search, io, PIL
googleimagesearcher = google_images_search.GoogleImagesSearch(googleAPIkey, searchEngineCX, validate_images=False)
import cv2
import numpy as np

def PromptQualquerCoisa(cookiebot, msg, chat_id, language):
    Send(cookiebot, chat_id, "Troque o 'qualquercoisa' por algo, vou mandar uma foto desse algo\n\nEXEMPLO: /fennec\n(acentos, letras maiusculas e espaços não funcionam)", msg, language)

def QualquerCoisa(cookiebot, msg, chat_id, sfw, language):
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
    Send(cookiebot, chat_id, "Não consegui achar uma imagem (ou era NSFW e eu filtrei)", msg, language)
    try:
        my_bytes_io.close()
        temp_img.close()
    except UnboundLocalError as e:
        print(e)


def AddtoRandomDatabase(msg, chat_id, photo_id=''):
    if not 'forward_from' in msg:
        PostRequestBackend('randomdatabase', {'chat_id': chat_id, 'message_id': str(msg['message_id']), 'photo_id': photo_id})

def ReplyAleatorio(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    for attempt in range(10):
        try:
            target = GetRequestBackend("randomdatabase")
            cookiebot.forwardMessage(chat_id, target['id'], target['idMessage'])
            break
        except Exception as e:
            print(e)
        

def AddtoStickerDatabase(msg, chat_id):
    stickerId = msg['sticker']['file_id']
    PostRequestBackend('stickerdatabase', {'id': stickerId})

def ReplySticker(cookiebot, msg, chat_id):
    sticker = GetRequestBackend("stickerdatabase")
    cookiebot.sendSticker(chat_id, sticker['id'], reply_to_message_id=msg['message_id'])

def Meme(cookiebot, msg, chat_id, language):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    wait_open("Registers/"+str(chat_id)+".txt")
    text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf8')
    members = text_file.readlines()
    members_tagged = []
    if ('@' in msg['text']):
        for target in msg['text'].split("@")[1:]:
            if 'CookieMWbot' in target:
                continue
            members_tagged.append(target)
    text_file.close()
    wait_open("Random_Database.txt")
    text_file = open("Random_Database.txt", 'r+', encoding='utf-8')
    random_medias = text_file.readlines()
    random_photos = [media for media in random_medias if len(media.split()) > 2]
    text_file.close()
    templates_eng = os.listdir("Meme/English")
    templates_pt = os.listdir("Meme/Portuguese")
    caption = ""
    for attempt in range(10):
        if 'pt' not in language.lower():
            template = "Meme/English/" + random.choice(templates_eng)
        else:
            template_id = random.randint(0, len(templates_pt)+len(templates_eng)-1)
            if template_id > len(templates_eng)-1:
                template = "Meme/Portuguese/" + templates_pt[template_id-len(templates_eng)]
            else:
                template = "Meme/English/" + templates_eng[template_id]
        template_img = cv2.imread(template)
        mask_green = cv2.inRange(template_img, (0, 250, 0), (5, 255, 5))
        mask_red = cv2.inRange(template_img, (0, 0, 250), (5, 5, 255))
        contours_green, tree = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_red, tree = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours_green) < len(members):
            break
    for green in contours_green:
        x, y, w, h = cv2.boundingRect(green)
        for attempt in range(10):
            if not len(members_tagged) == 0:
                chosen_member = random.choice(members_tagged)
                members_tagged.remove(chosen_member)
            else:
                chosen_member = random.choice(members)
                members.remove(chosen_member)
            try:
                url = "https://telegram.me/{}".format(chosen_member.split()[0])
            except IndexError:
                continue
            req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
            html = urllib.request.urlopen(req)
            soup = BeautifulSoup(html, "html.parser")
            images = [img for img in soup.findAll('img')]
            if len(images) == 0:
                continue
            break
        resp = urllib.request.urlopen(images[0]['src'])
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)
        mask_green_copy = mask_green[y:y+h, x:x+w]
        for i in range(y, y+h):
            for j in range(x, x+w):
                if mask_green_copy[i-y, j-x] == 255:
                    template_img[i, j] = image[i-y, j-x]
        caption += "@{} ".format(chosen_member.split()[0])
    for red in contours_red:
        x, y, w, h = cv2.boundingRect(red)
        for attempt in range(10):
            try:
                chosen_photo = random.choice(random_photos)
                random_photos.remove(chosen_photo)
                photo_id = chosen_photo.split()[2].replace("\n", '')
                photo_info = cookiebot.getFile(photo_id)
                photo_url = "https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, photo_info['file_path'])
                break
            except:
                continue
        resp = urllib.request.urlopen(photo_url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)
        mask_red_copy = mask_red[y:y+h, x:x+w]
        for i in range(y, y+h):
            for j in range(x, x+w):
                if mask_red_copy[i-y, j-x] == 255:
                    template_img[i, j] = image[i-y, j-x]
    if len(members_tagged) > 0:
        Meme(cookiebot, msg, chat_id, language)
    else:
        cv2.imwrite("meme.png", template_img)
        final_img = open("meme.png", 'rb')
        cookiebot.sendPhoto(chat_id, photo=final_img, caption=caption, reply_to_message_id=msg['message_id'])
        final_img.close()
        try:
            os.remove("meme.png")
        except FileNotFoundError:
            pass
