import os
import random
import urllib.request
import datetime
from bs4 import BeautifulSoup
from universal_funcs import googleAPIkey, searchEngineCX, saucenao_key, storage_bucket, get_request_backend, post_request_backend, send_chat_action, send_message, react_to_message, send_photo, forward_message, cookiebotTOKEN
from UserRegisters import get_members_chat
import google_images_search
import googleapiclient.discovery
from deep_translator import GoogleTranslator
from saucenao_api import SauceNao, errors
import cv2
import numpy as np
googleimagesearcher = google_images_search.GoogleImagesSearch(googleAPIkey, searchEngineCX, validate_images=False)
youtubesearcher = googleapiclient.discovery.build("youtube", "v3", developerKey=googleAPIkey)
reverseimagesearcher = SauceNao(saucenao_key)
templates_eng = os.listdir("Static/Meme/English")
templates_pt = os.listdir("Static/Meme/Portuguese")
bloblist_fighters_eng = list(storage_bucket.list_blobs(prefix="Fight/English"))
bloblist_fighters_pt = list(storage_bucket.list_blobs(prefix="Fight/Portuguese"))

with open('Static/avoid_search.txt', 'r', encoding='utf-8') as f:
    avoid_search = f.readlines()
avoid_search = [x.strip() for x in avoid_search]

def fetch_temp_jpg(cookiebot, msg, only_return_url=False):
    try:
        path = cookiebot.getFile(msg['photo'][-1]['file_id'])['file_path']
        image_url = f'https://api.telegram.org/file/bot{cookiebotTOKEN}/{path}'
        if only_return_url:
            return image_url
        urllib.request.urlretrieve(image_url, 'temp.jpg')
    except KeyError:
        path = cookiebot.getFile(msg['document']['file_id'])['file_path']
        video_url = f'https://api.telegram.org/file/bot{cookiebotTOKEN}/{path}'
        if only_return_url:
            return video_url
        urllib.request.urlretrieve(video_url, 'temp.mp4')
        vidcap = cv2.VideoCapture('temp.mp4')
        success, image = vidcap.read()
        cv2.imwrite('temp.jpg', image)
        os.remove('temp.mp4')

def get_members_tagged(msg):
    members_tagged = []
    if '@' in msg['text']:
        for target in msg['text'].split("@")[1:]:
            if 'CookieMWbot' in target:
                continue
            members_tagged.append(target)
    return members_tagged

