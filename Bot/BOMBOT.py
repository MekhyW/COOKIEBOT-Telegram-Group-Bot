from universal_funcs import *
isBombot = True
from Configurations import *
from GroupShield import *
from UserRegisters import *
from Cooldowns import *
from NaturalLanguage import *
from SocialContent import *
from Audio import *
from Miscellaneous import *
from Publisher import *
import threading, gc
unnatended_threads = list()

if isBombot:
    cookiebot = telepot.Bot(bombotTOKEN)
else:
    cookiebot = telepot.Bot(cookiebotTOKEN)
updates = cookiebot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    cookiebot.getUpdates(offset=last_update_id+1)

startPublisher(isBombot)
cookiebot.sendMessage(mekhyID, 'I am online')

def thread_function(msg):
    try:
        if any(key in msg for key in ['dice', 'poll', 'voice_chat_started', 'voice_chat_ended']):
            return
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id, msg['message_id'])
        FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions = 0, 1, 5, 600, 300, 1, 1
        if chat_type == 'private' and 'reply_to_message' not in msg:
            SetComandosPrivate(cookiebot, chat_id)
            if 'text' in msg:
                if msg['text'].startswith(tuple(["/grupos", "/groups"])) and msg['from']['id'] == mekhyID:
                    Grupos(cookiebot, msg, chat_id, 'eng')
                elif msg['text'].startswith(tuple(["/comandos", "/commands"])):
                    Comandos(cookiebot, msg, chat_id, 'eng')
                elif msg['text'] == "/stop" and msg['from']['id'] == mekhyID:
                    os._exit(0)
                elif msg['text'] == "/restart" and msg['from']['id'] == mekhyID:
                    os.execl(sys.executable, sys.executable, *sys.argv)
                elif msg['text'].startswith("/leave") and msg['from']['id'] == mekhyID:
                    LeaveAndBlacklist(cookiebot, msg['text'].split()[1])
                    os.remove('Registers/{}.txt'.format(msg['text'].split()[1]))
            if isBombot:
                cookiebot.sendMessage(chat_id, "Olá, sou o BomBot!\nSou um clone do @CookieMWbot criado para os chats da Brasil FurFest (BFF)\n\nSe tiver qualquer dúvida ou quiser a lista de comandos completa, mande uma mensagem para o @MekhyW")
            else:
                cookiebot.sendMessage(chat_id, "Olá, sou o CookieBot!\n\nAtualmente estou presente em *87* chats!\nSinta-se à vontade para me adicionar no seu\n\nSou um bot com IA de conversa, Defesa de grupos, Pesquisa, Conteúdo customizado e Speech-to-text.\nUse /comandos para ver todas as minhas funcionalidades\n\nSe tiver qualquer dúvida ou quiser que algo seja adicionado, mande uma mensagem para o @MekhyW",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Adicionar ao Grupo", url="https://t.me/CookieMWbot?startgroup=new")],
                    [InlineKeyboardButton(text="Grupo de teste/assistência", url="https://t.me/+mX6W3tGXPew2OTIx")]
                ]))
        else:
            if chat_type != 'private':
                listaadmins, listaadmins_id = GetAdmins(cookiebot, msg, chat_id)
                FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language = GetConfig(chat_id)
                CheckNewName(msg, chat_id)
                if isBombot:
                    lastmessagedate, lastmessagetime = CheckLastMessageDatetime(msg, chat_id)
            if content_type == "new_chat_member":
                if 'username' in msg['new_chat_participant'] and msg['new_chat_participant']['username'] in ["MekhysBombot", "CookieMWbot"]:
                    wait_open("Blacklist.txt")
                    text = open("Blacklist.txt", 'r', encoding='utf-8')
                    lines = text.readlines()
                    text.close()
                    for line in lines:
                        if str(chat_id) in line:
                            LeaveAndBlacklist(cookiebot, chat_id)
                            cookiebot.sendMessage(mekhyID, "Auto-left:\n{}".format(chat_id))
                            return
                    cookiebot.sendMessage(mekhyID, "Added:\n{}".format(cookiebot.getChat(chat_id)))
                if msg['new_chat_participant']['id'] != cookiebot.getMe()['id'] and not CheckCAS(cookiebot, msg, chat_id, language) and not CheckRaider(cookiebot, msg, chat_id, language) and not CheckHumanFactor(cookiebot, msg, chat_id, language) and not CheckBlacklist(cookiebot, msg, chat_id, language):
                    if captchatimespan > 0 and ("CookieMWbot" in listaadmins or "MekhysBombot" in listaadmins):
                        Captcha(cookiebot, msg, chat_id, captchatimespan, language)
                    else:
                        Bemvindo(cookiebot, msg, chat_id, limbotimespan, language)
            elif content_type == "left_chat_member":
                left_chat_member(msg, chat_id)
            elif content_type == "voice":
                if utilityfunctions == True:
                    r = requests.get("https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, cookiebot.getFile(msg['voice']['file_id'])['file_path']), allow_redirects=True, timeout=10)
                    duration = int(msg['voice']['duration'])
                    if duration >= 10 and duration <= 240:
                        Speech_to_text(cookiebot, msg, chat_id, sfw, r.content, language)
                    Identify_music(cookiebot, msg, chat_id, r.content, language)
            elif content_type == "audio":
                pass
            elif content_type == "photo":
                if sfw == 1 and funfunctions == True:
                    photo_id = msg['photo'][-1]['file_id']
                    AddtoRandomDatabase(msg, chat_id, photo_id)
                if 'sender_chat' in msg and msg['from']['first_name'] == 'Telegram' and 'caption' in msg and not isBombot:
                    AskPublisher(cookiebot, msg, chat_id, language)
            elif content_type == "video":
                if sfw == 1 and funfunctions == True:
                    AddtoRandomDatabase(msg, chat_id)
                if 'sender_chat' in msg and msg['from']['first_name'] == 'Telegram' and 'caption' in msg and not isBombot:
                    AskPublisher(cookiebot, msg, chat_id, language)
            elif content_type == "document":
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and funfunctions == True:
                    ReplySticker(cookiebot, msg, chat_id)
            elif content_type == "sticker":
                Sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language)
                if sfw == 1:
                    AddtoStickerDatabase(msg, chat_id)
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and funfunctions == True:
                    ReplySticker(cookiebot, msg, chat_id)
            elif 'text' in msg:
                if msg['text'].startswith("/leave") and msg['from']['id'] == mekhyID:
                    LeaveAndBlacklist(cookiebot, chat_id)
                elif isBombot and msg['text'].startswith("/") and " " not in msg['text'] and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and str(datetime.date.today()) == lastmessagedate and float(lastmessagetime)+60 >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                    CooldownAction(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/análise", "/análisis", "/analysis"])):
                    if 'reply_to_message' in msg:
                        Analyze(cookiebot, msg, chat_id, language)
                    else:
                        Send(cookiebot, chat_id, "Responda uma mensagem com o comando para analisar", msg, language)
                elif msg['text'].startswith(tuple(["/aleatorio", "/aleatório", "/random"])) and funfunctions == True:
                    ReplyAleatorio(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/meme") and funfunctions == True:
                    Meme(cookiebot, msg, chat_id, language)
                elif (msg['text'].startswith(tuple(["/dado", "/dice"])) or (msg['text'].lower().startswith("/d") and msg['text'].replace("@CookieMWbot", '').split()[0][2:].isnumeric())) and funfunctions == True:
                    Dado(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/idade", "/age", "/edad"])) and funfunctions == True:
                    Idade(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/genero", "/gender"])) and funfunctions == True:
                    Genero(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/shippar", "/ship"])) and funfunctions == True:
                    Shippar(cookiebot, msg, chat_id, language)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone joins the group":
                    if str(msg['from']['username']) in listaadmins:
                        AtualizaBemvindo(cookiebot, msg, chat_id)
                    else:
                        cookiebot.sendMessage(chat_id, "You are not a group admin!", reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith(tuple(["/novobemvindo", "/newwelcome", "/nuevabienvenida"])):
                    NovoBemvindo(cookiebot, msg, chat_id)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone asks for the rules":
                    if str(msg['from']['username']) in listaadmins:
                        AtualizaRegras(cookiebot, msg, chat_id)
                    else:
                        cookiebot.sendMessage(chat_id, "You are not a group admin!", reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith(tuple(["/novasregras", "/newrules", "/nuevasreglas"])):
                    NovasRegras(cookiebot, msg, chat_id)
                elif msg['text'].startswith(tuple(["/regras", "/rules", "/reglas"])):
                    Regras(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/tavivo", "/isalive", "/estavivo"])):
                    TaVivo(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith("/everyone"):
                    Everyone(cookiebot, msg, chat_id, listaadmins, language)
                elif msg['text'].startswith("/adm"):
                    Adm(cookiebot, msg, chat_id, listaadmins)
                elif msg['text'].startswith(tuple(["/comandos", "/commands"])):
                    Comandos(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/hoje", "/today", "/hoy"])) and funfunctions == True:
                    if FurBots == False:
                        Hoje(cookiebot, msg, chat_id, language)
                    else:
                        return
                elif (msg['text'].startswith("/cheiro") or msg['text'].startswith("/smell")) and funfunctions == True:
                    if FurBots == False:
                        Cheiro(cookiebot, msg, chat_id, language)
                    else:
                        return
                elif any(x in msg['text'].lower() for x in ['eu faço', 'eu faco', 'i do', 'debo hacer']) and '?' in msg['text'] and funfunctions == True and FurBots == False:
                    QqEuFaço(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/ideiadesenho", "/drawingidea", "/ideadibujo"])) and utilityfunctions == True:
                    IdeiaDesenho(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/contato", "/contact", "/contacto"])):
                    Contato(cookiebot, msg, chat_id)
                elif msg['text'].startswith(tuple(["/qualquercoisa", "/anything", "/cualquiercosa"])) and utilityfunctions == True:
                    PromptQualquerCoisa(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(tuple(["/configurar", "/configure"])):
                    Configurar(cookiebot, msg, chat_id, listaadmins, language)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "REPLY THIS MESSAGE with the new variable value" in msg['reply_to_message']['text']:
                    ConfigurarSettar(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/") and " " not in msg['text'] and os.path.exists("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')) and utilityfunctions == True:
                    CustomCommand(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/") and "//" not in msg['text'] and (len(msg['text'].split('@')) < 2 or msg['text'].split('@')[1] in ['CookieMWbot', 'MekhysBombot']) and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and utilityfunctions == True:
                    QualquerCoisa(cookiebot, msg, chat_id, sfw, language)
                elif (msg['text'].lower().startswith("cookiebot") or ('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot')) and any(x in msg['text'].lower() for x in ['quem', 'who', 'quién', 'quien']) and ("?" in msg['text']) and funfunctions == True:
                    Quem(cookiebot, msg, chat_id, language)
                elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and str(round(captchatimespan/60)) in msg['reply_to_message']['caption']:
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan, language)
                elif (('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and 'text' in msg['reply_to_message']) or "cookiebot" in msg['text'].lower() or "@CookieMWbot" in msg['text']) and funfunctions == True:
                    if not OnSay(cookiebot, msg, chat_id):
                        AnswerFinal = InteligenciaArtificial(cookiebot, msg, chat_id, language)
                        cookiebot.sendMessage(chat_id, AnswerFinal, reply_to_message_id=msg['message_id'])
                else:
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan, language)
                    CheckCaptcha(cookiebot, msg, chat_id, captchatimespan, language)
                    OnSay(cookiebot, msg, chat_id)
            if chat_type != 'private' and isBombot:
                CmdCooldownUpdates(msg, chat_id, lastmessagetime)
            if chat_type != 'private' and 'text' in msg:
                StickerCooldownUpdates(msg, chat_id)
            run_unnatendedthreads()
    except:
        if 'ConnectionResetError' in traceback.format_exc():
            handle(msg)
        else:
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
            cookiebot.sendMessage(mekhyID, str(msg))
    finally:
        SchedulerPull(cookiebot)

def run_unnatendedthreads():
    global unnatended_threads
    num_running_threads = threading.active_count()
    num_max_threads = 10
    for unnatended_thread in unnatended_threads:
        if unnatended_thread.is_alive():
            unnatended_threads.remove(unnatended_thread)
        elif num_running_threads < num_max_threads:
            unnatended_thread.start()
            num_running_threads += 1
            try:
                unnatended_threads.remove(unnatended_thread)
            except ValueError:
                pass
    if len(unnatended_threads) > 2 * num_max_threads:
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif len(unnatended_threads) > 0:
        print("{} threads are still unnatended".format(len(unnatended_threads)))
    gc.collect()

def handle(msg):
    try:
        global unnatended_threads
        new_thread = threading.Thread(target=thread_function, args=(msg,))
        unnatended_threads.append(new_thread)
        run_unnatendedthreads()
    except:
        cookiebot.sendMessage(mekhyID, traceback.format_exc())

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    try:
        chat_id = msg['message']['reply_to_message']['chat']['id']
        listaadmins, listaadmins_id = GetAdmins(cookiebot, msg, chat_id)
    except:
        chat_id = from_id
        listaadmins = []
        listaadmins_id = []
    if 'CONFIG' in query_data:
        ConfigVariableButton(cookiebot, msg, query_data)
    elif 'Pub' in query_data and (str(from_id) in listaadmins_id or str(from_id) == str(mekhyID)):
        if query_data.startswith('SendToApproval'):
            AskApproval(cookiebot, query_data)
        elif query_data.startswith('Approve'):
            SchedulePost(cookiebot, query_data)
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
    elif query_data == 'CAPTCHA' and (str(from_id) in listaadmins_id or str(from_id) == str(mekhyID)):
        SolveCaptcha(cookiebot, msg, chat_id, True)
        DeleteMessage(telepot.message_identifier(msg['message']))
    run_unnatendedthreads()
        

MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()