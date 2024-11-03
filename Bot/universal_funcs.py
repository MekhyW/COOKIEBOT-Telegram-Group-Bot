import os
import time
import re
import traceback
import json
import urllib3
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import telepot
from telepot.exception import TelegramError
from deep_translator import GoogleTranslator
from google.cloud import storage
load_dotenv('../.env')
login_backend, password_backend, serverIP = os.getenv('backend_login'), os.getenv('backend_password'), os.getenv('backend_serverIP')
googleAPIkey, searchEngineCX, exchangerate_key, openai_key, saucenao_key, spamwatch_token = os.getenv('googleAPIkey'), os.getenv('searchEngineCX'), os.getenv('exchangerate_key'), os.getenv('openai_key'), os.getenv('saucenao_key'), os.getenv('spamwatch_token')
cookiebotTOKEN, bombotTOKEN, pawstralbotTOKEN, tarinbotTOKEN, connectbotTOKEN = os.getenv('cookiebotTOKEN'), os.getenv('bombotTOKEN'), os.getenv('pawstralbotTOKEN'), os.getenv('tarinbotTOKEN'), os.getenv('connectbotTOKEN')
ownerID = int(os.getenv('ownerID'))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../cookiebot-bucket-key.json'
storage_client = storage.Client()
storage_bucket = storage_client.get_bucket(os.getenv('bucket_name'))

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

def get_request_backend(route, params=None):
    response = requests.get(f'{serverIP}/{route}', json=params,
                            auth = HTTPBasicAuth(login_backend, password_backend),
                            verify=False, timeout=60)
    try:
        if len(response.text):
            return json.loads(response.text)
        else:
            return ''
    except Exception as e:
        print(e)
        return ''

def post_request_backend(route, params=None):
    response = requests.post(f'{serverIP}/{route}', json=params,
                             auth = HTTPBasicAuth(login_backend, password_backend),
                             verify=False, timeout=60)
    try:
        if len(response.text):
            print("POST: ", response.text)
            return json.loads(response.text)
        else:
            return ''
    except Exception as e:
        print(e)
        return ''

def put_request_backend(route, params=None):
    response = requests.put(f'{serverIP}/{route}', json=params,
                            auth = HTTPBasicAuth(login_backend, password_backend),
                            verify=False, timeout=60)
    try:
        if len(response.text):
            print("PUT: ", response.text)
            return json.loads(response.text)
        else:
            return ''
    except Exception as e:
        print(e)
        return ''

def delete_request_backend(route, params=None):
    response = requests.delete(f'{serverIP}/{route}', json=params,
                               auth = HTTPBasicAuth(login_backend, password_backend),
                               verify=False, timeout=60)
    try:
        if len(response.text):
            print("DELETE: ", response.text)
            return json.loads(response.text)
        else:
            return ''
    except Exception as e:
        print(e)
        return ''

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
        r = requests.get(url, allow_redirects=True, timeout=10)
        if not downloadfile:
            return r.content
        filename = file_path_telegram.split('/')[-1]
        with open(filename, 'wb') as f:
            f.write(r.content)
        return filename
    except urllib3.exceptions.ProtocolError:
        get_media_content(cookiebot, msg, is_alternate_bot, downloadfile)

def send_message(cookiebot, chat_id, text, msg_to_reply=None, language="pt", thread_id=None, is_alternate_bot=0, reply_markup=None, parse_mode='HTML'):
    try:
        send_chat_action(cookiebot, chat_id, 'typing')
        if language == 'eng':
            text = GoogleTranslator(source='auto', target='en').translate(text)
        elif language == 'es':
            text = GoogleTranslator(source='auto', target='es').translate(text)
        if msg_to_reply:
            reply_id = msg_to_reply['message_id']
            try:
                cookiebot.sendMessage(chat_id, text, reply_to_message_id=reply_id, 
                                      reply_markup=reply_markup, parse_mode=parse_mode)
            except telepot.exception.TelegramError:
                text = text.replace('\\', '').replace('>', '')
                cookiebot.sendMessage(chat_id, text, reply_to_message_id=reply_id, 
                                      reply_markup=reply_markup)
        elif thread_id is not None:
            token = get_bot_token(is_alternate_bot)
            url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}&message_thread_id={thread_id}&reply_markup={reply_markup}&parse_mode={parse_mode}"
            if reply_markup is None:
                url = url.replace('&reply_markup=None', '')
            requests.get(url, timeout=10)
        else:
            try:
                cookiebot.sendMessage(chat_id, text, reply_markup=reply_markup, 
                                      parse_mode=parse_mode)
            except telepot.exception.TelegramError:
                text = text.replace('\\', '').replace('>', '')
                cookiebot.sendMessage(chat_id, text, reply_markup=reply_markup)
    except urllib3.exceptions.ProtocolError:
        print(traceback.format_exc())
        send_message(cookiebot, chat_id, text, msg_to_reply, language, 
                     thread_id, is_alternate_bot, reply_markup, parse_mode)
    except TelegramError:
        print(traceback.format_exc())
        try:
            cookiebot.sendMessage(ownerID, traceback.format_exc())
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

