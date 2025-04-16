import os
import time
import re
import traceback
import json
import urllib3
from urllib.parse import quote
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from functools import wraps
import threading
import telepot
from telepot.exception import TelegramError
from google.cloud import storage
from google.cloud import translate_v2
load_dotenv('../.env')
login_backend, password_backend = os.getenv('backend_login'), os.getenv('backend_password')
googleAPIkey, searchEngineCX, exchangerate_key, openai_key, saucenao_key, spamwatch_token = os.getenv('googleAPIkey'), os.getenv('searchEngineCX'), os.getenv('exchangerate_key'), os.getenv('openai_key'), os.getenv('saucenao_key'), os.getenv('spamwatch_token')
cookiebotTOKEN, bombotTOKEN, pawstralbotTOKEN, tarinbotTOKEN, connectbotTOKEN = os.getenv('cookiebotTOKEN'), os.getenv('bombotTOKEN'), os.getenv('pawstralbotTOKEN'), os.getenv('tarinbotTOKEN'), os.getenv('connectbotTOKEN')
ownerID = int(os.getenv('ownerID'))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../cookiebot-bucket-key.json'
storage_client = storage.Client()
translate_client = translate_v2.Client()
storage_bucket = storage_client.get_bucket("cookiebot-bucket")
storage_bucket_public = storage_client.get_bucket("cookiebot-bucket-public")

def get_bot_token(is_alternate_bot):
    match is_alternate_bot:
        case 0:
            return cookiebotTOKEN
        case 1:
            return bombotTOKEN
        case 2:
            return pawstralbotTOKEN
        case 3:
            return tarinbotTOKEN
        case 4:
            return connectbotTOKEN
        case _:
            return None
        
def cached_api_call(ttl_seconds):
    cache = {}
    cache_lock = threading.RLock()
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            with cache_lock:
                if key in cache:
                    result, timestamp = cache[key]
                    if time.time() - timestamp < ttl_seconds:
                        return result
            result = func(*args, **kwargs)
            with cache_lock:
                cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator

@cached_api_call(ttl_seconds=60)
def get_request_backend(route, params=None):
    try:
        response = requests.get(f'https://backend.cookiebotfur.net/{route}', json=params,
                            auth = HTTPBasicAuth(login_backend, password_backend),
                            verify=False, timeout=60)
        return json.loads(response.text) if len(response.text) else ''
    except Exception as e:
        print(e)
        return str(e)

@cached_api_call(ttl_seconds=60)
def post_request_backend(route, params=None):
    try:
        response = requests.post(f'https://backend.cookiebotfur.net/{route}', json=params,
                             auth = HTTPBasicAuth(login_backend, password_backend),
                             verify=False, timeout=60)
        return json.loads(response.text) if len(response.text) else ''
    except Exception as e:
        print(e)
        return str(e)

@cached_api_call(ttl_seconds=60)
def put_request_backend(route, params=None):
    try:
        response = requests.put(f'https://backend.cookiebotfur.net/{route}', json=params,
                            auth = HTTPBasicAuth(login_backend, password_backend),
                            verify=False, timeout=60)
        return json.loads(response.text) if len(response.text) else ''
    except Exception as e:
        print(e)
        return str(e)

@cached_api_call(ttl_seconds=60)
def delete_request_backend(route, params=None):
    try:
        response = requests.delete(f'https://backend.cookiebotfur.net/{route}', json=params,
                               auth = HTTPBasicAuth(login_backend, password_backend),
                               verify=False, timeout=60)
        return json.loads(response.text) if len(response.text) else ''
    except Exception as e:
        print(e)
        return str(e)
    
