from universal_funcs import *

def GetMembersChat(chat_id):
    members = GetRequestBackend(f"registers/{chat_id}", {"id": chat_id})
    members = json.loads(members['users'])
    return members

def CheckNewName(msg, chat_id):
    username = msg['from']['username']
    members = GetMembersChat(chat_id)
    if username not in members.keys():
        members.append({'user': username, 'date': ''})
        PutRequestBackend(f"registers/{chat_id}", {"id": chat_id, "users": json.dumps(members)})

def Everyone(cookiebot, msg, chat_id, listaadmins, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    if 'from' in msg and str(msg['from']['username']) not in listaadmins:
        Send(cookiebot, chat_id, "Você não tem permissão para chamar todos os membros do grupo!", msg, language)
    else:
        result = ""
        members = GetMembersChat(chat_id)
        for member in members:
            result += ("@"+member['user']+" ")
        cookiebot.sendMessage(chat_id, result, reply_to_message_id=msg['message_id'])

def Adm(cookiebot, msg, chat_id, listaadmins):
    cookiebot.sendChatAction(chat_id, 'typing')
    response = ""
    for admin in listaadmins:
        response += ("@" + admin + " ")
    cookiebot.sendMessage(chat_id, response, reply_to_message_id=msg['message_id'])

def Quem(cookiebot, msg, chat_id, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    members = GetMembersChat(chat_id)
    chosen = random.choice(members)['user']
    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
    Send(cookiebot, chat_id, LocucaoAdverbial+"@"+chosen, msg, language)

def Shippar(cookiebot, msg, chat_id, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    members = GetMembersChat(chat_id)
    if len(msg['text'].split()) >= 3:
        targetA = msg['text'].split()[1]
        targetB = msg['text'].split()[2]
    else:
        members.shuffle()
        targetA = members[0]['user']
        targetB = members[1]['user']
    divorce_prob = str(random.randint(0, 100))
    couple_characteristic = random.choice(['Eles se tratam sempre com respeito, educação e bondade', 'Eles evitam julgamentos precipitados ou tentam mudar a personalidade do outro', 'As diferenças existem como em todas as relações, mas elas são respeitadas e superadas', 'Cada um se responsabiliza por seus próprios atos e sentimentos e não culpa o outro por possíveis frustrações e desilusões', 'Eles sempre se certificam de que estão passando tempo suficiente juntos', 'Vocês conseguem rir um do outro e raramente ficam constrangidos em situações que poderiam ser embaraçosas para grande parte dos casais românticos', 
    'Vocês saem juntos por prazer e nunca por obrigação, já que compartilham dos mesmos gostos e preferências', 'Vocês conseguem se comunicar e se entender com simples trocas de olhares, sem precisar verbalizar o que sentem no momento', 'Mesmo quando tentam disfarçar, sempre sabem exatamente o que o outro está pensando', 'Uma tarde chuvosa em casa se transforma em um excelente programa a dois', 'O silêncio, quando surge entre vocês, nunca é incômodo ou desafiador', 'Vocês possuem um número infinito de piadas internas', 'Vocês não se sentem constrangidos ou intimidados em contar segredos ou mesmo chorar um na frente do outro', 'Quando um dos parceiros está triste, o outro sabe exatamente o que dizer e o que fazer para afastar o sentimento ruim',
    'O casal “olho por olho, dente por dente”', 'O casal que se recusa a falar sobre dinheiro'])
    children_quantity = random.choice(['Nenhum!', 'Um', 'Dois', 'Três'])
    Send(cookiebot, chat_id, "Detectei um Casal! @{} + @{} ❤️\nCaracterística: {} 😮\nQuantos filhos: {} 🧸\nChance de divórcio: {}% 📈".format(targetA, targetB, couple_characteristic, children_quantity, divorce_prob), msg, language)