import random
import time
from universal_funcs import send_chat_action, send_message, react_to_message, get_request_backend, post_request_backend, put_request_backend, delete_request_backend, ownerID, spampouncer_url, spampouncer_key
import requests
import hmac
import hashlib
import json
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
cache_members = {}
cache_users = {}

def get_members_chat(cookiebot, chat_id):
    if chat_id in cache_members and len(cache_members[chat_id]):
        return cache_members[chat_id]
    members = get_request_backend.__wrapped__(f"registers/{chat_id}", {"id": chat_id})
    print(members)
    if type(members) is str and not len(members):
        return []
    if ('error' in members and members['error'] == "Not Found") or ('users' in members and len(members['users']) > 2 * cookiebot.getChatMembersCount(chat_id)):
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

def left_chat_member(msg, chat_id):
    if 'username' not in msg['left_chat_member']:
        return
    delete_request_backend(f"registers/{chat_id}/users", {"user": msg['left_chat_member']['username']})
    if msg['left_chat_member']['username'] in cache_members[chat_id]:
        cache_members[chat_id].remove(msg['left_chat_member']['username'])

def everyone(cookiebot, msg, chat_id, listaadmins, language, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if len(listaadmins) > 0 and 'from' in msg and str(msg['from']['username']) not in listaadmins and 'sender_chat' not in msg:
        text = "Você não tem permissão para chamar todos os membros do grupo!\n<blockquote> Se está falando como canal, entre e use o comando como user </blockquote>" if language == 'pt' else "¡No tienes permiso para llamar a todos los miembros del grupo!\n<blockquote>Si estás hablando como canal, únete y usa el comando como usuario</blockquote>" if language == 'es' else "You don't have permission to call all members of the group!\n<blockquote>If you're speaking as a channel, join and use the command as a user</blockquote>"
        send_message(cookiebot, chat_id, text, msg)
        return
    members = get_members_chat(cookiebot, chat_id)
    top_message_index = 0
    usernames_list = [member['user'] for member in members if 'user' in member]
    usernames_list.extend(admin for admin in listaadmins if admin not in usernames_list)
    if len(usernames_list) < 2:
        text = "Ainda não vi nenhum membro no chat para chamar!\nCom o tempo, o bot vai reconhecer os membros e permitir chamar todos." if language == 'pt' else "¡Todavía no he visto ningún miembro en el chat para llamar!\nCon el tiempo, el bot reconocerá a los miembros y permitirá llamar a todos." if language == 'es' else "I haven't seen any members in the chat to call yet!\nOver time, the bot will recognize members and allow calling everyone."
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
            text = f"Você foi chamado no chat <b> {chat['title']} </b>" if language == 'pt' else f"¡Te han llamado en el chat <b> {chat['title']} </b>!" if language == 'es' else f"You were called in the chat <b> {chat['title']} </b>"
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
    text = "Confirma chamar os administradores?" if language == 'pt' else "¿Confirma llamar a los administradores?" if language == 'es' else "Do you confirm to call the admins?"
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
    additional = f"\n{caller} chamando todos os administradores!" if language == 'pt' else f"\n{caller} llamando a todos los administradores!" if language == 'es' else f"\n{caller} calling all admins!"
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
            text = f"Você foi chamado no chat <b> {chat['title']} </b>" if language == 'pt' else f"¡Te han llamado en el chat <b> {chat['title']} </b>!" if language == 'es' else f"You were called in the chat <b> {chat['title']} </b>"
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
    adverbial_phrases = [
        "Com certeza o(a)" if language == 'pt' else "Sin duda el/la" if language == 'es' else "Without a doubt",
        "Sem sombra de dúvidas o(a)" if language == 'pt' else "Sin lugar a dudas el/la" if language == 'es' else "Without a shadow of a doubt",
        "Suponho que o(a)" if language == 'pt' else "Supongo que el/la" if language == 'es' else "I suppose",
        "Aposto que o(a)" if language == 'pt' else "Apuesto a que el/la" if language == 'es' else "I bet",
        "Talvez o(a)" if language == 'pt' else "Quizás el/la" if language == 'es' else "Maybe",
        "Quem sabe o(a)" if language == 'pt' else "Quién sabe el/la" if language == 'es' else "Who knows",
        "Aparentemente o(a)" if language == 'pt' else "Aparentemente el/la" if language == 'es' else "Apparently",
    ]
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
            text = "Ainda não vi membros suficientes para shippar!" if language == 'pt' else "¡Todavía no he visto suficientes miembros para enviar un barco!" if language == 'es' else "I haven't seen enough members to ship yet!"
            send_message(cookiebot, chat_id, text, msg)
            return
        except TypeError:
            if chat_id in cache_members:
                cache_members.pop(chat_id)
            members = get_members_chat(cookiebot, chat_id)
            target_a = members[0]['user']
            target_b = members[1]['user']
    divorce_prob = str(random.randint(0, 100))
    with open(f'Static/ship/ship_dynamics_{language}.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        ship_dynamic = random.choice(lines).replace('\n', '')
    children_quantity = random.choice(['0', '1', '2', '3'])
    text = f"Detectei um Casal! @{target_a} + @{target_b} = ❤️\n\nDinâmica: {ship_dynamic}\nFilhos: {children_quantity} 🧸\nChance de divórcio: {divorce_prob}% 📈" if language == 'pt' else f"¡Detecté una pareja! @{target_a} + @{target_b} = ❤️\n\nDinámica: {ship_dynamic}\nHijos: {children_quantity} 🧸\nProbabilidad de divorcio: {divorce_prob}% 📈" if language == 'es' else f"I detected a Couple! @{target_a} + @{target_b} = ❤️\n\nDynamics: {ship_dynamic}\nChildren: {children_quantity} 🧸\nChance of divorce: {divorce_prob}% 📈"
    send_message(cookiebot, chat_id, text, msg)