def translate(text, dest='en'):
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    tags = {}
    count = 0
    def replace_tag(match):
        nonlocal count
        placeholder = f" htmltag{count} "
        tags[placeholder] = match.group(0)
        count += 1
        return placeholder
    newline_token = " NEWLINE_TOKEN_XYZ "
    newline_token_alts = ["NEWLINE_TOKEN_XYZ", "NEWLINE_XYZ_XYZ", "newline_xyz", "token_xyz", "_TOKEN_TOKKN_XYZ", "NEWLINE_TOKN_XYZ", "newline_xyz_token_xyz_xyz", "newloken_token_xyz", "_xyz", "newlina_TOKEN_XYZ"]
    text_with_placeholders = re.sub(r'<[^>]*>', replace_tag, text)
    text_with_tokens = text_with_placeholders.replace('\n', newline_token)
    translated = translate_client.translate(text_with_tokens, target_language=dest[:2])["translatedText"]
    translated = html.unescape(translated)
    for placeholder, tag in tags.items():
        translated = re.sub(re.escape(placeholder.strip()), tag, translated, flags=re.IGNORECASE)
    for token in newline_token_alts:
        padded_token = f" {token} "
        translated = re.sub(re.escape(padded_token.strip()), '\n', translated, flags=re.IGNORECASE)
        translated = re.sub(re.escape(token), '\n', translated, flags=re.IGNORECASE)
    translated = translated.replace('R $', 'R$')
    return translated

def send_chat_action(cookiebot, chat_id, action):
    try:
        cookiebot.sendChatAction(chat_id, action)
    except urllib3.exceptions.ProtocolError:
        cookiebot.sendChatAction(chat_id, action)

def get_media_content(cookiebot, msg, media_type, is_alternate_bot=0, downloadfile=False):
    token = get_bot_token(is_alternate_bot)
    try:
        try:
            file_path_telegram = cookiebot.getFile(msg[media_type]['file_id'])['file_path']
        except TypeError:
            file_path_telegram = cookiebot.getFile(msg[media_type][-1]['file_id'])['file_path']
        url = f"https://api.telegram.org/file/bot{token}/{file_path_telegram}"
        r = requests.get(url, allow_redirects=True, timeout=60)
        if not downloadfile:
            return r.content
        filename = file_path_telegram.split('/')[-1]
        with open(filename, 'wb') as f:
            f.write(r.content)
        return filename
    except urllib3.exceptions.ProtocolError:
        get_media_content(cookiebot, msg, is_alternate_bot, downloadfile)

def send_error_traceback(cookiebot, msg, traceback_text):
    if msg:
        cookiebot.sendMessage(ownerID, str(msg))
    if traceback_text:
        chunk_size = 4000
        for i in range(0, len(traceback_text), chunk_size):
            chunk = traceback_text[i:i + chunk_size]
            cookiebot.sendMessage(ownerID, chunk)

