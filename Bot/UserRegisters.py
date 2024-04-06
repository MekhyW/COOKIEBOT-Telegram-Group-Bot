from universal_funcs import *
cache_members = {}

def GetMembersChat(chat_id):
    if chat_id in cache_members:
        return cache_members[chat_id]
    members = GetRequestBackend(f"registers/{chat_id}", {"id": chat_id})
    if 'error' in members and members['error'] == "Not Found":
        PostRequestBackend(f"registers/{chat_id}", {"id": chat_id, "users": []})
        return []
    members = members['users']
    cache_members[chat_id] = members
    return members

def CheckNewName(msg, chat_id):
    if 'from' in msg and 'username' in msg['from'] and msg['from']['username'] != None:
        username = msg['from']['username']
        members = GetMembersChat(chat_id)
        if username not in str(members):
            PostRequestBackend(f"registers/{chat_id}/users", {"user": username, "date": ''})
            if chat_id not in cache_members:
                cache_members[chat_id] = []
            cache_members[chat_id].append(username)

def left_chat_member(msg, chat_id):
    if 'username' in msg['left_chat_member']:
        DeleteRequestBackend(f"registers/{chat_id}/users", {"user": msg['left_chat_member']['username']})
        if msg['left_chat_member']['username'] in cache_members[chat_id]:
            cache_members[chat_id].remove(msg['left_chat_member']['username'])

def Everyone(cookiebot, msg, chat_id, listaadmins, language, isBombot=False):
    SendChatAction(cookiebot, chat_id, 'typing')
    if len(listaadmins) > 0 and 'from' in msg and str(msg['from']['username']) not in listaadmins:
        Send(cookiebot, chat_id, "Você não tem permissão para chamar todos os membros do grupo\!\n>\(Se está falando como canal, entre e use o comando como user\)", msg, language)
    else:
        members = GetMembersChat(chat_id)
        if len(members) < 2:
            Send(cookiebot, chat_id, "Ainda não vi nenhum membro no chat para chamar\!\nCom o tempo, o bot vai reconhecer os membros e permitir chamar todos.", msg, language)
            return
        ReactToMessage(msg, '🫡', isBombot=isBombot)
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
            if len(result[top_message_index]) + len(username) + 2 > 4096:
                result.append("")
                top_message_index += 1
            result[top_message_index] += f"@{username} "
        for resulting_message in result:
            Send(cookiebot, chat_id, resulting_message, msg_to_reply=msg)

def ReportAsk(cookiebot, msg, chat_id, targetid, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    Send(cookiebot, chat_id, "Denunciar como conta falsa/spam?", msg_to_reply=msg, language=language, 
    reply_markup = InlineKeyboardMarkup (inline_keyboard = [
            [InlineKeyboardButton(text="✔️", callback_data=f"Report Yes {targetid} {language}")], 
            [InlineKeyboardButton(text="❌", callback_data=f"Report No {targetid} {language}")]
        ]
    ))

def Report(cookiebot, msg, chat_id, targetid, language):
    target = cookiebot.getChatMember(chat_id, targetid)
    chat = cookiebot.getChat(chat_id)
    Send(cookiebot, mekhyID, f"At chat {chat['title']}")
    Send(cookiebot, mekhyID, f"Account report\: {target}",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Blacklist", callback_data=f"Report Blacklist {targetid} {language} {chat_id}")],
            [InlineKeyboardButton(text="Discard Report", callback_data=f"Report No {targetid} {language}")]
        ]
    ))

def AdmAsk(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    Send(cookiebot, chat_id, "Confirma chamar os administradores?", msg_to_reply=msg, language=language, 
    reply_markup = InlineKeyboardMarkup (inline_keyboard = [
            [InlineKeyboardButton(text="✔️", callback_data=f"ADM Yes {language}")], 
            [InlineKeyboardButton(text="❌", callback_data=f"ADM No {language}")]
        ]
    ))

def Adm(cookiebot, msg, chat_id, listaadmins, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    response = ""
    for admin in listaadmins:
        response += f"@{admin} "
    if 'username' in msg['from']:
        response += f"\n*{msg['from']['username']}* chamando todos os administradores\!"
    else:
        response += f"\n*{msg['from']['first_name']}* chamando todos os administradores\!"
    Send(cookiebot, chat_id, response, language=language)

def Quem(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    members = GetMembersChat(chat_id)
    try:
        chosen = random.choice(members)['user']
    except TypeError:
        chosen = random.choice(members)['user']
    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
    Send(cookiebot, chat_id, LocucaoAdverbial+"@"+chosen, msg, language)

def Shippar(cookiebot, msg, chat_id, language, isBombot=False):
    ReactToMessage(msg, '❤️', isBombot=isBombot)
    SendChatAction(cookiebot, chat_id, 'typing')
    members = GetMembersChat(chat_id)
    if len(msg['text'].split()) >= 3:
        targetA = msg['text'].split()[1]
        targetB = msg['text'].split()[2]
    else:
        random.shuffle(members)
        try:
            targetA = members[0]['user']
            targetB = members[1]['user']
        except IndexError:
            Send(cookiebot, chat_id, "Ainda não vi membros suficientes para shippar\!", msg, language)
            return
        except TypeError:
            cache_members.pop(chat_id)
            members = GetMembersChat(chat_id)
            targetA = members[0]['user']
            targetB = members[1]['user']
    divorce_prob = str(random.randint(0, 100))
    with open('Static/ship_dynamics.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        ship_dynamic = random.choice(lines).replace('\n', '')
    children_quantity = random.choice(['Nenhum!', 'Um', 'Dois', 'Três'])
    Send(cookiebot, chat_id, f"Detectei um Casal! @{targetA} + @{targetB} = ❤️\n\nDinâmica: {ship_dynamic}\nFilhos: {children_quantity} 🧸\nChance de divórcio: {divorce_prob}% 📈", msg, language)