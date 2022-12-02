from universal_funcs import *

def GetAdmins(cookiebot, msg, chat_id):
    listaadmins, listaadmins_id = [], []
    for admin in cookiebot.getChatAdministrators(chat_id):
        if 'username' in admin['user']:
            listaadmins.append(str(admin['user']['username']))
        listaadmins_id.append(str(admin['user']['id']))
    return listaadmins, listaadmins_id


def SetLanguageComandos(cookiebot, chat_id, chat_to_alter, language):
    wait_open("Static/Cookiebot_functions_{}.txt".format(language))
    text_file = open("Static/Cookiebot_functions_{}.txt".format(language), "r", encoding='utf8')
    lines = text_file.readlines()
    text_file.close()
    comandos = []
    for line in lines:
        if " - " in line:
            command = line.split(" - ")[0].strip()
            description = line.split(" - ")[1].replace("\n", "")
            if len(command.split()) == 1 and command.islower():
                comandos.append({'command': command, 'description': description})
    #cookiebot.setMyCommands(commands = comandos, scope = {"type": "chat", "chat_id": chat_to_alter})
    #cookiebot.setMyCommands(commands = comandos, scope = {"type": "chat", "chat_id": chat_id})

def SetComandosPrivate(cookiebot, chat_id):
    SetLanguageComandos(cookiebot, chat_id, chat_id, "private")

def GetConfig(chat_id):
    FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask = 0, 1, 5, 600, 300, 1, 1, "pt", 1, 1
    configs = GetRequestBackend(f"configs/{chat_id}")
    if 'error' in configs and configs['error'] == "Not Found":
        PostRequestBackend(f"configs/{chat_id}", {'furbots': FurBots, 'sfw': sfw, 'stickerSpamLimit': stickerspamlimit, 'timeWithoutSendingImages': limbotimespan, 'timeCaptcha': captchatimespan, 'functionsFun': funfunctions, 'functionsUtility': utilityfunctions, 'language': language, 'publisherPost': publisherpost, 'publisherAsk': publisherask})
    else:
        FurBots = configs['furbots']
        sfw = configs['sfw']
        stickerspamlimit = configs['stickerSpamLimit']
        limbotimespan = configs['timeWithoutSendingImages']
        captchatimespan = configs['timeCaptcha']
        funfunctions = configs['functionsFun']
        utilityfunctions = configs['functionsUtility']
        language = configs['language']
        publisherpost = configs['publisherPost']
        publisherask = configs['publisherAsk']
    return [FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask]


