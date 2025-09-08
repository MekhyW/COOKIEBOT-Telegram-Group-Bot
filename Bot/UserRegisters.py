import random
import time
from universal_funcs import send_chat_action, send_message, react_to_message, get_request_backend, post_request_backend, put_request_backend, delete_request_backend, ownerID, spampouncer_url, spampouncer_key
import requests
import hmac
import hashlib
import json
import telepot
from loc import i18n
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
cache_members = {}
cache_users = {}

def get_members_chat(cookiebot, chat_id):
    if chat_id in cache_members and cache_members[chat_id]:
        return cache_members[chat_id]
    members = get_request_backend(f"registers/{chat_id}", {"id": chat_id})
    if type(members) is str and not members:
        return []
    if 'error' in members and members['error'] == "Not Found":
        post_request_backend(f"registers/{chat_id}", {"id": chat_id, "users": []})
        cache_members[chat_id] = []
        return []
    elif len(members['users']) > 2 * cookiebot.getChatMembersCount(chat_id):
        delete_request_backend(f"registers/{chat_id}")
        post_request_backend(f"registers/{chat_id}", {"id": chat_id, "users": []})
        cache_members[chat_id] = []
        return []
    members = members['users']
    cache_members[chat_id] = members
    return members

def get_user_info(cookiebot, msg, chat_id, user_id, username, first_name, last_name, language_code, birthdate):
    info = {"id": user_id, "username": username, "firstName": first_name, "lastName": last_name, "languageCode": language_code, "birthdate": birthdate}
    if user_id in cache_users and all(cache_users[user_id][key] == info[key] or info[key] is None for key in info):
        return cache_users[user_id]
    if 'text' not in msg and 'caption' not in msg:
        return info
    user = get_request_backend(f"users/{user_id}", {"id": user_id})
    if type(user) is str and not len(user):
        return info
    if 'error' in user and user['error'] == "Not Found":
        text_to_classify = msg['caption'] if 'caption' in msg else msg['text']
        request_body_bytes = json.dumps({"text": text_to_classify}).encode('utf-8')
        response = requests.post(spampouncer_url, data=request_body_bytes, headers={"Content-Type": "application/json", "Authorization": f"HMAC {hmac.new(spampouncer_key.encode('utf-8'), request_body_bytes, hashlib.sha256).hexdigest()}"})
        if 'result' in response.json() and response.json()['result'] == 'spam':
            try:
                cookiebot.kickChatMember(chat_id, user_id)
                cookiebot.deleteMessage(telepot.message_identifier(msg))
                send_message(cookiebot, chat_id, f"Spam message detected. User banned", msg)
            except:
                send_message(cookiebot, chat_id, f"Spam message detected, but I don't have admin rights to kick/delete", msg)
            print(f"Spam message detected in chat {chat_id}")
            return info
        user = info
        post_request_backend(f"users", user)
    elif any(user[key] != info[key] and info[key] is not None for key in info):
        for key in info:
            user[key] = info[key] if user[key] != info[key] and info[key] is not None else user[key]
        put_request_backend(f"users/{user_id}", user)
    cache_users[user_id] = user
    return user

def check_new_name(cookiebot, msg, chat_id, chat_type):
    if 'from' not in msg:
        return
    id = str(msg['from']['id'])
    username = msg['from']['username'] if 'username' in msg['from'] else None
    first_name = msg['from']['first_name'] if 'first_name' in msg['from'] else None
    last_name = msg['from']['last_name'] if 'last_name' in msg['from'] else None
    language_code = msg['from']['language_code'] if 'language_code' in msg['from'] else None
    birthdate = None
    if chat_type == 'private' and (id not in cache_users or 'birthdate' not in cache_users[id]):
        chat = cookiebot.getChat(chat_id)
        if 'birthdate' in chat:
            year = str(chat['birthdate']['year']).zfill(4) if 'year' in chat['birthdate'] else "0000"
            month = str(chat['birthdate']['month']).zfill(2)
            day = str(chat['birthdate']['day']).zfill(2)
            birthdate = f"{year}-{month}-{day}"
            cookiebot.sendMessage(chat_id, f"<b> Birthday registered! </b> <i> {month}/{day} </i>", parse_mode='HTML')
    get_user_info(cookiebot, msg, chat_id, id, username, first_name, last_name, language_code, birthdate)
    if chat_type in ['group', 'supergroup']:
        members = get_members_chat(cookiebot, chat_id)
        if username and username not in str(members):
            post_request_backend(f"registers/{chat_id}/users", {"user": username, "date": ''})
            if chat_id not in cache_members:
                cache_members[chat_id] = []
            cache_members[chat_id].append(username)

