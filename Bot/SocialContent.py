import os
import random
import urllib.request
import datetime
import requests
import re
import json
from bs4 import BeautifulSoup
from universal_funcs import googleAPIkey, searchEngineCX, saucenao_key, storage_bucket, get_request_backend, post_request_backend, send_chat_action, send_message, react_to_message, send_photo, forward_message, cookiebotTOKEN, translate
from UserRegisters import get_members_chat
import google_images_search
import googleapiclient.discovery
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
TWITTER_REGEX = r'(?:twitter|x)\.com/[a-zA-Z0-9_]{1,15}/status/[0-9]{1,20}'
TIKTOK_REGEX = r'(?:tiktok\.com/@[a-zA-Z0-9_.]{1,24}/video/[0-9]{1,20}|vm\.tiktok\.com/[A-Za-z0-9]+/?)'
INSTAGRAM_REGEX = r'instagram\.com/(reel|p)/[a-zA-Z0-9_-]{1,11}'
BSKY_REGEX = r'bsky\.app/profile/[a-zA-Z0-9.-]{1,253}'

with open('Static/avoid_search.txt', 'r', encoding='utf-8') as f:
    avoid_search = f.readlines()
avoid_search = [x.strip() for x in avoid_search]

def fix_embed_if_social_link(message: str) -> str | bool:
    message = message.strip()
    if any(domain in message for domain in ['vxtwitter.com', 'fxtwitter.com', 'fixupx.com', 'd.tnktok.com', 'vm.vxtiktok.com', 'ddinstagram.com', 'fxbsky.app']):
        return False
    try:
        requests.get(message, timeout=2)
    except:
        return False
    transformations = [
        (TWITTER_REGEX, "https://fixupx.com/{}", r'[^/]+/status/[0-9]+'),
        (TIKTOK_REGEX, "https://vm.vxtiktok.com/{}", r'@[^/]+/video/[0-9]+'),
        #(INSTAGRAM_REGEX, "https://ddinstagram.com/{}", r'(reel|p)/([^?/]+)'),
        (BSKY_REGEX, "https://fxbsky.app/profile/{}", r'\.app/profile/(.+)')
    ]
    if re.search(TIKTOK_REGEX, message) and re.search(r'vm\.tiktok\.com/.+|tiktok\.com/t/.+', message):
        try:
            message = requests.get(message, timeout=1).url
        except:
            return False
    for main_pattern, template, extract_pattern in transformations:
        if re.search(main_pattern, message):
            if match := re.search(extract_pattern, message):
                if 'ddinstagram.com' in template:
                    path = match.group(1) + '/' + match.group(2)
                    query = message[message.find('?'):] if '?' in message else ''
                    return template.format(path) + query
                return template.format(match.group(1) if '(' in extract_pattern else match.group())
            return False
    return False

def check_reply_embed(cookiebot, msg, chat_id, is_alternate_bot):
    if 'link_preview_options' not in msg:
        return
    url_embed = fix_embed_if_social_link(msg['text'])
    if url_embed and url_embed.strip() != msg['text'].strip():
        send_message(cookiebot, chat_id, url_embed, msg_to_reply=msg, is_alternate_bot=is_alternate_bot, link_preview_options=json.dumps({'show_above_text': True, 'prefer_large_media': True, 'disable_web_page_preview': False}))

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
            if target.endswith('bot'):
                continue
            members_tagged.append(target)
    return members_tagged

