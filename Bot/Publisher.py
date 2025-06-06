import datetime
import random
import sqlite3
import re
import json
import traceback
import requests
from GroupShield import EMOJI_PATTERN
from universal_funcs import send_chat_action, send_message, forward_message, get_request_backend, react_to_message, emojis_to_numbers, ownerID, exchangerate_key, translate
from Configurations import get_config
from UserRegisters import get_members_chat
from price_parser import Price
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import telepot.exception
publisher_db = sqlite3.connect('Publisher.db', check_same_thread=False)
publisher_cursor = publisher_db.cursor()
publisher_cursor.execute("CREATE TABLE IF NOT EXISTS publisher (name TEXT, days INT, next_time TEXT, target_chat_id INT, postmail_chat_id INT, second_chatid INT, postmail_message_id INT, second_messageid INT, origin_userid INT)")
publisher_db.commit()
cache_posts = {}
POSTMAIL_CHAT_LINK = "https://t.me/CookiebotPostmail"
POSTMAIL_CHAT_ID = -1001869523792
APPROVAL_CHAT_ID = -1001659344607
URL_REGEX = r'\b((?:https?|ftp|file):\/\/[-a-zA-Z0-9+&@#\/%?=~_|!:,.;]{1,2048})'
EMOJI_PATTERN = re.compile(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+")

def add_post_to_cache(msg):
    if 'photo' in msg:
        media_type = 'photo'
        media_id = msg['photo'][-1]['file_id']
    elif 'video' in msg:
        media_type = 'video'
        media_id = msg['video']['file_id']
    elif 'animation' in msg:
        media_type = 'animation'
        media_id = msg['animation']['file_id']
    elif 'document' in msg:
        media_type = 'animation'
        media_id = msg['document']['file_id']
    caption_entities = []
    if 'caption_entities' in msg:
        for entity in msg['caption_entities']:
            caption_entities.append(entity)
    caption = msg['caption'] if 'caption' in msg else ''
    cache_posts[str(msg['forward_from_message_id'])] = {media_type: media_id, 'caption': caption, 'caption_entities': caption_entities}

def ask_publisher(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    answer = "Divulgar postagem?" if language == "pt" else "Share post?"
    send_message(cookiebot, chat_id, answer, msg_to_reply=msg, 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data=f"SendToApprovalPub {msg['forward_from_chat']['id']} {chat_id} {msg['forward_from_message_id']} {msg['message_id']}")],
            [InlineKeyboardButton(text="❌",callback_data='nPub')]
        ]
    ))
    add_post_to_cache(msg)

def ask_publisher_command(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    if not 'reply_to_message' in msg:
        text = "Você precisa responder a uma mensagem com o comando para eu poder divulgar ela!" if language == "pt" else "¡Debes responder un mensaje con el comando para que pueda compartirlo!" if language == "es" else "You need to reply to a message with the command for me to be able to share it!"
        send_message(cookiebot, chat_id, text, msg_to_reply=msg)
        return
    if 'forward_from_chat' not in msg['reply_to_message'] or 'forward_from_message_id' not in msg['reply_to_message']:
        text = "Essa mensagem não é de um canal!" if language == "pt" else "¡Este mensaje no es de un canal!" if language == "es" else "This message is not from a channel!"
        send_message(cookiebot, chat_id, text, msg_to_reply=msg)
        return
    if 'caption' not in msg['reply_to_message']:
        text = "O anúncio precisa ter uma foto, vídeo ou GIF" if language == "pt" else "¡El anuncio necesita tener una foto, vídeo o GIF!" if language == "es" else "This ad needs to have a photo, video or GIF"
        send_message(cookiebot, chat_id, text, msg_to_reply=msg)
        return
    replied_post = msg['reply_to_message']
    add_post_to_cache(replied_post)
    ask_approval(cookiebot, f"SendToApprovalPub {replied_post['forward_from_chat']['id']} {chat_id} {replied_post['forward_from_message_id']} {replied_post['message_id']}", msg['from']['id'])
    text = "Post enviado para aprovação, aguarde" if language == "pt" else "Publicación enviada para aprobación, por favor espere" if language == "es" else "Post sent for approval, please wait"
    send_message(cookiebot, chat_id, text, msg_to_reply=msg)

def ask_approval(cookiebot, query_data, from_id, is_alternate_bot=0):
    origin_chatid = query_data.split()[1]
    second_chatid = query_data.split()[2]
    origin_messageid = query_data.split()[3]
    second_messageid = query_data.split()[4]
    origin_userid = from_id
    forward_message(cookiebot, APPROVAL_CHAT_ID, second_chatid, second_messageid, is_alternate_bot=is_alternate_bot)
    send_message(cookiebot, APPROVAL_CHAT_ID, 'Approve post?', 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️ 7 days (NSFW)",callback_data=f'yPub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 7 {second_messageid} 1')],
            [InlineKeyboardButton(text="✔️ 7 days",callback_data=f'yPub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 7 {second_messageid} 0')],
            [InlineKeyboardButton(text="✔️ 3 days",callback_data=f'yPub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 3 {second_messageid} 0')],
            [InlineKeyboardButton(text="✔️ 1 day",callback_data=f'yPub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 1 {second_messageid} 0')],
            [InlineKeyboardButton(text="❌",callback_data=f'nPub {origin_messageid}')]
        ]
    ))