def send_photo(cookiebot, chat_id, photo, caption=None, msg_to_reply=None, language="pt", thread_id=None, is_alternate_bot=0, reply_markup=None):
    try:
        send_chat_action(cookiebot, chat_id, 'upload_photo')
        if language in ['eng', 'es']:
            caption = GoogleTranslator(source='auto', target=language[:2]).translate(caption) if caption else None
        if thread_id is not None:
            token = get_bot_token(is_alternate_bot)
            url = f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}&photo={photo}&caption={caption}&message_thread_id={thread_id}&reply_markup={reply_markup}"
            if reply_markup is None:
                url = url.replace('&reply_markup=None', '')
            response = requests.get(url, timeout=10)
            sentphoto = {'message_id': json.loads(response.text)['result']['message_id']}
        else:
            reply_to_message_id = msg_to_reply['message_id'] if msg_to_reply else None
            if reply_markup is None:
                sentphoto = cookiebot.sendPhoto(chat_id, photo, caption=caption, 
                            reply_to_message_id=reply_to_message_id, parse_mode='HTML')
            else:
                sentphoto = cookiebot.sendPhoto(chat_id, photo, caption=caption, 
                            reply_to_message_id=reply_to_message_id, 
                            reply_markup=reply_markup, parse_mode='HTML')
    except urllib3.exceptions.ProtocolError:
        return send_photo(cookiebot, chat_id, photo, caption, 
                          msg_to_reply, language, thread_id, is_alternate_bot, reply_markup)
    except TelegramError:
        try:
            cookiebot.sendMessage(ownerID, traceback.format_exc())
        except Exception as e:
            print(e)
        return None
    return sentphoto['message_id']

def send_animation(cookiebot, chat_id, animation, caption=None, msg_to_reply=None, language="pt", thread_id=None, is_alternate_bot=0, reply_markup=None):
    try:
        send_chat_action(cookiebot, chat_id, 'upload_photo')
        if language in ['eng', 'es']:
            caption = GoogleTranslator(source='auto', target=language[:2]).translate(caption) if caption else None
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
                                reply_to_message_id=reply_to_message_id, parse_mode='HTML')
            else:
                sentanimation = cookiebot.sendAnimation(chat_id, animation, caption=caption, 
                                reply_to_message_id=reply_to_message_id, 
                                reply_markup=reply_markup, parse_mode='HTML')
    except urllib3.exceptions.ProtocolError:
        return send_animation(cookiebot, chat_id, animation, caption, 
                              msg_to_reply, language, thread_id, is_alternate_bot, reply_markup)
    except TelegramError:
        try:
            cookiebot.sendMessage(ownerID, traceback.format_exc())
        except Exception as e:
            print(e)
        return None
    return sentanimation['message_id']

def set_bot_commands(cookiebot, commands, scope_chat_id, is_alternate_bot=0, language="pt"):
    token = get_bot_token(is_alternate_bot)
    url = f'https://api.telegram.org/bot{token}/setMyCommands'
    data = {'commands': commands,
            'scope': {'type': 'chat', 'chat_id': scope_chat_id},
            'language_code': language[0:2].lower()}
    r = requests.get(url, json=data, timeout=10)
    return r.text

def forward_message(cookiebot, chat_id, from_chat_id, message_id, thread_id=None, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    token = get_bot_token(is_alternate_bot)
    if thread_id:
        url_req = f"https://api.telegram.org/bot{token}/forwardMessage?chat_id={chat_id}&from_chat_id={from_chat_id}&message_id={message_id}&message_thread_id={thread_id}"
        requests.get(url_req, timeout=10)
    else:
        cookiebot.forwardMessage(chat_id, from_chat_id, message_id)

def react_to_message(msg, emoji, is_big=True, is_alternate_bot=0):
    token = get_bot_token(is_alternate_bot)
    reaction = [{'type': 'emoji', 'emoji': emoji}]
    reaction_json = json.dumps(reaction)
    url = f'https://api.telegram.org/bot{token}/setMessageReaction?chat_id={msg["chat"]["id"]}&message_id={msg["message_id"]}&reaction={reaction_json}&is_big={is_big}'
    requests.get(url, timeout=10)

def ban_and_blacklist(cookiebot, chat_id, user_id):
    post_request_backend(f'blacklist/{user_id}')
    cookiebot.kickChatMember(chat_id, user_id)

def leave_and_blacklist(cookiebot, chat_id):
    post_request_backend(f'blacklist/{chat_id}')
    delete_request_backend(f'registers/{chat_id}')
    delete_request_backend(f'configs/{chat_id}')
    cookiebot.leaveChat(chat_id)

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
