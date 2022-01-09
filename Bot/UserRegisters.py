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
    target = None
    while len(lines)>1 and target in (None, ''):
        target = lines[random.randint(0, len(lines)-1)].replace("\n", '')
        target = target.split()[0]
    cookiebot.sendMessage(chat_id, LocucaoAdverbial+"@"+target, reply_to_message_id=msg['message_id'])
    text_file.close()