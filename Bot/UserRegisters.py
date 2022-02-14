from universal_funcs import *

def CheckNewName(msg, chat_id):
    if not os.path.isfile("Registers/"+str(chat_id)+".txt"):
        open("Registers/"+str(chat_id)+".txt", 'a', encoding='utf-8').close() 
    wait_open("Registers/"+str(chat_id)+".txt")
    text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf-8')
    if 'username' in msg['from'] and (check_if_string_in_file(text_file, msg['from']['username']) == False):
        text_file.write("\n"+msg['from']['username'])
    text_file.close()

def CheckLastMessageDatetime(msg, chat_id):
    lastmessagedate, lastmessagetime = "1-1-1", "0"
    wait_open("Registers/"+str(chat_id)+".txt")
    text_file = open("Registers/"+str(chat_id)+".txt", "r", encoding='utf-8')
    lines = text_file.read().split("\n")
    text_file.close()
    text_file = open("Registers/"+str(chat_id)+".txt", "w", encoding='utf-8')
    for line in lines:
        if line == '':
            pass
        elif 'username' in msg['from'] and line.startswith(msg['from']['username']):
            entry = line.split()
            if 'text' in msg:
                if msg['text'].startswith("/"):
                    if len(entry) == 3:
                        now = entry[2].split(":")
                        lastmessagedate = entry[1]
                        lastmessagetime = (float(now[0])*3600)+(float(now[1])*60)+(float(now[2])*1)
                    else:
                        lastmessagedate = "1-1-1"
                        lastmessagedate = "0"
                    if lines.index(line) == len(lines)-1:
                        text_file.write(entry[0]+" "+str(datetime.datetime.now()))
                    else:
                        text_file.write(entry[0]+" "+str(datetime.datetime.now())+"\n")
                else:
                    if lines.index(line) == len(lines)-1:
                        text_file.write(line)
                    else:
                        text_file.write(line+"\n")
        elif lines.index(line) == len(lines)-1:
            text_file.write(line)
        else:
            text_file.write(line+"\n")
    text_file.close()
    return lastmessagedate, lastmessagetime

def Everyone(cookiebot, msg, chat_id, listaadmins):
    cookiebot.sendChatAction(chat_id, 'typing')
    if str(msg['from']['username']) not in listaadmins:
        cookiebot.sendMessage(chat_id, "Você não tem permissão para chamar todos os membros do grupo.", reply_to_message_id=msg['message_id'])
    else:
        wait_open("Registers/"+str(chat_id)+".txt")
        text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf8')
        lines = text_file.readlines()
        result = ""
        for line in lines:
            username = line.split()[0]
            result += ("@"+username+" ")
        text_file.close()
        cookiebot.sendMessage(chat_id, result, reply_to_message_id=msg['message_id'])

def Adm(cookiebot, msg, chat_id, listaadmins):
    cookiebot.sendChatAction(chat_id, 'typing')
    response = ""
    for admin in listaadmins:
        response += ("@" + admin + " ")
    cookiebot.sendMessage(chat_id, response, reply_to_message_id=msg['message_id'])

def Quem(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
    wait_open("Registers/"+str(chat_id)+".txt")
    text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf-8')
    lines = text_file.readlines()
    text_file.close()
    target = None
    while len(lines)>1 and target in (None, ''):
        target = lines[random.randint(0, len(lines)-1)].replace("\n", '')
        target = target.split()[0]
    cookiebot.sendMessage(chat_id, LocucaoAdverbial+"@"+target, reply_to_message_id=msg['message_id'])

def Shippar(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Registers/"+str(chat_id)+".txt")
    text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf-8')
    lines = text_file.readlines()
    text_file.close()
    targetA = None
    targetB = None
    while len(lines)>2 and (targetA in (None, '') and targetB in (None, '') or targetA == targetB):
        targetA = lines[random.randint(0, len(lines)-1)].replace("\n", '')
        targetA = targetA.split()[0]
        targetB = lines[random.randint(0, len(lines)-1)].replace("\n", '')
        targetB = targetB.split()[0]
    divorce_prob = str(random.randint(0, 100))
    couple_characteristic = random.choice(['Eles se tratam sempre com respeito, educação e bondade', 'Eles evitam julgamentos precipitados ou tentam mudar a personalidade do outro', 'As diferenças existem como em todas as relações, mas elas são respeitadas e superadas', 'Cada um se responsabiliza por seus próprios atos e sentimentos e não culpa o outro por possíveis frustrações e desilusões', 'Eles sempre se certificam de que estão passando tempo suficiente juntos', 'Vocês conseguem rir um do outro e raramente ficam constrangidos em situações que poderiam ser embaraçosas para grande parte dos casais românticos', 
    'Vocês saem juntos por prazer e nunca por obrigação, já que compartilham dos mesmos gostos e preferências', 'Vocês conseguem se comunicar e se entender com simples trocas de olhares, sem precisar verbalizar o que sentem no momento', 'Mesmo quando tentam disfarçar, sempre sabem exatamente o que o outro está pensando', 'Uma tarde chuvosa em casa se transforma em um excelente programa a dois', 'O silêncio, quando surge entre vocês, nunca é incômodo ou desafiador', 'Vocês possuem um número infinito de piadas internas', 'Vocês não se sentem constrangidos ou intimidados em contar segredos ou mesmo chorar um na frente do outro', 'Quando um dos parceiros está triste, o outro sabe exatamente o que dizer e o que fazer para afastar o sentimento ruim',
    'O casal “olho por olho, dente por dente”', 'O casal que se recusa a falar sobre dinheiro'])
    cookiebot.sendMessage(chat_id, "Detectei um Casal! @{} + @{} ❤️\nCaracterística: {} 😮\nChance de divórcio: {}% 📈".format(targetA, targetB, couple_characteristic, divorce_prob), reply_to_message_id=msg['message_id'])