def send_message(cookiebot, chat_id, text, msg_to_reply=None, language="pt", thread_id=None, is_alternate_bot=0, reply_markup=None, link_preview_options=None, disable_notification=False, parse_mode='HTML'):
    try:
        if language in ['eng', 'es']:
            text = translate(text, language)
        if msg_to_reply and link_preview_options:
            url = f"https://api.telegram.org/bot{get_bot_token(is_alternate_bot)}/sendMessage"
            params = {'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup, 'link_preview_options': link_preview_options, 'disable_notification': disable_notification, 'parse_mode': parse_mode}
            full_url = f"{url}?" + "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
            if reply_markup is None:
                full_url = full_url.replace('&reply_markup=None', '')
            requests.get(full_url, timeout=5)
        elif msg_to_reply:
            try:
                return cookiebot.sendMessage(chat_id, text, reply_to_message_id=msg_to_reply['message_id'], reply_markup=reply_markup, disable_notification=disable_notification, parse_mode=parse_mode)
            except telepot.exception.TelegramError:
                return cookiebot.sendMessage(chat_id, text.replace('\\', '').replace('>', ''), reply_to_message_id=msg_to_reply['message_id'], disable_notification=disable_notification, reply_markup=reply_markup)
        elif thread_id is not None:
            url = f"https://api.telegram.org/bot{get_bot_token(is_alternate_bot)}/sendMessage?chat_id={chat_id}&text={text}&message_thread_id={thread_id}&reply_markup={reply_markup}&disable_notification={disable_notification}&parse_mode={parse_mode}"
            if reply_markup is None:
                url = url.replace('&reply_markup=None', '')
            requests.get(url, timeout=5)
        else:
            try:
                return cookiebot.sendMessage(chat_id, text, reply_markup=reply_markup, disable_notification=disable_notification, parse_mode=parse_mode)
            except telepot.exception.TelegramError:
                return cookiebot.sendMessage(chat_id, text.replace('\\', '').replace('>', ''), disable_notification=disable_notification, reply_markup=reply_markup)
    except urllib3.exceptions.ProtocolError:
        send_message(cookiebot, chat_id, text, msg_to_reply, language, thread_id, is_alternate_bot, reply_markup, link_preview_options, disable_notification, parse_mode)
    except Exception:
        traceback_text = traceback.format_exc()
        if not 'Bad Request: PEER_ID_INVALID' in traceback_text:
            send_error_traceback(cookiebot, None, traceback_text)

def send_photo(cookiebot, chat_id, photo, caption=None, msg_to_reply=None, language="pt", thread_id=None, is_alternate_bot=0, reply_markup=None, parse_mode='HTML'):
    try:
        if language in ['eng', 'es']:
            caption = translate(caption, language) if caption else None
        if len(caption) > 1024:
            caption = caption[:1018] + '(...)'
        if thread_id is not None:
            token = get_bot_token(is_alternate_bot)
            url = f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}&photo={photo}&caption={caption}&message_thread_id={thread_id}&reply_markup={reply_markup}"
            if reply_markup is None:
                url = url.replace('&reply_markup=None', '')
            response = requests.get(url, timeout=60)
            sentphoto = {'message_id': json.loads(response.text)['result']['message_id']}
        else:
            reply_to_message_id = msg_to_reply['message_id'] if msg_to_reply else None
            if reply_markup is None:
                sentphoto = cookiebot.sendPhoto(chat_id, photo, caption=caption, 
                            reply_to_message_id=reply_to_message_id, parse_mode=parse_mode)
            else:
                sentphoto = cookiebot.sendPhoto(chat_id, photo, caption=caption, 
                            reply_to_message_id=reply_to_message_id, 
                            reply_markup=reply_markup, parse_mode=parse_mode)
    except urllib3.exceptions.ProtocolError:
        return send_photo(cookiebot, chat_id, photo, caption, 
                          msg_to_reply, language, thread_id, is_alternate_bot, reply_markup)
    except TelegramError:
        send_error_traceback(cookiebot, None, traceback.format_exc())
        return None
    return sentphoto['message_id']

def send_animation(cookiebot, chat_id, animation, caption=None, msg_to_reply=None, language="pt", thread_id=None, is_alternate_bot=0, reply_markup=None, parse_mode='HTML'):
    try:
        if language in ['eng', 'es']:
            caption = translate(caption, language) if caption else None
        if thread_id is not None:
            token = get_bot_token(is_alternate_bot)
            url = f"https://api.telegram.org/bot{token}/sendAnimation?chat_id={chat_id}&animation={animation}&caption={caption}&message_thread_id={thread_id}&reply_markup={reply_markup}"
            if reply_markup is None:
                url = url.replace('&reply_markup=None', '')
            response = requests.get(url)
            sentanimation = {'message_id': json.loads(response.text)['result']['message_id']}
        else:
            reply_to_message_id = msg_to_reply['message_id'] if msg_to_reply else None
            if reply_markup is None:
                sentanimation = cookiebot.sendAnimation(chat_id, animation, caption=caption, 
                                reply_to_message_id=reply_to_message_id, parse_mode=parse_mode)
            else:
                sentanimation = cookiebot.sendAnimation(chat_id, animation, caption=caption, 
                                reply_to_message_id=reply_to_message_id, 
                                reply_markup=reply_markup, parse_mode=parse_mode)
    except urllib3.exceptions.ProtocolError:
        return send_animation(cookiebot, chat_id, animation, caption, 
                              msg_to_reply, language, thread_id, is_alternate_bot, reply_markup)
    except TelegramError:
        send_error_traceback(cookiebot, None, traceback.format_exc())
        return None
    return sentanimation['message_id']