def create_job(hour, minute, name, days, target_chat_id, postmail_chat_id, second_chatid, postmail_message_id, second_messageid, origin_userid):
    current_time = datetime.datetime.now()
    next_time = str(datetime.datetime(current_time.year, current_time.month, current_time.day, hour, minute) + datetime.timedelta(days=1))
    publisher_cursor.execute("INSERT INTO publisher VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, days, next_time, target_chat_id, postmail_chat_id, second_chatid, postmail_message_id, second_messageid, origin_userid))
    publisher_db.commit()
    return name

def list_jobs():
    publisher_cursor.execute("SELECT * FROM publisher")
    jobs = []
    for row in publisher_cursor.fetchall():
        job = {
            'name': row[0],
            'days': row[1],
            'next_time': row[2],
            'target_chat_id': row[3],
            'postmail_chat_id': row[4],
            'second_chatid': row[5],
            'postmail_message_id': row[6],
            'second_messageid': row[7],
            'origin_userid': row[8]
        }
        jobs.append(job)
    return jobs

def delete_job(job_name):
    publisher_cursor.execute("DELETE FROM publisher WHERE name = ?", (job_name,))
    publisher_db.commit()
    return job_name

def edit_job_data(job_name, param, value):
    publisher_cursor.execute(f"UPDATE publisher SET {param} = ? WHERE name = ?", (value, job_name))
    publisher_db.commit()
    return job_name

def convert_prices_in_text(text, code_target):
    if (code_target == 'BRL') and any([x in text for x in ('R$', 'BRL', 'Reais', 'reais')]):
        return text
    final_text = ''
    text = text.replace('Reais', 'R$').replace('reais', 'R$')
    for paragraph in text.split('\n'):
        amount = 0
        currency = None
        for word in paragraph.split():
            parsed = Price.fromstring(word, currency_hint='usd')
            if parsed.amount is not None and parsed.amount_float > amount:
                amount = parsed.amount_float
            if parsed.currency is not None:
                currency = parsed.currency
        if amount == 0 or currency is None:
            final_text += f"{paragraph}\n"
            continue
        if currency in ('$', 'US$', 'USD', 'U$'):
            code_from = 'USD'
        elif currency in ('€', 'EUR'):
            code_from = 'EUR'
        elif currency in ('£', 'GBP'):
            code_from = 'GBP'
        elif currency in ('R$', 'BRL'):
            code_from = 'BRL'
        elif currency in ('¥', 'JPY'):
            code_from = 'JPY'
        elif currency in ('C$', 'CAD'):
            code_from = 'CAD'
        elif currency in ('A$', 'AUD'):
            code_from = 'AUD'
        elif currency in ('ARS'):
            code_from = 'ARS'
        else:
            code_from = currency
        if code_from == code_target:
            return text
        try:
            rate_url = f"https://v6.exchangerate-api.com/v6/{exchangerate_key}/latest/{code_from}"
            rate = json.loads(requests.get(rate_url, timeout=10).text)['conversion_rates'][code_target]
            converted = round(amount * rate, 2)
            final_text += f"{paragraph} ({code_target} ≈{converted})\n"
        except Exception:
            final_text += f"{paragraph}\n"
    return final_text

def remove_emojis_from_ends(input_string):
    while EMOJI_PATTERN.match(input_string):
        input_string = input_string[1:]
    while EMOJI_PATTERN.match(input_string[::-1]):
        input_string = input_string[:-1]
    return input_string

def prepare_post(cookiebot, origin_messageid, origin_chat, origin_user):
    cached_post = cache_posts[origin_messageid]
    inline_keyboard = []
    inline_keyboard.append([InlineKeyboardButton(text=origin_chat['title'], url=f"https://t.me/{origin_chat['username']}")])
    for url in set(re.findall(URL_REGEX, cached_post['caption'])):
        name = url.rstrip('/').split('/')[-1].replace('www.', '')
        url_no_emojis_on_ends = remove_emojis_from_ends(url)
        if len(name) and len(url_no_emojis_on_ends) > 3 and url_no_emojis_on_ends != f"https://t.me/{origin_chat['username']}":
            inline_keyboard.append([InlineKeyboardButton(text=name, url=url_no_emojis_on_ends, parse_mode='HTML')])
            cached_post['caption'] = cached_post['caption'].replace(url, url_no_emojis_on_ends)
    caption_new = emojis_to_numbers(cached_post['caption'])
    for entity in cached_post['caption_entities']:
        if 'url' in entity and len(entity['url']) > 3 and len(inline_keyboard) < 5:
            name = entity['url'].rstrip('/').replace('www.', '').replace('http://', '').replace('https://', '')
            inline_keyboard.append([InlineKeyboardButton(text=name, url=entity['url'])])
    if origin_user is not None and 'Mekhy' not in origin_user['first_name']:
        inline_keyboard.append([InlineKeyboardButton(text=origin_user['first_name'], url=f"https://t.me/{origin_user['username']}")])
    inline_keyboard.append([InlineKeyboardButton(text="Mural 📬", url=POSTMAIL_CHAT_LINK)])
    caption_pt = translate(caption_new, 'pt')
    caption_en = translate(caption_new, 'en')
    caption_pt = convert_prices_in_text(caption_pt, 'BRL').replace('<', '⩽').replace('>', '⩾').replace('&', '＆')
    caption_en = convert_prices_in_text(caption_en, 'USD').replace('<', '⩽').replace('>', '⩾').replace('&', '＆')
    caption_pt = caption_pt[:1020]
    caption_en = caption_en[:1020]
    if 'Error 500 (Server Error)' in caption_pt:
        caption_pt = caption_new
    if 'Error 500 (Server Error)' in caption_en:
        caption_en = caption_new
    if 'photo' in cached_post:
        sent_pt = cookiebot.sendPhoto(chat_id=POSTMAIL_CHAT_ID, photo=cached_post['photo'], caption=caption_pt, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard), parse_mode='HTML')['message_id']
        sent_en = cookiebot.sendPhoto(chat_id=POSTMAIL_CHAT_ID, photo=cached_post['photo'], caption=caption_en, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard), parse_mode='HTML')['message_id']
    elif 'video' in cached_post:
        sent_pt = cookiebot.sendVideo(chat_id=POSTMAIL_CHAT_ID, video=cached_post['video'], caption=caption_pt, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))['message_id']
        sent_en = cookiebot.sendVideo(chat_id=POSTMAIL_CHAT_ID, video=cached_post['video'], caption=caption_en, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))['message_id']
    elif 'animation' in cached_post:
        sent_pt = cookiebot.sendAnimation(chat_id=POSTMAIL_CHAT_ID, animation=cached_post['animation'], caption=caption_pt, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))['message_id']
        sent_en = cookiebot.sendAnimation(chat_id=POSTMAIL_CHAT_ID, animation=cached_post['animation'], caption=caption_en, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))['message_id']
    if origin_messageid in cache_posts:
        cache_posts.pop(origin_messageid)
    return sent_pt, sent_en