def reverse_search(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if not 'reply_to_message' in msg:
        text = "Responda uma imagem com o comando para procurar a fonte (busca reversa)\n<blockquote> Para busca direta, use o /qualquercoisa </blockquote>" if language == 'pt' else "Responda a una imagen con el comando para buscar la fuente (búsqueda inversa)\n<blockquote> Para una búsqueda directa, use /lo que sea</blockquote>" if language == 'es' else "Reply an image with the command to search for the source (reverse search)\n<blockquote> For direct search, use /anything </blockquote>"
        send_message(cookiebot, chat_id, text, msg)
        return
    url = fetch_temp_jpg(cookiebot, msg['reply_to_message'], only_return_url=True)
    try:
        results = reverseimagesearcher.from_url(url)
    except errors.ShortLimitReachedError:
        text = "Ainda estou processando outros resultados, aguarde e tente novamente" if language == 'pt' else "Todavía estoy procesando otros resultados, espera y vuelve a intentarlo" if language == 'es' else "I'm still processing other results, please wait and try again"
        send_message(cookiebot, chat_id, text, msg)
        return
    except errors.LongLimitReachedError:
        text = "Limite diário de busca atingido, aguarde e tente novamente" if language == 'pt' else "Límite diario de búsqueda alcanzado, espere y vuelva a intentarlo" if language == 'es' else "Daily search limit reached, please wait and try again"
        send_message(cookiebot, chat_id, text, msg)
        return
    if results and results[0].urls and results[0].similarity > 80:
        best = results[0]
        answer = 'Melhor correspondência encontrada:\n\n' if language == 'pt' else 'Mejor coincidencia encontrada:\n\n' if language == 'es' else 'Best match found:\n\n'
        answer += f'"{best.title}"'
        if best.author:
            answer +=  f" - {best.author}"
        answer += f"\n{best.urls[0]}\n\n"
        react_to_message(msg, '🫡', is_big=False, is_alternate_bot=is_alternate_bot)
        send_message(cookiebot, chat_id, answer, msg, language)
    else:
        react_to_message(msg, '🤷', is_big=False, is_alternate_bot=is_alternate_bot)
        text = "A busca não encontrou correspondência, parece ser uma imagem original!" if language == 'pt' else "La búsqueda no encontró coincidencias, ¡parece ser una imagen original!" if language == 'es' else "The search found no matches, it seems to be an original image!"
        send_message(cookiebot, chat_id, text, msg)

def prompt_qualquer_coisa(cookiebot, msg, chat_id, language):
    text = "Você precisa digitar o nome do que quer procurar\n<blockquote> EXEMPLO: /batata frita </blockquote>" if language == 'pt' else "Necesitas escribir el nombre de lo que quieres buscar\n<blockquote> EJEMPLO: /french fries </blockquote>" if language == 'es' else "You need to type the name of what you want to search for\n<blockquote> EXAMPLE: /french fries </blockquote>"
    send_message(cookiebot, chat_id, text, msg)

def qualquer_coisa(cookiebot, msg, chat_id, sfw, language, is_alternate_bot=0):
    searchterm = msg['text'].split("@")[0].replace("/", ' ').replace("@CookieMWbot", '').replace("@pawstralbot", '')
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
            return True
        except Exception as e:
            pass
    react_to_message(msg, '🤷', is_big=False, is_alternate_bot=is_alternate_bot)
    text = "Não consegui achar uma imagem <i> (ou era NSFW e eu filtrei) </i>" if language == 'pt' else "No pude encontrar una imagen <i> (o era NSFW y lo filtré) </i>" if language == 'es' else "I couldn't find an image <i> (or it was NSFW and I filtered it) </i>"
    send_message(cookiebot, chat_id, text, msg)

def youtube_search(cookiebot, msg, chat_id, language):
    if len(msg['text'].split()) == 1:
        text = "Você precisa digitar o nome do vídeo\n<blockquote> EXEMPLO: /youtube batata assada </blockquote>" if language == 'pt' else "Debes escribir el nombre del video\n<blockquote> EJEMPLO: /youtube papa al horno</blockquote>" if language == 'es' else "You need to type the name of the video\n<blockquote> EXAMPLE: /youtube baked potato </blockquote>"
        send_message(cookiebot, chat_id, text, msg)
        return
    query = ' '.join(msg['text'].split()[1:])
    request = youtubesearcher.search().list(q=query, part="snippet", type="video", maxResults=10)
    response = request.execute()
    videos = response.get("items", [])
    if not videos:
        react_to_message(msg, '🤷', is_big=False)
        text = "Não consegui achar nenhum vídeo" if language == 'pt' else "No pude encontrar ningún video" if language == 'es' else "I couldn't find any video"
        send_message(cookiebot, chat_id, text, msg)
        return
    random_video = random.choice(videos)
    video_url = f"https://www.youtube.com/watch?v={random_video['id']['videoId']}"
    video_description = random_video["snippet"]["description"]
    send_message(cookiebot, chat_id, f"<i> {video_url} </i>\n\n<b> {video_description} </b>", msg, parse_mode='HTML')

def add_to_random_database(msg, chat_id, photo_id=''):
    if 'forward_from' in msg or 'forward_from_chat' in msg:
        return
    if any(x in msg['chat']['title'].lower() for x in ['yiff', 'porn', '18+', '+18', 'nsfw', 'hentai', 'rule34', 'r34', 'nude', '🔞']):
        return
    post_request_backend('randomdatabase', {'id': chat_id, 'idMessage': str(msg['message_id']), 'idMedia': photo_id})

def random_media(cookiebot, msg, chat_id, thread_id=None, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    for _ in range(50):
        try:
            target = get_request_backend.__wrapped__("randomdatabase")
            forward_message(cookiebot, chat_id, target['id'], target['idMessage'], thread_id=thread_id, is_alternate_bot=is_alternate_bot)
            break
        except Exception as e:
            pass

def add_to_sticker_database(msg):
    BANNED_EMOJIS = ['🍆', '🍑', '🍌', '🍭', '🥵', '💦', '🫦', '👄', '🔞', '😏', '🇩🇪', '⚡', '👌', '👌🏻', '👌🏼', '👌🏽', '👌🏾', '👌🏿', '❤️‍🔥', '🌽', '🍩', '🍼', '🥛', '😫', '😩', '🌚', '♋️', '🩸', '🪢', '👅', '😈', '🩲', '💋', '🤤', '🍒', '🥖', '🌶️', '💄', '🔩', '🐙']
    BANNED_TITLESUBSTRINGS = ['yiff', 'porn', '18+', '+18', 'nsfw', 'hentai', 'rule34', 'r34', 'nude', '🔞']
    if any(x in msg['chat']['title'].lower() for x in BANNED_TITLESUBSTRINGS):
        return
    if (not 'emoji' in msg['sticker']) or any(x in msg['sticker']['emoji'] for x in BANNED_EMOJIS):
        return
    if (not 'set_name' in msg['sticker']) or (not re.match(r'^[a-zA-Z0-9]+$', msg['sticker']['set_name'])):
        return
    stickerId = msg['sticker']['file_id']
    post_request_backend('stickerdatabase', {'id': stickerId})

def reply_sticker(cookiebot, msg, chat_id):
    sticker = get_request_backend("stickerdatabase")
    cookiebot.sendSticker(chat_id, sticker['id'], reply_to_message_id=msg['message_id'])

def meme(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    members = get_members_chat(cookiebot, chat_id)
    members_tagged = get_members_tagged(msg)
    print(f"NUMBER OF MEMBERS FOUND: {len(members)}")
    print(f"NUMBER OF MEMBERS TAGGED: {len(members_tagged)}")
    if len(members_tagged) > 5:
        text = "Não é possível criar memes com mais de 5 membros" if language == 'pt' else "No se pueden crear memes con más de 5 miembros" if language == 'es' else "It is not possible to create memes with more than 5 members"
        send_message(cookiebot, chat_id, text, msg)
        return
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
        chosen_member = None
        profile_image = None
        while members_tagged and not profile_image:
            chosen_member = random.choice(members_tagged)
            members_tagged.remove(chosen_member)
            members = [m for m in members if 'user' not in m or m['user'] != chosen_member]
            profile_image = get_profile_image(chosen_member)
        while members and not profile_image:
            member = random.choice(members)
            members.remove(member)
            if 'user' not in member:
                continue
            chosen_member = member['user']
            profile_image = get_profile_image(chosen_member)
        if not profile_image:
            text = "Não consegui extrair a foto de perfil desse usuário. Verifique se está público!" if language == 'pt' else "No pude extraer la foto de perfil de este usuario. ¡Verifica si es público!" if language == 'es' else "I couldn't extract the profile picture of this user. Check if it's public!"
            send_message(cookiebot, chat_id, text, msg)
            return
        image = cv2.imdecode(np.asarray(bytearray(profile_image.read()), dtype="uint8"), cv2.IMREAD_COLOR)
        image = cv2.resize(image, (w, h), interpolation=cv2.INTER_NEAREST)
        mask_green_copy = mask_green[y:y+h, x:x+w]
        mask_region = mask_green_copy == 255
        template_img[y:y+h, x:x+w][mask_region] = image[mask_region]
        caption += f"@{chosen_member} "
    cv2.imwrite("meme.png", template_img)
    with open("meme.png", 'rb') as final_img:
        send_photo(cookiebot, chat_id, photo=final_img, caption=caption, msg_to_reply=msg)

def get_profile_image(username):
    """Helper function to get a user's profile image"""
    try:
        url = f"https://telegram.me/{username}"
        req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
        html = urllib.request.urlopen(req)
        soup = BeautifulSoup(html, "html.parser")
        images = soup.findAll('img')
        if images:
            return urllib.request.urlopen(images[0]['src'])
        else:
            return None
    except (IndexError, urllib.error.URLError) as e:
        return None

def battle(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    react_to_message(msg, '🔥', is_alternate_bot=is_alternate_bot)
    send_chat_action(cookiebot, chat_id, 'upload_photo')
    members_tagged = get_members_tagged(msg)
    if len(members_tagged) > 1 or 'random' in msg['text'].lower():
        if 'random' in msg['text'].lower():
            members = get_members_chat(cookiebot, chat_id)
            if len(members) < 2:
                text = "Não há membros suficientes para batalhar" if language == 'pt' else "No hay miembros suficientes para luchar" if language == 'es' else "Not enough members to battle"
                send_message(cookiebot, chat_id, text, msg)
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
            text = f"Não consegui extrair a foto de {members_tagged[0]}. Verifique se está público!" if language == 'pt' else f"No pude extraer la foto de {members_tagged[0]}. ¡Verifica si es público!" if language == 'es' else f"I couldn't extract the photo of {members_tagged[0]}. Check if it's public!"
            send_message(cookiebot, chat_id, text, msg)
            return
        if len(images[1]) == 0:
            text = f"Não consegui extrair a foto de {members_tagged[1]}. Verifique se está público!" if language == 'pt' else f"No pude extraer la foto de {members_tagged[1]}. ¡Verifica si es público!" if language == 'es' else f"I couldn't extract the photo of {members_tagged[1]}. Check if it's public!"
            send_message(cookiebot, chat_id, text, msg)
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
        poll_title = "QUEM VENCE?" if language == 'pt' else "¿QUIÉN GANA?" if language == 'es' else "WHO WINS?"
        if language == 'pt':
            caption += f"\n\nTipo: {random.choice(['Boxe 🥊🥊', 'Luta Livre 🎭', 'Luta Greco 🤼‍♂️', 'Artes Marciais 🥋', 'Sambo 👊', 'Muay Thai 🥋', 'Luta de rua 👊', 'Luta de piscina💧', 'Judo 🇯🇵', 'Sumo ⛩', 'Gutpunching 💪', 'Ballbusting 🍳🍳'])}\nRegras: {random.choice(['KO por rounds', 'KO sem rounds', 'Vale tudo', 'Mais gols no Bomba Patch', 'Mais latinhas bebidas', 'Maior numero de litrão', 'Até Beber, Cair, Levantar', 'O último do mesão de magic'])}\nEquipamento: {random.choice(['Full Gear', 'Só luvas', 'De calcinha', 'Pelados', 'Uniforme de luta', 'Vale tudo', 'Tanguinha de sumô', 'Robô gigante', 'Uniforme de Maid', 'Kimono de Judô', 'Armadura Samurai', 'Toalha de nerdola', 'Uniforme de Waifu escolar', 'Roupa da Sailor Moon', 'Menininha mágica', 'Cosplay da Akatsuki', 'Aqueles maiôs de natação japoneses', 'Bunnysuit', 'Casaco de inverno cyberpunk', 'Chinelo', 'Ronaldinho Gaúcho', 'Uniforme do Vasco', 'Uniforme do Curintia', 'Camiseta do São Paulo', 'Uniforme do Parmeira', 'Roupa de bruxinha', 'Óculos Juliett', 'Tanguinha de Ratanabá'])}"
        elif language == 'es':
            caption += f"\n\nTipo: {random.choice(['Boxeo 🥊🥊', 'Lucha 🎭', 'Lucha griega 🤼‍♂️', 'Artes marciales 🥋', 'Sambo 👊', 'Muay Thai 🥋', 'Lucha callejera 👊', 'Lucha en la piscina💧', 'Judo 🇯🇵', 'Sumo ⛩', 'Golpes al estómago 💪', 'Romper pelotas 🍳🍳'])}\nReglas: {random.choice(['KO por asaltos', 'KO sin asaltos', 'Todo vale', 'Más goles en Bomba Patch', 'La mayor cantidad de latas bebidas', 'La mayor cantidad de litros', 'Hasta beber, caer, levantarse', 'El último de la mesa de Magic'])}\nEquipamento: {random.choice(['Equipo completo', 'Solo guantes', 'En bragas', 'Desnudo', 'Uniforme de combate', 'Vale todo', 'Tanga de sumo', 'Robot gigante', 'Uniforme de sirvienta', 'Kimono de judo', 'Armadura de samurái', 'Toalla de nerd', 'Uniforme de waifu escolar', 'Disfraz de Sailor Moon', 'Niña mágica', 'Cosplay de Akatsuki', 'Esos trajes de baño japoneses', 'Traje de conejita', 'Abrigo de invierno cyberpunk', 'Zapatilla', 'Traje de bruja', 'Tanga'])}"
        else:
            caption += f"\n\nType: {random.choice(['Boxing 🥊🥊', 'Wrestling 🎭', 'Greco Wrestling 🤼‍♂️', 'Martial Arts 🥋', 'Sambo 👊', 'Muay Thai 🥋', 'Street Fighting 👊', 'Pool Fighting💧', 'Judo 🇯🇵', 'Sumo ⛩', 'Gutpunching 💪', 'Ballbusting 🍳🍳'])}\nRules: {random.choice(['KO by rounds', 'KO without rounds', 'Anything goes', 'Most goals in Bomba Patch', 'Most cans of drinks', 'Biggest number of liters', 'Until Drinking, Falling, Getting Up', 'The last of the magic table'])}\nEquipment: {random.choice(['Full Gear', 'Gloves Only', 'In Panties', 'Naked', 'Fighting Uniform', 'Anything Goes', 'Sumo Thong', 'Giant Robot', 'Maid Uniform', 'Judo Kimono', 'Samurai Armor', 'Nerd Towel', 'School Waifu Uniform', 'Sailor Moon Outfit', 'Magical Little Girl', 'Akatsuki Cosplay', 'Those Japanese Swimming Swimsuits', 'Bunnysuit', 'Cyberpunk Winter Coat', 'Flip Flops', 'Witch Outfit', 'Thong'])}" 
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
            text = "Não consegui extrair a foto de perfil desse usuário. Verifique se está público!" if language == 'pt' else "No pude extraer la foto de perfil de este usuario. ¡Verifica si es público!" if language == 'es' else "I couldn't extract the profile picture of this user. Check if it's public!"
            send_message(cookiebot, chat_id, text, msg)
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
            text = "Você precisa ter uma foto de perfil <i> (ou está privado) </i>" if language == 'pt' else "Necesitas tener una foto de perfil <i> (o está privado) </i>" if language == 'es' else "You need to have a profile picture <i> (or it's private) </i>"
            send_message(cookiebot, chat_id, text, msg)
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
