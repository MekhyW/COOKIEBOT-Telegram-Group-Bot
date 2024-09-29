from universal_funcs import send_message, send_chat_action, react_to_message, delete_message, get_request_backend, put_request_backend, post_request_backend, wait_open, set_bot_commands, leave_and_blacklist, ownerID
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
cache_configurations = {}
cache_admins = {}

def get_admins(cookiebot, chat_id, ignorecache=False):
    if chat_id in cache_admins and not ignorecache:
        admins = cache_admins[chat_id]
        return admins[0], admins[1], admins[2]
    listaadmins, listaadmins_id, listaadmins_status = [], [], []
    for admin in cookiebot.getChatAdministrators(chat_id):
        if 'username' in admin['user']:
            listaadmins.append(str(admin['user']['username']))
        listaadmins_id.append(str(admin['user']['id']))
        listaadmins_status.append(admin['status'])
    cache_admins[chat_id] = [listaadmins, listaadmins_id, listaadmins_status]
    return listaadmins, listaadmins_id, listaadmins_status

def set_language_commands(cookiebot, chat_id, chat_to_alter, language, is_alternate_bot=0, silent=False):
    wait_open(f"Static/Cookiebot_functions_{language}.txt")
    with open(f"Static/Cookiebot_functions_{language}.txt", "r", encoding='utf8') as text_file:
        lines = text_file.readlines()
    comandos = []
    for line in lines:
        if " - " in line:
            command = line.split(" - ")[0].strip()
            description = line.split(" - ")[1].replace("\n", "")
            if len(command.split()) == 1 and command.islower():
                comandos.append({'command': command, 'description': description})
    if language == "private":
        set_bot_commands(cookiebot, comandos, chat_to_alter, is_alternate_bot=is_alternate_bot)
    else:
        for lang in ['pt', 'es', 'eng']:
            if lang != language:
                set_bot_commands(cookiebot, comandos, chat_to_alter, is_alternate_bot=is_alternate_bot, language=lang)
        set_bot_commands(cookiebot, comandos, chat_to_alter, is_alternate_bot=is_alternate_bot, language=language)
        if silent:
            print(f"Comandos no chat com ID {chat_to_alter} alterados para o idioma {language}")
        else:
            send_message(cookiebot, chat_id, f"Comandos no chat com ID <b>{chat_to_alter}</b> alterados para o idioma <b>{language}</b>", language=language)

def set_private_commands(cookiebot, chat_id, is_alternate_bot=0):
    set_language_commands(cookiebot, chat_id, chat_id, "private", is_alternate_bot)

def get_config(cookiebot, chat_id, ignorecache=False, is_alternate_bot=0):
    if chat_id in cache_configurations and not ignorecache:
        return cache_configurations[chat_id]
    isBlacklisted = get_request_backend(f"blacklist/{chat_id}")
    if not 'error' in isBlacklisted:
        leave_and_blacklist(cookiebot, chat_id)
        send_message(cookiebot, ownerID, f"Auto-left\n{chat_id}")
        return
    FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = 1, 1, 5, 600, 300, 1, 1, "pt", 0, 1, "9999", 9999, 0
    configs = get_request_backend(f"configs/{chat_id}")
    if 'error' in configs and configs['error'] == "Not Found":
        post_request_backend(f"configs/{chat_id}", {'furbots': FurBots, 'sfw': sfw, 'stickerSpamLimit': stickerspamlimit, 
        'timeWithoutSendingImages': limbotimespan, 'timeCaptcha': captchatimespan, 'functionsFun': funfunctions, 'functionsUtility': utilityfunctions, 
        'language': language, 'publisherPost': publisherpost, 'publisherAsk': publisherask, 'threadPosts': threadPosts, 'maxPosts': maxPosts, 
        'publisherMembersOnly': publisherMembersOnly})
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
        threadPosts = configs['threadPosts']
        maxPosts = configs['maxPosts']
        publisherMembersOnly = configs['publisherMembersOnly']
    if captchatimespan < 30:
        captchatimespan = abs(captchatimespan)*60
    cache_configurations[chat_id] = [FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly]
    try:
        set_language_commands(cookiebot, chat_id, chat_id, language, is_alternate_bot=is_alternate_bot, silent=True)
    except Exception as e:
        print(e)
    return [FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly]