def deny_post(query_data):
    if len(query_data.split()) < 2:
        return
    origin_messageid = query_data.split()[1]
    if origin_messageid in cache_posts:
        cache_posts.pop(origin_messageid)

def schedule_post(cookiebot, query_data):
    _, origin_chatid, second_chatid, origin_messageid, origin_userid, days, second_messageid, has_nsfw = query_data.split()[:8]
    origin_chat = cookiebot.getChat(origin_chatid)
    try:
        origin_user = cookiebot.getChatMember(origin_chatid, origin_userid)['user']
    except Exception:
        origin_user = None
    sent_pt, sent_en = prepare_post(cookiebot, origin_messageid, origin_chat, origin_user)
    jobs = list_jobs()
    for job in jobs.copy():
        if job['name'].split('-->')[0].strip() == origin_chat['title'].strip():
            delete_job(job['name'])
            jobs.remove(job)
    answer = f"Post set for the following times ({days} days):\nNOW - Cookiebot Mural 📬\n"
    for group in get_request_backend('registers'):
        try:
            _, sfw, _, _, _, _, _, language, publisherpost, _, _, max_posts, publisher_members_only = get_config(cookiebot, group['id'])
        except TypeError:
            continue
        if (not publisherpost) or (has_nsfw == '1' and sfw):
            continue
        if publisher_members_only:
            members = get_members_chat(cookiebot, group['id'])
            if origin_user is None or origin_user['username'] not in str(members):
                continue
        try:
            num_posts_for_group = 0
            target_chattitle = cookiebot.getChat(group['id'])['title']
            for job in jobs.copy():
                if f"--> {target_chattitle}" in job['name']:
                    num_posts_for_group += 1
                if max_posts is not None and num_posts_for_group > max_posts:
                    delete_job(job['name'])
                    jobs.remove(job)
                    num_posts_for_group -= 1
            hour = random.randint(0,23)
            minute = random.randint(0,59)
            postmail_message_id = sent_pt if language == 'pt' else sent_en
            create_job(hour, minute, f"{origin_chat['title']} --> {target_chattitle}, at {hour}:{minute}", int(days), int(group['id']),
                       int(POSTMAIL_CHAT_ID), int(second_chatid), int(postmail_message_id), int(second_messageid), int(origin_userid))
            print(f"CREATED JOB {hour}:{minute} - {target_chattitle}")
            answer += f"{hour}:{minute} - {target_chattitle}\n"
        except Exception as e:
            pass
    try:
        answer += "OBS: private chats are not listed!"
        send_message(cookiebot, ownerID, answer)
        send_message(cookiebot, origin_userid, answer)
        text = "Post added to the publication queue!"
        send_message(cookiebot, second_chatid, text, msg_to_reply={'message_id': second_messageid})
    except Exception:
        send_message(cookiebot, ownerID, traceback.format_exc())
        text = "Post added to the publication queue, but I was unable to send you the times.\n<blockquote> Send /start in my DM so I can send you messages. </blockquote>"
        send_message(cookiebot, second_chatid, text, msg_to_reply={'message_id': second_messageid})

