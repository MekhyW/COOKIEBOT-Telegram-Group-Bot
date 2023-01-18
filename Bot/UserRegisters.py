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
    if 'username' in msg['from'] and msg['from']['username'] != None:
        username = msg['from']['username']
        members = GetMembersChat(chat_id)
        if username not in str(members):
            PostRequestBackend(f"registers/{chat_id}/users", {"user": username, "date": ''})
            cache_members[chat_id].append(username)

def left_chat_member(msg, chat_id):
    if 'username' in msg['left_chat_member']:
        DeleteRequestBackend(f"registers/{chat_id}/users", {"user": msg['left_chat_member']['username']})
        if msg['left_chat_member']['username'] in cache_members[chat_id]:
            cache_members[chat_id].remove(msg['left_chat_member']['username'])

def Everyone(cookiebot, msg, chat_id, listaadmins, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    if 'from' in msg and str(msg['from']['username']) not in listaadmins:
        Send(cookiebot, chat_id, "Você não tem permissão para chamar todos os membros do grupo!", msg, language)
    else:
        members = GetMembersChat(chat_id)
        result = f"Number of known users: {len(members)}\n"
        for member in members:
            if 'user' in member:
                result += f"@{member['user']} "
        Send(cookiebot, chat_id, result, msg_to_reply=msg)

def Adm(cookiebot, msg, chat_id, listaadmins):
    SendChatAction(cookiebot, chat_id, 'typing')
    response = ""
    for admin in listaadmins:
        response += ("@" + admin + " ")
    Send(cookiebot, chat_id, response, msg_to_reply=msg)

def Quem(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    members = GetMembersChat(chat_id)
    chosen = random.choice(members)['user']
    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
    Send(cookiebot, chat_id, LocucaoAdverbial+"@"+chosen, msg, language)

def Shippar(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    members = GetMembersChat(chat_id)
    if len(msg['text'].split()) >= 3:
        targetA = msg['text'].split()[1]
        targetB = msg['text'].split()[2]
    else:
        random.shuffle(members)
        targetA = members[0]['user']
        targetB = members[1]['user']
    divorce_prob = str(random.randint(0, 100))
    couple_characteristic = random.choice(['Eles se tratam sempre com respeito, educação e bondade', 'Eles evitam julgamentos precipitados ou tentam mudar a personalidade do outro', 'As diferenças existem como em todas as relações, mas elas são respeitadas e superadas', 'Cada um se responsabiliza por seus próprios atos e sentimentos e não culpa o outro por possíveis frustrações e desilusões', 'Eles sempre se certificam de que estão passando tempo suficiente juntos', 'Vocês conseguem rir um do outro e raramente ficam constrangidos em situações que poderiam ser embaraçosas para grande parte dos casais românticos', 
    'Vocês saem juntos por prazer e nunca por obrigação, já que compartilham dos mesmos gostos e preferências', 'Vocês conseguem se comunicar e se entender com simples trocas de olhares, sem precisar verbalizar o que sentem no momento', 'Mesmo quando tentam disfarçar, sempre sabem exatamente o que o outro está pensando', 'Uma tarde chuvosa em casa se transforma em um excelente programa a dois', 'O silêncio, quando surge entre vocês, nunca é incômodo ou desafiador', 'Vocês possuem um número infinito de piadas internas', 'Vocês não se sentem constrangidos ou intimidados em contar segredos ou mesmo chorar um na frente do outro', 'Quando um dos parceiros está triste, o outro sabe exatamente o que dizer e o que fazer para afastar o sentimento ruim',
    'O casal “olho por olho, dente por dente”', 'O casal que se recusa a falar sobre dinheiro'])
    children_quantity = random.choice(['Nenhum!', 'Um', 'Dois', 'Três'])
    Send(cookiebot, chat_id, f"Detectei um Casal! @{targetA} + @{targetB} ❤️\nCaracterística: {couple_characteristic} 😮\nQuantos filhos: {children_quantity} 🧸\nChance de divórcio: {divorce_prob}% 📈", msg, language)