def left_chat_member(msg, chat_id):
    if 'username' not in msg['left_chat_member']:
        return
    delete_request_backend(f"registers/{chat_id}/users", {"user": msg['left_chat_member']['username']})
    if msg['left_chat_member']['username'] in cache_members[chat_id]:
        cache_members[chat_id].remove(msg['left_chat_member']['username'])

def everyone(cookiebot, msg, chat_id, listaadmins, language, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if len(listaadmins) > 0 and 'from' in msg and str(msg['from']['username']) not in listaadmins and 'sender_chat' not in msg:
        text = i18n.get("everyone_no", lang=language)
        send_message(cookiebot, chat_id, text, msg)
        return
    members = get_members_chat(cookiebot, chat_id)
    top_message_index = 0
    usernames_list = [member['user'] for member in members if 'user' in member]
    usernames_list.extend(admin for admin in listaadmins if admin not in usernames_list)
    if len(usernames_list) < 2:
        text = i18n.get("everyone_len", lang=language)
        send_message(cookiebot, chat_id, text, msg)
        return
    react_to_message(msg, '🫡', is_alternate_bot=is_alternate_bot)
    result = [f"Number of known users: {min(len(usernames_list), cookiebot.getChatMembersCount(chat_id))}\n"]
    for username in usernames_list:
        try:
            if len(result[top_message_index]) + len(username) + 2 > 4096:
                result.append("")
                top_message_index += 1
        except TypeError:
            pass
        result[top_message_index] += f"@{username} "
    for resulting_message in result:
        send_message(cookiebot, chat_id, resulting_message, msg_to_reply=msg, parse_mode='HTML')
    chat = cookiebot.getChat(chat_id)
    myself = cookiebot.getMe()
    notification_count = 0
    if myself['username'] in usernames_list:
        usernames_list.remove(myself['username'])
    for username in usernames_list:
        user = get_request_backend(f"users?username={username}")
        try:
            if len(user) != 1 or cookiebot.getChatMember(chat_id, int(user[0]['id']))['status'] in ['left', 'kicked']:
                raise Exception
        except:
            delete_request_backend(f"registers/{chat_id}/users", {"user": username})
            continue
        notification_count += 1
        if notification_count % 10 == 0:
            cookiebot.forwardMessage(ownerID, chat_id, msg['message_id']) #will error if original message is deleted
        try:
            text = i18n.get("everyone_call", lang=language, title=chat['title'])
            send_message(cookiebot, user[0]['id'], text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Show message", url=f"https://t.me/c/{str(chat['id']).replace('-100', '')}/{msg['message_id']}")],
            ]))
            time.sleep(0.1)
        except Exception as e:
            pass

def report_ask(cookiebot, msg, chat_id, targetid, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    send_message(cookiebot, chat_id, "Denunciar como conta falsa/spam?", msg_to_reply=msg, language=language, 
    reply_markup = InlineKeyboardMarkup (inline_keyboard = [
            [InlineKeyboardButton(text="✔️", callback_data=f"Report Yes {targetid} {language}")], 
            [InlineKeyboardButton(text="❌", callback_data=f"Report No {targetid} {language}")]
        ]
    ))

def report(cookiebot, chat_id, targetid, language):
    target = cookiebot.getChatMember(chat_id, targetid)
    chat = cookiebot.getChat(chat_id)
    send_message(cookiebot, ownerID, f"At chat {chat['title']}")
    send_message(cookiebot, ownerID, f"Account report: {target}",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Blacklist", callback_data=f"Report Blacklist {targetid} {language} {chat_id}")],
            [InlineKeyboardButton(text="Discard Report", callback_data=f"Report No {targetid} {language}")]
        ]
    ))

