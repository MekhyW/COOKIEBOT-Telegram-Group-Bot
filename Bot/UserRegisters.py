from universal_funcs import *
cache_members = {}

def get_members_chat(chat_id):
    if chat_id in cache_members:
        return cache_members[chat_id]
    members = get_request_backend(f"registers/{chat_id}", {"id": chat_id})
    if 'error' in members and members['error'] == "Not Found":
        post_request_backend(f"registers/{chat_id}", {"id": chat_id, "users": []})
        return []
    members = members['users']
    cache_members[chat_id] = members
    return members

def check_new_name(msg, chat_id):
    if 'from' in msg and 'username' in msg['from'] and msg['from']['username'] != None:
        username = msg['from']['username']
        members = get_members_chat(chat_id)
        if username not in str(members):
            post_request_backend(f"registers/{chat_id}/users", {"user": username, "date": ''})
            if chat_id not in cache_members:
                cache_members[chat_id] = []
            cache_members[chat_id].append(username)

def left_chat_member(msg, chat_id):
    if 'username' in msg['left_chat_member']:
        delete_request_backend(f"registers/{chat_id}/users", {"user": msg['left_chat_member']['username']})
        if msg['left_chat_member']['username'] in cache_members[chat_id]:
            cache_members[chat_id].remove(msg['left_chat_member']['username'])

def everyone(cookiebot, msg, chat_id, listaadmins, language, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    if len(listaadmins) > 0 and 'from' in msg and str(msg['from']['username']) not in listaadmins:
        send_message(cookiebot, chat_id, "Você não tem permissão para chamar todos os membros do grupo!\n<blockquote>Se está falando como canal, entre e use o comando como user</blockquote>", msg, language)
        return
    members = get_members_chat(chat_id)
    if len(members) < 2:
        send_message(cookiebot, chat_id, "Ainda não vi nenhum membro no chat para chamar!\nCom o tempo, o bot vai reconhecer os membros e permitir chamar todos.", msg, language)
        return
    react_to_message(msg, '🫡', is_alternate_bot=is_alternate_bot)
    usernames_list = []
    result = [f"Number of known users: {len(members)}\n"]
    top_message_index = 0
    for member in members:
        if 'user' in member:
            usernames_list.append(member['user'])
    for admin in listaadmins:
        if admin not in usernames_list:
            usernames_list.append(admin)
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

def report_ask(cookiebot, msg, chat_id, targetid, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    send_message(cookiebot, chat_id, "Denunciar como conta falsa/spam?", msg_to_reply=msg, language=language, 
    reply_markup = InlineKeyboardMarkup (inline_keyboard = [
            [InlineKeyboardButton(text="✔️", callback_data=f"Report Yes {targetid} {language}")], 
            [InlineKeyboardButton(text="❌", callback_data=f"Report No {targetid} {language}")]
        ]
    ))

def report(cookiebot, msg, chat_id, targetid, language):
    target = cookiebot.getChatMember(chat_id, targetid)
    chat = cookiebot.getChat(chat_id)
    send_message(cookiebot, mekhyID, f"At chat {chat['title']}")
    send_message(cookiebot, mekhyID, f"Account report: {target}",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Blacklist", callback_data=f"Report Blacklist {targetid} {language} {chat_id}")],
            [InlineKeyboardButton(text="Discard Report", callback_data=f"Report No {targetid} {language}")]
        ]
    ))

def call_admins_ask(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    send_message(cookiebot, chat_id, "Confirma chamar os administradores?", msg_to_reply=msg, language=language, 
    reply_markup = InlineKeyboardMarkup (inline_keyboard = [
            [InlineKeyboardButton(text="✔️", callback_data=f"ADM Yes {language}")], 
            [InlineKeyboardButton(text="❌", callback_data=f"ADM No {language}")]
        ]
    ))

def call_admins(cookiebot, msg, chat_id, listaadmins, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    response = ""
    for admin in listaadmins:
        response += f"@{admin} "
    if 'username' in msg['from']:
        response += f"\n{msg['from']['username']} chamando todos os administradores!"
    else:
        response += f"\n{msg['from']['first_name']} chamando todos os administradores!"
    send_message(cookiebot, chat_id, response, language=language, parse_mode='HTML')

def who(cookiebot, msg, chat_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    members = get_members_chat(chat_id)
    try:
        chosen = random.choice(members)['user']
    except TypeError:
        chosen = random.choice(members)['user']
    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
    send_message(cookiebot, chat_id, LocucaoAdverbial+"@"+chosen, msg, language)

def shipp(cookiebot, msg, chat_id, language, is_alternate_bot=0):
    react_to_message(msg, '❤️', is_alternate_bot=is_alternate_bot)
    send_chat_action(cookiebot, chat_id, 'typing')
    members = get_members_chat(chat_id)
    if len(msg['text'].split()) >= 3:
        targetA = msg['text'].split()[1]
        targetB = msg['text'].split()[2]
    else:
        random.shuffle(members)
        try:
            targetA = members[0]['user']
            targetB = members[1]['user']
        except IndexError:
            send_message(cookiebot, chat_id, "Ainda não vi membros suficientes para shippar!", msg, language)
            return
        except TypeError:
            cache_members.pop(chat_id)
            members = get_members_chat(chat_id)
            targetA = members[0]['user']
            targetB = members[1]['user']
    divorce_prob = str(random.randint(0, 100))
    with open('Static/ship_dynamics.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        ship_dynamic = random.choice(lines).replace('\n', '')
    children_quantity = random.choice(['Nenhum!', 'Um', 'Dois', 'Três'])
    send_message(cookiebot, chat_id, f"Detectei um Casal! @{targetA} + @{targetB} = ❤️\n\nDinâmica: {ship_dynamic}\nFilhos: {children_quantity} 🧸\nChance de divórcio: {divorce_prob}% 📈", msg, language)