def configurar(cookiebot, msg, chat_id, listaadmins_id, language):
    send_chat_action(cookiebot, chat_id, 'typing')
    if str(msg['from']['id']) in listaadmins_id or str(msg['from']['id']) == str(ownerID):
        configs = get_config(cookiebot, chat_id)
        variables = f"FurBots: {configs[0]}\n sfw: {configs[1]}\n Sticker Spam Limit: {configs[2]}\n Time Without Sending Images: {configs[3]}\n Time Captcha: {configs[4]}\n Fun Functions: {configs[5]}\n Utility Functions: {configs[6]}\n Language: {configs[7]}\n Publisher Post: {configs[8]}\n Publisher Ask: {configs[9]}\n Thread Posts: {configs[10]}\n Max Posts: {configs[11]}"
        try:
            cookiebot.sendMessage(msg['from']['id'],"Current settings:\n\n" + variables + '\n\nChoose the variable you would like to change\n\n(If you want to change rules or welcome message, use /newrules or /newwelcome on the group)', reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="Language",callback_data=f'k CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="FurBots",callback_data=f'a CONFIG {chat_id}')], 
                                    [InlineKeyboardButton(text="Stickers limit",callback_data=f'b CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="🕒 Limbo",callback_data=f'c CONFIG {chat_id}')], 
                                    [InlineKeyboardButton(text="🕒 CAPTCHA",callback_data=f'd CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="Fun Functions",callback_data=f'h CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="Utility Functions",callback_data=f'i CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="SFW Chat",callback_data=f'j CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="Publisher Post",callback_data=f'm CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="Publisher Ask",callback_data=f'n CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="Thread Posts",callback_data=f'o CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="Max Posts",callback_data=f'p CONFIG {chat_id}')],
                                    [InlineKeyboardButton(text="Publisher Members Only",callback_data=f'q CONFIG {chat_id}')]
                                ]
                            ))
            send_message(cookiebot, chat_id, "Te mandei uma mensagem no chat privado para configurar!", msg, language)
        except Exception as e:
            send_message(cookiebot, chat_id, "Não consegui te mandar o menu de configuração\n<blockquote>Mande uma mensagem no meu chat privado para que eu consiga fazer isso)</blockquote>" , msg, language)
            print(e)
    else:
        send_message(cookiebot, chat_id, "Você não tem permissão para configurar o bot!\n<blockquote>Você está falando como usuário e não como canal? A permissão 'permanecer anônimo' deve estar desligada!</blockquote>", msg, language)
        with open('Static/remove_anonymous_tutorial.mp4', 'rb') as video:
            cookiebot.sendVideo(chat_id, video)

def configurar_set(cookiebot, msg, chat_id, is_alternate_bot=0):
    send_chat_action(cookiebot, chat_id, 'typing')
    chat_to_alter = msg['reply_to_message']['text'].split("\n")[0].split("= ")[1]
    current_configs = get_config(cookiebot, chat_to_alter)
    new_val = msg['text'].lower()
    if new_val or new_val in ["pt", "eng", "es"]:
        if "Bot language for the chat. Use pt for portuguese, eng for english or es for spanish" in msg['reply_to_message']['text']:
            current_configs[7] = new_val
            set_language_commands(cookiebot, chat_id, chat_to_alter, new_val, is_alternate_bot=is_alternate_bot)
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
        elif "Use 1 to allow the bot to post publications from other channels" in msg['reply_to_message']['text']:
            current_configs[8] = bool(int(new_val))
        elif "Use 1 if the bot should add posts sent in the group to the publisher queue, or 0 if not" in msg['reply_to_message']['text']:
            current_configs[9] = bool(int(new_val))
        elif "This is the id of the topic I should publish posts to if your chat has topics enabled (you can find it out with /analysis command)" in msg['reply_to_message']['text']:
            current_configs[10] = int(new_val)
        elif "This is the maximum number of posts I should publish in the chat per day" in msg['reply_to_message']['text']:
            current_configs[11] = int(new_val)
        elif "Use 1 if the bot should only allow members of the channel to use the publisher, or 0 if not" in msg['reply_to_message']['text']:
            current_configs[12] = bool(int(new_val))
        put_request_backend(f"configs/{chat_to_alter}", {"furbots": current_configs[0], "sfw": current_configs[1], 
        "stickerSpamLimit": current_configs[2], "timeWithoutSendingImages": current_configs[3], "timeCaptcha": current_configs[4], 
        "functionsFun": current_configs[5], "functionsUtility": current_configs[6], "language": current_configs[7], 
        "publisherPost": current_configs[8], "publisherAsk": current_configs[9], "threadPosts": current_configs[10], "maxPosts": current_configs[11],
        "publisherMembersOnly": current_configs[12]})
        cache_configurations[chat_id] = current_configs
        react_to_message(msg, '👍', is_alternate_bot=is_alternate_bot)
        cookiebot.sendMessage(chat_id, "Successfully changed the variable!\nSend /reload in the chat if the old config persists")
    else:
        cookiebot.sendMessage(chat_id, "ERROR: invalid input\nTry again", reply_to_message_id=msg['message_id'])

def config_variable_button(cookiebot, msg, query_data):
    chat = query_data.split()[2]
    if query_data.startswith('k'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f'Chat = {chat}\nBot language for the chat. Use pt for portuguese, eng for english or es for spanish\n\nREPLY THIS MESSAGE with the new variable value')
    if query_data.startswith('a'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nUse 1 to not interfere with other furbots if they're in the group, or 0 if I'm the only one.\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('b'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nThis is the maximum number of stickers allowed in a sequence by the bot. The next ones beyond that will be deleted to avoid spam. It's valid for everyone.\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('c'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f'Chat = {chat}\nThis is the time for which new users in the group will not be able to send images (the bot automatically deletes).\n\nREPLY THIS MESSAGE with the new variable value')
    elif query_data.startswith('d'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f'Chat = {chat}\nThis is the time new users have to solve Captcha. USE 0 TO TURN CAPTCHA OFF!\n\nREPLY THIS MESSAGE with the new variable value')
    elif query_data.startswith('h'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nUse 1 to enable commands and fun functionality, or 0 for control/management functions only.\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('i'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nUse 1 to enable commands and utility features, or 0 to disable them.\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('j'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nUse 1 to indicate the chat is SFW, or 0 for NSFW.\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('m'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nUse 1 to allow the bot to post publications from other channels (only works if group has over 50 members), or 0 to not allow\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('n'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nUse 1 if the bot should add posts sent in the group to the publisher queue, or 0 if not\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('o'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nThis is the id of the topic I should publish posts to if your chat has topics enabled (you can find it out with /analysis command)\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('p'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nThis is the maximum number of posts I should publish in the chat per day\n\nREPLY THIS MESSAGE with the new variable value")
    elif query_data.startswith('q'):
        cookiebot.sendMessage(msg['message']['chat']['id'], f"Chat = {chat}\nUse 1 if the bot should only allow members of the channel to use the publisher, or 0 if not\n\nREPLY THIS MESSAGE with the new variable value")

def set_language(cookiebot, msg, chat_id, language_code):
    if 'pt' in language_code:
        msg['text'] = "pt"
    elif 'es' in language_code:
        msg['text'] = "es"
    else:
        msg['text'] = "eng"
    msg['reply_to_message'] = {}
    msg['reply_to_message']['text'] = f'Chat = {chat_id}\nBot language for the chat. Use pt for portuguese, eng for english or es for spanish'
    configurar_set(cookiebot, msg, ownerID)

def update_welcome_message(cookiebot, msg, chat_id, listaadmins_id, is_alternate_bot=0):
    if str(msg['from']['id']) not in listaadmins_id:
        send_message(cookiebot, chat_id, "You are not a group admin!", msg_to_reply=msg)
        return
    send_chat_action(cookiebot, chat_id, 'typing')
    req = put_request_backend(f"welcomes/{chat_id}", {"message": msg['text']})
    if 'error' in req and req['error'] == "Not Found":
        post_request_backend(f"welcomes/{chat_id}", {"message": msg['text']})
    react_to_message(msg, '👍', is_alternate_bot=is_alternate_bot)
    cookiebot.sendMessage(chat_id, "Welcome message updated! ✅", reply_to_message_id=msg['message_id'])
    delete_message(cookiebot, telepot.message_identifier(msg['reply_to_message']))

def new_welcome_message(cookiebot, msg, chat_id):
    send_chat_action(cookiebot, chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone joins the group.\n\nYou can include <user> to be replaced with the user name", reply_to_message_id=msg['message_id'])

def update_rules_message(cookiebot, msg, chat_id, listaadmins_id, is_alternate_bot=0):
    if str(msg['from']['id']) not in listaadmins_id:
        send_message(cookiebot, chat_id, "You are not a group admin!", msg_to_reply=msg)
        return
    send_chat_action(cookiebot, chat_id, 'typing')
    req = put_request_backend(f"rules/{chat_id}", {"rules": msg['text']})
    if 'error' in req and req['error'] == "Not Found":
        post_request_backend(f"rules/{chat_id}", {"rules": msg['text']})
    react_to_message(msg, '👍', is_alternate_bot=is_alternate_bot)
    cookiebot.sendMessage(chat_id, "Updated rules message! ✅", reply_to_message_id=msg['message_id'])
    delete_message(cookiebot, telepot.message_identifier(msg['reply_to_message']))

def new_rules_message(cookiebot, msg, chat_id):
    send_chat_action(cookiebot, chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone asks for the rules", reply_to_message_id=msg['message_id'])