def reverse_search(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if not 'reply_to_message' in msg:
        send_message(cookiebot, chat_id, "Responda uma imagem com o comando para procurar a fonte (busca reversa)\n<blockquote>Para busca direta, use o /qualquercoisa</blockquote>", msg, language)
        return
    url = fetch_temp_jpg(cookiebot, msg['reply_to_message'], only_return_url=True)
    try:
        results = reverseimagesearcher.from_url(url)
    except errors.ShortLimitReachedError:
        send_message(cookiebot, chat_id, "Ainda estou processando outros resultados, aguarde e tente novamente", msg, language)
        return
    except errors.LongLimitReachedError:
        send_message(cookiebot, chat_id, "Limite diário de busca atingido, aguarde e tente novamente", msg, language)
        return
    if results and results[0].urls and results[0].similarity > 80:
        best = results[0]
        answer = 'Melhor correspondência encontrada:\n\n'
        answer += f'"{best.title}"'
        if best.author:
            answer +=  f" - {best.author}"
        answer += f"\n{best.urls[0]}\n\n"
        react_to_message(msg, '🫡', is_big=False, is_alternate_bot=is_alternate_bot)
        send_message(cookiebot, chat_id, answer, msg, language)
    else:
        react_to_message(msg, '🤷', is_big=False, is_alternate_bot=is_alternate_bot)
        send_message(cookiebot, chat_id, "A busca não encontrou correspondência, parece ser uma imagem original!", msg, language)

def prompt_qualquer_coisa(cookiebot, msg, chat_id, language):
    send_message(cookiebot, chat_id, "Troque o 'qualquercoisa' por algo, vou mandar uma foto desse algo\n<blockquote>EXEMPLO: /fennec</blockquote>", msg, language)

def qualquer_coisa(cookiebot, msg, chat_id, sfw, language, is_alternate_bot=0):
    searchterm = msg['text'].split("@")[0].replace("/", ' ').replace("@CookieMWbot", '')
    if searchterm.split()[0] in avoid_search:
        return
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    if sfw == 0:
        googleimagesearcher.search({'q': searchterm, 'num': 10, 'safe':'off', 'filetype':'jpg|gif|png'})
    else:
        googleimagesearcher.search({'q': searchterm, 'num': 10, 'safe':'medium', 'filetype':'jpg|gif|png'})
    images = googleimagesearcher.results()
    random.shuffle(images)
    for image in images:
        try:
            if 'gif' in image.url:
                cookiebot.sendAnimation(chat_id, image.url, reply_to_message_id=msg['message_id'], caption=image.referrer_url)
            else:
                cookiebot.sendPhoto(chat_id, image.url, reply_to_message_id=msg['message_id'], caption=image.referrer_url)
            return 1
        except Exception as e:
            print(e)
    react_to_message(msg, '🤷', is_big=False, is_alternate_bot=is_alternate_bot)
    send_message(cookiebot, chat_id, "Não consegui achar uma imagem <i>(ou era NSFW e eu filtrei)</i>", msg, language)

def youtube_search(cookiebot, msg, chat_id, language):
    if len(msg['text'].split()) == 1:
        send_message(cookiebot, chat_id, "Você precisa digitar o nome do vídeo\n<blockquote>EXEMPLO: /youtube batata assada</blockquote>", msg, language)
        return
    query = ' '.join(msg['text'].split()[1:])
    request = youtubesearcher.search().list(q=query, part="snippet", type="video", maxResults=10)
    response = request.execute()
    videos = response.get("items", [])
    if not videos:
        send_message(cookiebot, chat_id, "Nenhum vídeo encontrado", msg, language)
        return
    random_video = random.choice(videos)
    video_url = f"https://www.youtube.com/watch?v={random_video['id']['videoId']}"
    video_description = random_video["snippet"]["description"]
    send_message(cookiebot, chat_id, f"<i>{video_url}</i>\n\n<b>{video_description}</b>", msg, language, parse_mode='HTML')

def add_to_random_database(msg, chat_id, photo_id=''):
    if any(x in msg['chat']['title'].lower() for x in ['yiff', 'porn', '18+', '+18', 'nsfw', 'hentai', 'rule34', 'r34', 'nude', '🔞']):
        return
    if not 'forward_from' in msg and not 'forward_from_chat' in msg:
        post_request_backend('randomdatabase', {'id': chat_id, 'idMessage': str(msg['message_id']), 'idMedia': photo_id})

def random_media(cookiebot, msg, chat_id, thread_id=None, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    for _ in range(50):
        try:
            target = get_request_backend("randomdatabase")
            forward_message(cookiebot, chat_id, target['id'], target['idMessage'], thread_id=thread_id, is_alternate_bot=is_alternate_bot)
            break
        except Exception as e:
            print(e)

def add_to_sticker_database(msg, chat_id):
    if any(x in msg['chat']['title'].lower() for x in ['yiff', 'porn', '18+', '+18', 'nsfw', 'hentai', 'rule34', 'r34', 'nude', '🔞']):
        return
    if 'emoji' in msg['sticker'] and msg['sticker']['emoji'] in ['🍆', '🍑', '🥵', '💦', '🫦']:
        return
    stickerId = msg['sticker']['file_id']
    post_request_backend('stickerdatabase', {'id': stickerId})

def reply_sticker(cookiebot, msg, chat_id):
    sticker = get_request_backend("stickerdatabase")
    cookiebot.sendSticker(chat_id, sticker['id'], reply_to_message_id=msg['message_id'])

def meme(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    members = get_members_chat(chat_id)
    members_tagged = get_members_tagged(msg)
    caption = ""
    for _ in range(100):
        if 'pt' not in language.lower():
            template = "Static/Meme/English/" + random.choice(templates_eng)
        else:
            template_id = random.randint(0, len(templates_pt)+len(templates_eng)-1)
            template = "Static/Meme/Portuguese/" + templates_pt[template_id - len(templates_eng)] if template_id > len(templates_eng) - 1 else "Static/Meme/English/" + templates_eng[template_id]
        template_img = cv2.imread(template)
        mask_green = cv2.inRange(template_img, (0, 210, 0), (40, 255, 40))
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(members_tagged) <= len(contours_green):
            break
    for green in contours_green:
        x, y, w, h = cv2.boundingRect(green)
        for _ in range(100):
            if len(members_tagged) > 0:
                chosen_member = random.choice(members_tagged)
                members_tagged.remove(chosen_member)
                members = [member for member in members if 'user' not in member or member['user'] != chosen_member]
            else:
                try:
                    chosen_member = random.choice(members)
                except IndexError:
                    return meme(cookiebot, msg, chat_id, language)
                members.remove(chosen_member)
                if 'user' in chosen_member:
                    chosen_member = chosen_member['user']
                else:
                    continue
            try:
                url = f"https://telegram.me/{chosen_member}"
            except IndexError:
                continue
            req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
            html = urllib.request.urlopen(req)
            soup = BeautifulSoup(html, "html.parser")
            images = list(soup.findAll('img'))
            if len(images) > 0:
                break
        resp = urllib.request.urlopen(images[0]['src'])
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (w, h), interpolation=cv2.INTER_NEAREST)
        mask_green_copy = mask_green[y:y+h, x:x+w]
        for i in range(y, y+h):
            for j in range(x, x+w):
                if mask_green_copy[i-y, j-x] == 255:
                    template_img[i, j] = image[i-y, j-x]
        caption += f"@{chosen_member} "
    cv2.imwrite("meme.png", template_img)
    with open("meme.png", 'rb') as final_img:
        send_photo(cookiebot, chat_id, photo=final_img, caption=caption, msg_to_reply=msg)
    try:
        os.remove("meme.png")
    except FileNotFoundError:
        pass

def battle(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    react_to_message(msg, '🔥', is_alternate_bot=is_alternate_bot)
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    members_tagged = get_members_tagged(msg)
    if len(members_tagged) > 1 or 'random' in msg['text'].lower():
        if 'random' in msg['text'].lower():
            members = get_members_chat(chat_id)
            if len(members) < 2:
                send_message(cookiebot, chat_id, "Não há membros suficientes para batalhar", msg, language)
                return
            for _ in range(100):
                random.shuffle(members)
                if 'user' in members[0] and 'user' in members[1]:
                    users = members[0]['user'], members[1]['user']
                    break
        else:
            users = members_tagged[0], members_tagged[1]
        soup1 = BeautifulSoup(urllib.request.urlopen(urllib.request.Request(f"https://telegram.me/{users[0]}", headers={'User-Agent' : "Magic Browser"})), "html.parser")
        soup2 = BeautifulSoup(urllib.request.urlopen(urllib.request.Request(f"https://telegram.me/{users[1]}", headers={'User-Agent' : "Magic Browser"})), "html.parser")
        images = list(soup1.findAll('img')), list(soup2.findAll('img'))
        if len(images[0]) == 0:
            send_message(cookiebot, chat_id, f"Não consegui extrair a foto de {members_tagged[0]}. Verifique se está público!", msg, language)
            return
        if len(images[1]) == 0:
            send_message(cookiebot, chat_id, f"Não consegui extrair a foto de {members_tagged[1]}. Verifique se está público!", msg, language)
            return
        resp = urllib.request.urlopen(images[0][0]['src']), urllib.request.urlopen(images[1][0]['src'])
        user_images = cv2.imdecode(np.asarray(bytearray(resp[0].read()), dtype="uint8"), cv2.IMREAD_COLOR), cv2.imdecode(np.asarray(bytearray(resp[1].read()), dtype="uint8"), cv2.IMREAD_COLOR)
        cv2.imwrite("user1.jpg", user_images[0])
        cv2.imwrite("user2.jpg", user_images[1])
        user_images = open("user1.jpg", 'rb'), open("user2.jpg", 'rb')
        if len(members_tagged) > 1:
            medias, choices = [{'type': 'photo', 'media': user_images[0]}, {'type': 'photo', 'media': user_images[1]}], [members_tagged[0], members_tagged[1]]
            caption = f"{members_tagged[0]} VS {members_tagged[1]}"
        else:
            medias, choices = [{'type': 'photo', 'media': user_images[0]}, {'type': 'photo', 'media': user_images[1]}], [users[0], users[1]]
            caption = f"@{users[0]} VS @{users[1]}"
        poll_title = "QUEM VENCE?"
        caption += f"\n\nTipo: {random.choice(['Boxe 🥊🥊', 'Luta Livre 🎭', 'Luta Greco 🤼‍♂️', 'Artes Marciais 🥋', 'Sambo 👊', 'Muay Thai 🥋', 'Luta de rua 👊', 'Luta de piscina💧', 'Judo 🇯🇵', 'Sumo ⛩', 'Gutpunching 💪', 'Ballbusting 🍳🍳'])}\nRegras: {random.choice(['KO por rounds', 'KO sem rounds', 'Vale tudo', 'Mais gols no Bomba Patch', 'Mais latinhas bebidas', 'Maior numero de litrão', 'Até Beber, Cair, Levantar', 'O último do mesão de magic'])}\nEquipamento: {random.choice(['Full Gear', 'Só luvas', 'De calcinha', 'Pelados', 'Uniforme de luta', 'Vale tudo', 'Tanguinha de sumô', 'Robô gigante', 'Uniforme de Maid', 'Kimono de Judô', 'Armadura Samurai', 'Toalha de nerdola', 'Uniforme de Waifu escolar', 'Roupa da Sailor Moon', 'Menininha mágica', 'Cosplay da Akatsuki', 'Aqueles maiôs de natação japoneses', 'Bunnysuit', 'Casaco de inverno cyberpunk', 'Chinelo', 'Ronaldinho Gaúcho', 'Uniforme do Vasco', 'Uniforme do Curintia', 'Camiseta do São Paulo', 'Uniforme do Parmeira', 'Roupa de bruxinha', 'Óculos Juliett', 'Tanguinha de Ratanabá'])}"
        if language == 'eng':
            poll_title = "WHO WINS?"
            caption = GoogleTranslator(source='auto', target='en').translate(caption)
        elif language == 'es':
            poll_title = "¿QUIÉN GANA?"
            caption = GoogleTranslator(source='auto', target='es').translate(caption)
        medias[0]['caption'] = caption
        cookiebot.sendMediaGroup(chat_id, medias, reply_to_message_id=msg['message_id'])
        cookiebot.sendPoll(chat_id, poll_title, choices, is_anonymous=False, allows_multiple_answers=False, reply_to_message_id=msg['message_id'])
        return
    elif len(members_tagged):
        user = members_tagged[0]
        html = urllib.request.urlopen(urllib.request.Request(f"https://telegram.me/{user}", headers={'User-Agent' : "Magic Browser"}))
        soup = BeautifulSoup(html, "html.parser")
        images = list(soup.findAll('img'))
        if not len(images):
            send_message(cookiebot, chat_id, "Não consegui extrair a foto de perfil desse usuário. Verifique se está público!", msg, language)
            return
        resp = urllib.request.urlopen(images[0]['src'])
        user_image = cv2.imdecode(np.asarray(bytearray(resp.read()), dtype="uint8"), cv2.IMREAD_COLOR)
        cv2.imwrite("user.jpg", user_image)
        user_image = open("user.jpg", 'rb')
    else:
        user = msg['from']['username'] if 'username' in msg['from'] else msg['from']['first_name']
        try:
            user_image = cookiebot.getUserProfilePhotos(msg['from']['id'], limit=1)['photos'][0][-1]['file_id']
        except IndexError:
            send_message(cookiebot, chat_id, "Você precisa ter uma foto de perfil <i>(ou está privado)</i>", msg, language)
            return
    if language == 'pt':
        fighter = random.choice(random.choice([bloblist_fighters_eng, bloblist_fighters_pt]))
        poll_title = "QUEM VENCE " + random.choice(["NO TAPA", "NO X1", "NO SOCO", "NA MÃO", "NA PORRADA", "NO ARGUMENTO", "NO DUELO", "NA VIDA"]) + "?"
    else:
        fighter = random.choice(bloblist_fighters_eng)
        poll_title = "¿QUIÉN GANA?" if language == 'es' else "WHO WINS?"
    fighter_image = fighter.generate_signed_url(datetime.timedelta(minutes=15), method='GET')
    fighter_name = fighter.name.split('/')[-1].replace(".png", "").replace(".jpg", "").replace(".jpeg", "").replace("_", " ").capitalize()
    medias, caption, choices = [{'type': 'photo', 'media': user_image}, {'type': 'photo', 'media': fighter_image}], f"{user} VS {fighter_name}", [user, fighter_name]
    if random.choice([0, 1]):
        medias, caption, choices = [medias[1], medias[0]], f"{fighter_name} VS {user}", [fighter_name, user]
    medias[0]['caption'] = caption
    cookiebot.sendMediaGroup(chat_id, medias, reply_to_message_id=msg['message_id'])
    cookiebot.sendPoll(chat_id, poll_title, choices, is_anonymous=False, allows_multiple_answers=False, reply_to_message_id=msg['message_id'])
