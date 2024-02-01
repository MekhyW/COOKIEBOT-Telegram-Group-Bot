googleAPIkey = ''
searchEngineCX = ''
exchangerate_key = ''
openai_key = ''
cookiebotTOKEN = ''
bombotTOKEN = ''
mekhyID = 780875868
import os, math, numpy, random, time, datetime, re, sys, traceback
import urllib, urllib3, json, requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, Message
from telepot.delegate import (per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
from telepot.exception import *
import googletrans
translator = googletrans.Translator()
backendauth = json.loads(open('cookiebot_backendauth.json', 'r').read())
login_backend, password_backend, serverIP = backendauth['login'], backendauth['password'], backendauth['serverIP']

def GetRequestBackend(route, params=None):
    response = requests.get(f'{serverIP}/{route}', json=params, auth = HTTPBasicAuth(login_backend, password_backend), verify=False, timeout=10)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return ''
    except Exception as e:
        print(e)
        return ''

def PostRequestBackend(route, params=None):
    response = requests.post(f'{serverIP}/{route}', json=params, auth = HTTPBasicAuth(login_backend, password_backend), verify=False, timeout=10)
    try:
        print("POST: ", response.text)
        return json.loads(response.text)
    except json.JSONDecodeError:
        return ''
    except Exception as e:
        print(e)
        return ''

def PutRequestBackend(route, params=None):
    response = requests.put(f'{serverIP}/{route}', json=params, auth = HTTPBasicAuth(login_backend, password_backend), verify=False, timeout=10)
    try:
        print("PUT: ", response.text)
        return json.loads(response.text)
    except json.JSONDecodeError:
        return ''
    except Exception as e:
        print(e)
        return ''

def DeleteRequestBackend(route, params=None):
    response = requests.delete(f'{serverIP}/{route}', json=params, auth = HTTPBasicAuth(login_backend, password_backend), verify=False, timeout=10)
    try:
        print("DELETE: ", response.text)
        return json.loads(response.text)
    except json.JSONDecodeError:
        return ''
    except Exception as e:
        print(e)
        return ''

def SendChatAction(cookiebot, chat_id, action):
    try:
        cookiebot.sendChatAction(chat_id, action)
    except urllib3.exceptions.ProtocolError:
        cookiebot.sendChatAction(chat_id, action)

def GetVoiceMessage(cookiebot, msg, isBombot=False):
    if isBombot:
        token = bombotTOKEN
    else:
        token = cookiebotTOKEN
    try:
        r = requests.get(f"https://api.telegram.org/file/bot{token}/{cookiebot.getFile(msg['voice']['file_id'])['file_path']}", allow_redirects=True, timeout=10)
    except urllib3.exceptions.ProtocolError:
        r = requests.get(f"https://api.telegram.org/file/bot{token}/{cookiebot.getFile(msg['voice']['file_id'])['file_path']}", allow_redirects=True, timeout=10)
    return r.content

def Send(cookiebot, chat_id, text, msg_to_reply=None, language="pt", thread_id=None, isBombot=False, reply_markup=None):
    try:
        SendChatAction(cookiebot, chat_id, 'typing')
        if language == 'eng':
            text = translator.translate(text, dest='en').text
        elif language == 'es':
            text = translator.translate(text, dest='es').text
        if msg_to_reply:
            reply_id = msg_to_reply['message_id']
            try:
                cookiebot.sendMessage(chat_id, text, reply_to_message_id=reply_id, reply_markup=reply_markup, parse_mode='Markdown')
            except telepot.exception.TelegramError:
                cookiebot.sendMessage(chat_id, text, reply_to_message_id=reply_id, reply_markup=reply_markup)
        elif thread_id is not None:
            token = bombotTOKEN if isBombot else cookiebotTOKEN
            url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}&message_thread_id={thread_id}&reply_markup={reply_markup}&parse_mode=Markdown"
            if reply_markup is None:
                url = url.replace('&reply_markup=None', '')
            requests.get(url)
        else:
            try:
                cookiebot.sendMessage(chat_id, text, reply_markup=reply_markup, parse_mode='Markdown')
            except telepot.exception.TelegramError:
                cookiebot.sendMessage(chat_id, text, reply_markup=reply_markup)
    except urllib3.exceptions.ProtocolError:
        Send(cookiebot, chat_id, text, msg_to_reply, language, thread_id, isBombot, reply_markup)
    except TelegramError:
        try:
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
        except Exception as e:
            print(e)