def call_admins_ask(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    text = i18n.get("call_admin_ask", lang=language)
    send_message(cookiebot, chat_id, text, msg_to_reply=msg, 
    reply_markup = InlineKeyboardMarkup (inline_keyboard = [
            [InlineKeyboardButton(text="✔️", callback_data=f"ADM Yes {language} {msg['message_id']}")], 
            [InlineKeyboardButton(text="❌", callback_data=f"ADM No {language} {msg['message_id']}")]
        ]
    ))

def call_admins(cookiebot, msg, chat_id, listaadmins, language, message_id):
    send_chat_action(cookiebot, chat_id, 'typing')
    response = " ".join(f"@{admin}" for admin in listaadmins)
    caller = msg['from'].get('username', msg['from']['first_name'])
    additional = i18n.get("call_admin", lang=language, caller=caller)
    response += additional
    send_message(cookiebot, chat_id, response, parse_mode='HTML')
    chat = cookiebot.getChat(chat_id)
    myself = cookiebot.getMe()
    notification_count = 0
    for username in listaadmins:
        user = get_request_backend(f"users?username={username}")
        if len(user) != 1 or int(user[0]['id']) == int(myself['id']):
            continue
        notification_count += 1
        if notification_count % 10 == 0:
            cookiebot.forwardMessage(ownerID, chat_id, message_id) #will error if original message is deleted
        try:
            text = i18n.get("notification_admin", lang=language, title=chat['title'])
            send_message(cookiebot, user[0]['id'], text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Show message", url=f"https://t.me/c/{str(chat['id']).replace('-100', '')}/{message_id}")],
            ]))
            time.sleep(0.1)
        except Exception as e:
            pass

def who(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    members = get_members_chat(cookiebot, chat_id)
    valid_members = [member['user'] for member in members if isinstance(member, dict) and 'user' in member]
    if not valid_members:
        send_message(cookiebot, chat_id, "Não sei", msg, language)
        return
    chosen = random.choice(valid_members)
    adverbial_phrases = i18n.get("adverbial_phrases", lang=language)
    send_message(cookiebot, chat_id, f"{random.choice(adverbial_phrases)} @{chosen}", msg)

def shipp(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    react_to_message(msg, '❤️', is_alternate_bot=is_alternate_bot)
    send_chat_action(cookiebot, chat_id, 'typing')
    members = get_members_chat(cookiebot, chat_id)
    if len(msg['text'].split()) >= 3:
        target_a = msg['text'].split()[1]
        target_b = msg['text'].split()[2]
    else:
        random.shuffle(members)
        try:
            target_a = members[0]['user']
            target_b = members[1]['user']
        except IndexError:
            text = i18n.get("no_ship", lang=language)
            send_message(cookiebot, chat_id, text, msg)
            return
        except TypeError:
            if chat_id in cache_members:
                cache_members.pop(chat_id)
            members = get_members_chat(cookiebot, chat_id)
            target_a = members[0]['user']
            target_b = members[1]['user']
    divorce_prob = str(random.randint(0, 100))

    ship_dynamic = i18n.get_random_line("ship_dynamics.txt", lang=language)
    children_quantity = random.choice(['0', '1', '2', '3'])
    ctx = {
        "target_a": target_a,
        "target_b": target_b,
        "ship_dynamic": ship_dynamic,
        "children_count": children_quantity,
        "divorce_prob": divorce_prob
    }
    text = i18n.get("ship", lang=language, **ctx)
    send_message(cookiebot, chat_id, text, msg)
