from telegram import BotCommand
from universal_funcs import *

def GetAdmins(cookiebot, msg, chat_id):
    listaadmins, listaadmins_id = [], []
    if not os.path.exists("GranularAdmins/GranularAdmins_" + str(chat_id) + ".txt"):
        text = open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt", 'w').close()
    wait_open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt")
    text_file = open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt", 'r', encoding='utf-8')
    lines = text_file.readlines()
    text_file.close()
    if lines != []:
        for username in lines:
            listaadmins.append(username.replace("\n", ''))
    else:
        for admin in cookiebot.getChatAdministrators(chat_id):
            if 'username' in admin['user']:
                listaadmins.append(str(admin['user']['username']))
            listaadmins_id.append(str(admin['user']['id']))
    return listaadmins, listaadmins_id


def SetLanguageComandos(cookiebot, chat_id, chat_to_alter, language):
    wait_open("Cookiebot functions {}.txt".format(language))
    text_file = open("Cookiebot functions {}.txt".format(language), "r", encoding='utf8')
    lines = text_file.readlines()
    text_file.close()
    comandos = []
    for line in lines:
        if " - " in line:
            command = line.split(" - ")[0].strip()
            description = line.split(" - ")[1].replace("\n", "")
            if len(command.split()) == 1 and command.islower():
                comandos.append({'command': command, 'description': description})
    cookiebot.setMyCommands(commands = comandos, scope = {"type": "chat", "chat_id": chat_to_alter})
    cookiebot.setMyCommands(commands = comandos, scope = {"type": "chat", "chat_id": chat_id})


def GetConfig(chat_id):
    publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language = 1, 0, 1, 5, 600, 300, 1, 1, "pt"
    if not os.path.isfile("Configs/Config_"+str(chat_id)+".txt"):
        open("Configs/Config_"+str(chat_id)+".txt", 'a', encoding='utf-8').close()
        text_file = open("Configs/Config_"+str(chat_id)+".txt", "w", encoding='utf-8')
        text_file.write("Publicador: 1\nFurBots: 0\nSticker_Spam_Limit: 15\nTempo_sem_poder_mandar_imagem: 600\nTempo_Captcha: 300\nFunções_Diversão: 1\nFunções_Utilidade: 1\nSFW: 1\nLanguage: pt")
        text_file.close()
    wait_open("Configs/Config_"+str(chat_id)+".txt")
    text_file = open("Configs/Config_"+str(chat_id)+".txt", "r", encoding='utf-8')
    lines = text_file.readlines()
    text_file.close()
    for line in lines:
        if line.split()[0] == "Publicador:":
            publisher = int(line.split()[1])
        elif line.split()[0] == "FurBots:":
            FurBots = int(line.split()[1])
        elif line.split()[0] == "Sticker_Spam_Limit:":
            stickerspamlimit = int(line.split()[1])
        elif line.split()[0] == "Tempo_sem_poder_mandar_imagem:":
            limbotimespan = int(line.split()[1])
        elif line.split()[0] == "Tempo_Captcha:":
            captchatimespan = int(line.split()[1])
        elif line.split()[0] == "Funções_Diversão:":
            funfunctions = int(line.split()[1])
        elif line.split()[0] == "Funções_Utilidade:":
            utilityfunctions = int(line.split()[1])
        elif line.split()[0] == "SFW:":
            sfw = int(line.split()[1])
        elif line.split()[0] == "Language:":
            language = line.split()[1]
    return publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language