def schedule_autopost(cookiebot, msg, chat_id, language, listaadmins_id, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if str(msg['from']['id']) not in listaadmins_id and int(msg['from']['id']) != ownerID and 'sender_chat' not in msg:
        text = "Você não é um administrador do grupo!" if language == "pt" else "¡No eres un administrador del grupo!" if language == "es" else "You are not a group admin!"
        send_message(cookiebot, chat_id, text, msg_to_reply=msg)
        return
    if 'reply_to_message' not in msg:
        text = "Você precisa responder a uma mensagem com o comando para eu poder repostar ela nesse grupo!" if language == "pt" else "¡Debes responder un mensaje con el comando para que pueda compartirlo en este grupo!" if language == "es" else "You need to reply to a message with the command for me to be able to repost it in this group!"
        send_message(cookiebot, chat_id, text, msg_to_reply=msg)
        return
    if len(msg['text'].split()) > 1:
        if not msg['text'].split()[1].isnumeric():
            text = "Você precisa colocar um número de dias válido!" if language == "pt" else "¡Debes poner un número de días válido!" if language == "es" else "You need to put a valid number of days!"
            send_message(cookiebot, chat_id, text, msg_to_reply=msg)
            return
        days = msg['text'].split()[1]
        text = f"Repostagem programada para o grupo por {days} dias!" if language == "pt" else f"¡Reposteo programado para el grupo por {days} días!" if language == "es" else f"Repost scheduled for the group for {days} days!"
    else:
        days = 9999
        text = "Repostagem programada para o grupo! (sem limite de dias)" if language == "pt" else "¡Reposteo programado para el grupo! (sin límite de días)" if language == "es" else "Repost scheduled for the group! (no limit of days)"
    original_msg_id = msg['reply_to_message']['message_id']
    chat = cookiebot.getChat(chat_id)
    hour = random.randint(10,17)
    minute = random.randint(0,59)
    create_job(hour, minute, f"{chat['title']} --> {chat['title']}, at {hour}:{minute} ", int(days), int(chat_id), int(chat_id), int(chat_id), int(original_msg_id), int(original_msg_id), int(msg['from']['id']))
    react_to_message(msg, '👍', is_alternate_bot=is_alternate_bot)
    send_message(cookiebot, chat_id, text, msg_to_reply=msg, parse_mode='HTML')

def cancel_posts(cookiebot, msg, chat_id, language, listaadmins_id, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if str(msg['from']['id']) not in listaadmins_id and 'sender_chat' not in msg:
        text = "Você não é um administrador do grupo!" if language == "pt" else "¡No eres un administrador del grupo!" if language == "es" else "You are not a group admin!"
        send_message(cookiebot, chat_id, text, msg_to_reply=msg)
        return
    for job in list_jobs():
        if str(job['second_chatid']) == str(chat_id):
            delete_job(job['name'])
    react_to_message(msg, '👍', is_alternate_bot=is_alternate_bot)
    text = "Posts e reposts do grupo cancelados!" if language == "pt" else "¡Publicaciones y reenvíos del grupo cancelados!" if language == "es" else "Posts and reposts canceled!"
    send_message(cookiebot, chat_id, text, msg_to_reply=msg)

def scheduler_pull(cookiebot, is_alternate_bot=0):
    current_time = datetime.datetime.now()
    current_time = datetime.datetime(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
    for job in list_jobs():
        if current_time < datetime.datetime.strptime(job['next_time'], '%Y-%m-%d %H:%M:%S'):
            continue
        if job['days'] <= 1:
            delete_job(job['name'])
        else:
            edit_job_data(job['name'], 'days', job['days'] - 1)
            edit_job_data(job['name'], 'next_time', str(current_time + datetime.timedelta(days=1)))
        try:
            group_id = str(job['target_chat_id'])
            config = get_config(cookiebot, group_id)
            if not config[8]:
                delete_job(job['name'])
                continue
            origin_messageid = str(job['postmail_message_id'])
            target_chat = cookiebot.getChat(group_id)
            if 'is_forum' in target_chat and target_chat['is_forum']:
                forward_message(cookiebot, group_id, POSTMAIL_CHAT_ID, origin_messageid, thread_id=int(config[10]), is_alternate_bot=is_alternate_bot)
            else:
                forward_message(cookiebot, group_id, POSTMAIL_CHAT_ID, origin_messageid, is_alternate_bot=is_alternate_bot)
        except telepot.exception.BotWasKickedError:
            delete_job(job['name'])
            continue
        except Exception:
            send_message(cookiebot, ownerID, traceback.format_exc())
            delete_job(job['name'])

def check_notify_post_reply(cookiebot, msg, chat_id, language):
    for job in list_jobs():
        if job['name'].startswith(msg['reply_to_message']['reply_markup']['inline_keyboard'][0][0]['text']):
            second_chatid = str(job['second_chatid'])
            second_messageid = str(job['second_messageid'])
            text = f"@{msg['from']['username']}" if 'username' in msg['from'] else f"{msg['from']['first_name']} {msg['from']['last_name']}"
            text += f" replied:\n'{msg['text']}'\n\nIn chat {msg['chat']['title']}"
            send_message(cookiebot, second_chatid, text, msg_to_reply={'message_id': second_messageid})
            text = "Resposta enviada ao dono do post!" if language == "pt" else "¡Respuesta enviada al dueño del post!" if language == "es" else "Reply sent to the owner of the post!"
            send_message(cookiebot, chat_id, text, msg_to_reply=msg)
            return