def Configurar(cookiebot, msg, chat_id, listaadmins, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    if str(msg['from']['username']) in listaadmins or str(msg['from']['username']) == "MekhyW":
        configs = GetConfig(chat_id)
        variables = f"FurBots: {configs[0]}\n sfw: {configs[1]}\n Sticker Spam Limit: {configs[2]}\n Time Without Sending Images: {configs[3]}\n Time Captcha: {configs[4]}\n Fun Functions: {configs[5]}\n Utility Functions: {configs[6]}\n Language: {configs[7]}\n Publisher Post: {configs[8]}\n Publisher Ask: {configs[9]}"
        try:
            cookiebot.sendMessage(msg['from']['id'],"Current settings:\n\n" + variables + '\n\nChoose the variable you would like to change', reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="Language",callback_data='k CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="FurBots",callback_data='a CONFIG {}'.format(str(chat_id)))], 
                                    [InlineKeyboardButton(text="Stickers limit",callback_data='b CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="🕒 Limbo",callback_data='c CONFIG {}'.format(str(chat_id)))], 
                                    [InlineKeyboardButton(text="🕒 CAPTCHA",callback_data='d CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="Fun Functions",callback_data='h CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="Utility Functions",callback_data='i CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="SFW Chat",callback_data='j CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="Publisher Post",callback_data='m CONFIG {}'.format(str(chat_id)))],
                                    [InlineKeyboardButton(text="Publisher Ask",callback_data='n CONFIG {}'.format(str(chat_id)))]
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
    chat_to_alter = msg['reply_to_message']['text'].split("\n")[0].split("= ")[1]
    current_configs = GetConfig(chat_to_alter)
    new_val = msg['text'].lower()
    if new_val or new_val in ["pt", "eng", "es"]:
        variable_to_be_altered = ""
        if "Bot language for the chat. Use pt for portuguese, eng for english or es for spanish" in msg['reply_to_message']['text']:
            current_configs[7] = new_val
        elif "Use 1 to not interfere with other furbots if they're in the group, or 0 if I'm the only one." in msg['reply_to_message']['text']:
            current_configs[0] = bool(int(new_val))
        elif "This is the maximum number of stickers allowed in a sequence by the bot. The next ones beyond that will be deleted to avoid spam. It's valid for everyone." in msg['reply_to_message']['text']:
            current_configs[2] = int(new_val)
        elif "This is the time for which new users in the group will not be able to send images (the bot automatically deletes)." in msg['reply_to_message']['text']:
            current_configs[3] = int(new_val)
        elif "This is the time new users have to solve Captcha. USE 0 TO TURN CAPTCHA OFF!" in msg['reply_to_message']['text']:
            current_configs[4] = int(new_val)
        elif "Use 1 to enable commands and fun functionality, or 0 for control/management functions only." in msg['reply_to_message']['text']:
            current_configs[5] = bool(int(new_val))
        elif "Use 1 to enable commands and utility features, or 0 to disable them." in msg['reply_to_message']['text']:
            current_configs[6] = bool(int(new_val))
        elif "Use 1 to indicate the chat is SFW, or 0 for NSFW." in msg['reply_to_message']['text']:
            current_configs[1] = bool(int(new_val))
        elif "Use 1 to allow the bot to post publications from other channels (only works if group has over 50 members), or 0 to not allow" in msg['reply_to_message']['text']:
            current_configs[8] = bool(int(new_val))
        elif "Use 1 if the bot should add posts sent in the group to the publisher queue, or 0 if not" in msg['reply_to_message']['text']:
            current_configs[9] = bool(int(new_val))
        PutRequestBackend(f"configs/{chat_id}", {"furbots": current_configs[0], "sfw": current_configs[1], "stickerSpamLimit": current_configs[2], "timeWithoutSendingImages": current_configs[3], "timeCaptcha": current_configs[4], "functionsFun": current_configs[5], "functionsUtility": current_configs[6], "language": current_configs[7], "publisherPost": current_configs[8], "publisherAsk": current_configs[9]})
        if variable_to_be_altered == "Language":
            SetLanguageComandos(cookiebot, chat_id, chat_to_alter, msg['text'].lower())
        cookiebot.sendMessage(chat_id, "Successfully changed the variable!", reply_to_message_id=msg['message_id'])
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
    elif query_data.startswith('m'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 to allow the bot to post publications from other channels (only works if group has over 50 members), or 0 to not allow\nREPLY THIS MESSAGE with the new variable value".format(query_data.split()[2]))
    elif query_data.startswith('n'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 if the bot should add posts sent in the group to the publisher queue, or 0 if not\nREPLY THIS MESSAGE with the new variable value".format(query_data.split()[2]))


def AtualizaBemvindo(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    PutRequestBackend(f"welcomes/{chat_id}", {"message": msg['text']})
    cookiebot.sendMessage(chat_id, "Welcome message updated! ✅", reply_to_message_id=msg['message_id'])
    DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))

def NovoBemvindo(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone joins the group", reply_to_message_id=msg['message_id'])


def AtualizaRegras(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    PutRequestBackend(f"rules/{chat_id}", {"rules": msg['text']})
    cookiebot.sendMessage(chat_id, "Updated rules message! ✅", reply_to_message_id=msg['message_id'])
    DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))

def NovasRegras(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone asks for the rules", reply_to_message_id=msg['message_id'])

def Regras(cookiebot, msg, chat_id, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    rules = GetRequestBackend(f"rules/{chat_id}")
    if 'error' in rules and rules['error'] == "Not Found":    
        Send(cookiebot, chat_id, "Ainda não há regras colocadas para esse grupo\nPara tal, use o /novasregras", msg, language)
    else:
        regras = rules['rules']
        if regras.endswith("@MekhyW"):
            cookiebot.sendMessage(chat_id, regras, reply_to_message_id=msg['message_id'])
        else:
            if language == 'pt':
                cookiebot.sendMessage(chat_id, regras+"\n\nDúvidas em relação ao bot? Mande para @MekhyW", reply_to_message_id=msg['message_id'])
            elif language == 'es':
                cookiebot.sendMessage(chat_id, regras+"\n\n¿Preguntas sobre el bot? Envíalo a @MekhyW", reply_to_message_id=msg['message_id'])
            else:
                cookiebot.sendMessage(chat_id, regras+"\n\nQuestions about the bot? Send to @MekhyW", reply_to_message_id=msg['message_id'])