def Configurar(cookiebot, msg, chat_id, listaadmins, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    if str(msg['from']['username']) in listaadmins or str(msg['from']['username']) == "MekhyW":
        wait_open("Configs/Config_"+str(chat_id)+".txt")
        text = open("Configs/Config_"+str(chat_id)+".txt", 'r', encoding='utf-8')
        variables = text.read()
        text.close()
        try:
            cookiebot.sendMessage(msg['from']['id'],"Current settings:\n\n" + variables + '\n\nChoose the variable you would like to change', reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="Language",callback_data='k CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="FurBots",callback_data='a CONFIG {}'.format(str(chat_id)))], 
                                    [InlineKeyboardButton(text="Stickers limit",callback_data='b CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="🕒 Limbo",callback_data='c CONFIG {}'.format(str(chat_id)))], 
                                    [InlineKeyboardButton(text="🕒 CAPTCHA",callback_data='d CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="Fun Functions",callback_data='h CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="Utility Functions",callback_data='i CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="SFW Chat",callback_data='j CONFIG {}'.format(str(chat_id)))]
                                ]
                            ))
            Send(cookiebot, chat_id, "Te mandei uma mensagem no chat privado para configurar", msg, language)
        except Exception as e:
            Send(cookiebot, chat_id, "Não consegui te mandar o menu de configuração (vc já mandou /start no meu chat privado?)" , msg, language)
            print(e)
    else:
        Send(cookiebot, chat_id, "Você não tem permissão para configurar o bot!", msg, language)


def ConfigurarSettar(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if msg['text'].isdigit() or msg['text'] in ["pt", "eng", "es"]:
        variable_to_be_altered = ""
        if "Bot language for the chat. Use pt for portuguese, eng for english or es for spanish" in msg['reply_to_message']['text']:
            variable_to_be_altered = "Language"
        elif "Use 1 to not interfere with other furbots if they're in the group, or 0 if I'm the only one." in msg['reply_to_message']['text']:
            variable_to_be_altered = "FurBots"
        elif "This is the maximum number of stickers allowed in a sequence by the bot. The next ones beyond that will be deleted to avoid spam. It's valid for everyone." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Sticker_Spam_Limit"
        elif "This is the time for which new users in the group will not be able to send images (the bot automatically deletes)." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Tempo_sem_poder_mandar_imagem"
        elif "This is the time new users have to solve Captcha. USE 0 TO TURN CAPTCHA OFF!" in msg['reply_to_message']['text']:
            variable_to_be_altered = "Tempo_Captcha"
        elif "Use 1 to enable commands and fun functionality, or 0 for control/management functions only." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Funções_Diversão"
        elif "Use 1 to enable commands and utility features, or 0 to disable them." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Funções_Utilidade"
        elif "Use 1 to indicate the chat is SFW, or 0 for NSFW." in msg['reply_to_message']['text']:
            variable_to_be_altered = "SFW"
        chat_to_alter = msg['reply_to_message']['text'].split("\n")[0].split("= ")[1]
        wait_open("Configs/Config_"+str(chat_to_alter)+".txt")
        text_file = open("Configs/Config_"+str(chat_to_alter)+".txt", 'r', encoding='utf-8')
        lines = text_file.readlines()
        text_file.close()
        text_file = open("Configs/Config_"+str(chat_to_alter)+".txt", 'w', encoding='utf-8')
        for line in lines:
            if variable_to_be_altered in line:
                text_file.write(variable_to_be_altered + ": " + msg['text'] + "\n")
                cookiebot.sendMessage(chat_id, "Variable configured! ✔️\nYou can return to chat now")
                DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))
                DeleteMessage(cookiebot, telepot.message_identifier(msg))
                if variable_to_be_altered == "Language":
                    SetLanguageComandos(cookiebot, chat_id, chat_to_alter, msg['text'])
            elif len(line.split()) > 1:
                text_file.write(line)
        text_file.close()
    else:
        cookiebot.sendMessage(chat_id, "ERROR: invalid input\nTry again", reply_to_message_id=msg['message_id'])


def ConfigVariableButton(cookiebot, msg, query_data):
    DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
    if query_data.startswith('k'):
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nBot language for the chat. Use pt for portuguese, eng for english or es for spanish\nREPLY THIS MESSAGE with the new variable value'.format(query_data.split()[2]))
    if query_data.startswith('a'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 to not interfere with other furbots if they're in the group, or 0 if I'm the only one.\nREPLY THIS MESSAGE with the new variable value".format(query_data.split()[2]))
    elif query_data.startswith('b'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nThis is the maximum number of stickers allowed in a sequence by the bot. The next ones beyond that will be deleted to avoid spam. It's valid for everyone.\nREPLY THIS MESSAGE with the new variable value".format(query_data.split()[2]))
    elif query_data.startswith('c'):
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nThis is the time for which new users in the group will not be able to send images (the bot automatically deletes).\nREPLY THIS MESSAGE with the new variable value'.format(query_data.split()[2]))
    elif query_data.startswith('d'):
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nThis is the time new users have to solve Captcha. USE 0 TO TURN CAPTCHA OFF!\nREPLY THIS MESSAGE with the new variable value'.format(query_data.split()[2]))
    elif query_data.startswith('h'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 to enable commands and fun functionality, or 0 for control/management functions only.\nREPLY THIS MESSAGE with the new variable value".format(query_data.split()[2]))
    elif query_data.startswith('i'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 to enable commands and utility features, or 0 to disable them.\nREPLY THIS MESSAGE with the new variable value".format(query_data.split()[2]))
    elif query_data.startswith('j'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 to indicate the chat is SFW, or 0 for NSFW.\nREPLY THIS MESSAGE with the new variable value".format(query_data.split()[2]))


def AtualizaBemvindo(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Welcome/Welcome_" + str(chat_id)+".txt")
    text_file = open("Welcome/Welcome_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Welcome message updated! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))

def NovoBemvindo(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone joins the group", reply_to_message_id=msg['message_id'])


def AtualizaRegras(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Rules/Regras_" + str(chat_id)+".txt")
    text_file = open("Rules/Regras_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Updated rules message! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))

def NovasRegras(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone asks for the rules", reply_to_message_id=msg['message_id'])

def Regras(cookiebot, msg, chat_id, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Rules/Regras_" + str(chat_id)+".txt")
    if os.path.exists("Rules/Regras_" + str(chat_id)+".txt"):
        with open("Rules/Regras_" + str(chat_id)+".txt", encoding='utf-8') as file:
            regras = file.read()
        if language == 'pt':
            cookiebot.sendMessage(chat_id, regras+"\n\nDúvidas em relação ao bot? Mande para @MekhyW", reply_to_message_id=msg['message_id'])
        elif language == 'es':
            cookiebot.sendMessage(chat_id, regras+"\n\n¿Preguntas sobre el bot? Envíalo a @MekhyW", reply_to_message_id=msg['message_id'])
        else:
            cookiebot.sendMessage(chat_id, regras+"\n\nQuestions about the bot? Send to @MekhyW", reply_to_message_id=msg['message_id'])
    else:    
        Send(cookiebot, chat_id, "Ainda não há regras colocadas para esse grupo\nPara tal, use o /novasregras", msg, language)