def SendPhoto(cookiebot, chat_id, photo, caption=None, msg_to_reply=None, language="pt", thread_id=None, isBombot=False, reply_markup=None):
    try:
        SendChatAction(cookiebot, chat_id, 'upload_photo')
        if language == 'eng' and caption is not None:
            caption = translator.translate(caption, dest='en').text
        elif language == 'es':
            caption = translator.translate(caption, dest='es').text
        if msg_to_reply:
            try:
                sentphoto = cookiebot.sendPhoto(chat_id, photo, caption=caption, reply_to_message_id=msg_to_reply['message_id'], reply_markup=reply_markup, parse_mode='Markdown')
            except telepot.exception.TelegramError:
                sentphoto = cookiebot.sendPhoto(chat_id, photo, caption=caption, reply_to_message_id=msg_to_reply['message_id'], reply_markup=reply_markup)
        elif thread_id is not None:
            token = bombotTOKEN if isBombot else cookiebotTOKEN
            url = f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}&photo={photo}&caption={caption}&message_thread_id={thread_id}&reply_markup={reply_markup}&parse_mode=Markdown"
            if reply_markup is None:
                url = url.replace('&reply_markup=None', '')
            sentphoto = {}
            sentphoto['message_id'] = json.loads(requests.get(url).text)['result']['message_id']
        else:
            try:
                sentphoto = cookiebot.sendPhoto(chat_id, photo, caption=caption, reply_markup=reply_markup, parse_mode='Markdown')
            except telepot.exception.TelegramError:
                sentphoto = cookiebot.sendPhoto(chat_id, photo, caption=caption, reply_markup=reply_markup)
    except urllib3.exceptions.ProtocolError:
        return SendPhoto(cookiebot, chat_id, photo, caption, msg_to_reply, language, thread_id, isBombot, reply_markup)
    except TelegramError:
        try:
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
        except Exception as e:
            print(e)
        return None
    return sentphoto['message_id']

def SetMyCommands(cookiebot, commands, scope_chat_id, isBombot=False, language="pt"):
    if isBombot:
        token = bombotTOKEN
    else:
        token = cookiebotTOKEN
    url = f'https://api.telegram.org/bot{token}/setMyCommands'
    data = {'commands': commands,
            'scope': {'type': 'chat', 'chat_id': scope_chat_id},
            'language_code': language[0:2].lower()}
    r = requests.get(url, json=data)
    return r.text

def Forward(cookiebot, chat_id, from_chat_id, message_id, thread_id=None, isBombot=False):
    SendChatAction(cookiebot, chat_id, 'typing')
    if isBombot:
        token = bombotTOKEN
    else:
        token = cookiebotTOKEN
    if thread_id:
        url_req = f"https://api.telegram.org/bot{token}/forwardMessage?chat_id={chat_id}&from_chat_id={from_chat_id}&message_id={message_id}&message_thread_id={thread_id}"
        requests.get(url_req)
    else:
        cookiebot.forwardMessage(chat_id, from_chat_id, message_id)

def BanAndBlacklist(cookiebot, chat_id, user_id):
    PostRequestBackend(f'blacklist/{user_id}')
    cookiebot.kickChatMember(chat_id, user_id)

def LeaveAndBlacklist(cookiebot, chat_id):
    PostRequestBackend(f'blacklist/{chat_id}')
    DeleteRequestBackend(f'registers/{chat_id}')
    DeleteRequestBackend(f'configs/{chat_id}')
    cookiebot.leaveChat(chat_id)

def wait_open(filename):
    if os.path.exists(filename):
        try:
            text = open(filename, 'r')
            text.close()
        except IOError:
            time.sleep(1)

def DeleteMessage(cookiebot, identifier):
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
    emojis = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'}
    emojis_string = ''
    for digit in str(number):
        emojis_string += emojis[digit]
    return emojis_string

def emojis_to_numbers(text):
    emojis = {'0️⃣': '0', '1️⃣': '1', '2️⃣': '2', '3️⃣': '3', '4️⃣': '4', '5️⃣': '5', '6️⃣': '6', '7️⃣': '7', '8️⃣': '8', '9️⃣': '9'}
    text_without_emojis = ''
    for char in text:
        if char in emojis:
            text_without_emojis += emojis[char]
        else:
            text_without_emojis += char
    return text_without_emojis