def set_bot_commands(cookiebot, commands, scope_chat_id, is_alternate_bot=0, language="pt"):
    token = get_bot_token(is_alternate_bot)
    url = f'https://api.telegram.org/bot{token}/setMyCommands'
    data = {'commands': commands,
            'scope': {'type': 'chat', 'chat_id': scope_chat_id},
            'language_code': language[0:2].lower()}
    r = requests.get(url, json=data, timeout=60)
    return r.text

def forward_message(cookiebot, chat_id, from_chat_id, message_id, thread_id=None, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    token = get_bot_token(is_alternate_bot)
    if thread_id:
        url_req = f"https://api.telegram.org/bot{token}/forwardMessage?chat_id={chat_id}&from_chat_id={from_chat_id}&message_id={message_id}&message_thread_id={thread_id}"
        requests.get(url_req, timeout=60)
    else:
        cookiebot.forwardMessage(chat_id, from_chat_id, message_id)

def react_to_message(msg, emoji, is_big=True, is_alternate_bot=0):
    token = get_bot_token(is_alternate_bot)
    reaction = [{'type': 'emoji', 'emoji': emoji}]
    reaction_json = json.dumps(reaction)
    url = f'https://api.telegram.org/bot{token}/setMessageReaction?chat_id={msg["chat"]["id"]}&message_id={msg["message_id"]}&reaction={reaction_json}&is_big={is_big}'
    requests.get(url, timeout=60)

def blacklist_user(user_id):
    id = str(user_id).replace('@', '')
    post_request_backend(f'blacklist/{id}')

def unblacklist_user(user_id):
    id = str(user_id).replace('@', '')
    delete_request_backend(f'blacklist/{id}')

def ban_and_blacklist(cookiebot, chat_id, user_id):
    id = str(user_id).replace('@', '')
    post_request_backend(f'blacklist/{id}')
    cookiebot.kickChatMember(chat_id, user_id)

def leave_and_blacklist(cookiebot, chat_id):
    id = str(chat_id).replace('@', '')
    post_request_backend(f'blacklist/{id}')
    delete_request_backend(f'registers/{chat_id}')
    delete_request_backend(f'configs/{chat_id}')
    delete_request_backend(f'groups/{chat_id}')
    try:
        cookiebot.leaveChat(chat_id)
    except Exception as e:
        print("Error leaving chat: " + str(e))

def wait_open(filename):
    if os.path.exists(filename):
        try:
            text = open(filename, 'r', encoding='utf-8')
            text.close()
        except IOError:
            time.sleep(1)

def delete_message(cookiebot, identifier):
    try:
        cookiebot.deleteMessage(identifier)
    except Exception as e:
        print(e)

def check_if_string_in_file(file_name, string_to_search):
    for line in file_name:
        if string_to_search in line:
            return True
    return False

def number_to_emojis(number):
    emojis = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
              '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'}
    emojis_string = ''
    for digit in str(number):
        emojis_string += emojis[digit]
    return emojis_string

def emojis_to_numbers(text):
    numbers = {'0️⃣': '0', '1️⃣': '1', '2️⃣': '2', '3️⃣': '3', '4️⃣': '4',
               '5️⃣': '5', '6️⃣': '6', '7️⃣': '7', '8️⃣': '8', '9️⃣': '9'}
    pattern = re.compile('|'.join(map(re.escape, numbers.keys())))
    return pattern.sub(lambda x: numbers[x.group()], text)
