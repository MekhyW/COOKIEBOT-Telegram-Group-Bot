from universal_funcs import *

sentcooldownmessage = False

def Sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit):
    wait_open("Stickers.txt")
    text_file = open("Stickers.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    if any(str(chat_id) in string for string in lines):
        pass
    else:
        lines.append("\n"+str(chat_id)+" 0")
    text_file.close()
    counter_new = 0
    for line in lines:
        if str(chat_id) in line:
            counter_new = int(line.split()[1])+1
            break
    text_file = open("Stickers.txt", "w", encoding='utf8')
    for line in lines:
        if str(chat_id) in line:
            text_file.write(line.split()[0] + " " + str(int(line.split()[1])+1) + "\n")
        else:
            text_file.write(line)
    text_file.close()
    if counter_new == stickerspamlimit:
        cookiebot.sendMessage(chat_id, "Cuidado com o flood de stickers.\nMantenham o chat com textos!")
    if counter_new > stickerspamlimit:
        DeleteMessage(cookiebot, telepot.message_identifier(msg))

def CooldownUpdates(msg, chat_id, lastmessagetime):
    if float(lastmessagetime)+60 < ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
        sentcooldownmessage = False
    if 'text' in msg:
        wait_open("Stickers.txt")
        text_file = open("Stickers.txt", "r+", encoding='utf8')
        lines = text_file.readlines()
        text_file.close()
        text_file = open("Stickers.txt", "w", encoding='utf8')
        for line in lines:
            if str(chat_id) in line:
                text_file.write(line.split()[0] + " " + "0" + "\n")
            else:
                text_file.write(line)
        text_file.close()

def CooldownAction(cookiebot, msg, chat_id):
    global sentcooldownmessage
    if sentcooldownmessage == False:
        cookiebot.sendMessage(chat_id, "Você está em Cooldown!\nApenas use um comando '/' por minuto\nIsso é feito como medida de anti-spam :c\n(OBS: o cooldown foi resetado agora)", reply_to_message_id=msg['message_id'])
        sentcooldownmessage = True
    elif sentcooldownmessage == True:
        DeleteMessage(cookiebot, telepot.message_identifier(msg))