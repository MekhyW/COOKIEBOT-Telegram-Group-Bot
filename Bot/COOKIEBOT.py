from universal_funcs import *
isBombot = False
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
        FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask = 0, 1, 5, 600, 300, 1, 1, 'pt', 0, 1
        if chat_type == 'private' and 'reply_to_message' not in msg:
            SetComandosPrivate(cookiebot, chat_id)
            if 'text' in msg:
                if msg['text'].startswith(("/grupos", "/groups")) and 'from' in msg and msg['from']['id'] == mekhyID:
                    Grupos(cookiebot, msg, chat_id, 'eng')
                elif msg['text'].startswith(("/comandos", "/commands")):
                    Comandos(cookiebot, msg, chat_id, 'eng')
                elif msg['text'] == "/stop" and 'from' in msg and msg['from']['id'] == mekhyID:
                    os._exit(0)
                elif msg['text'] == "/restart" and 'from' in msg and msg['from']['id'] == mekhyID:
                    os.execl(sys.executable, sys.executable, *sys.argv)
                elif msg['text'].startswith("/leave") and 'from' in msg and msg['from']['id'] == mekhyID:
                    targetId = msg['text'].split()[1]
                    LeaveAndBlacklist(cookiebot, targetId)
                    DeleteRequestBackend(f'registers/{targetId}')
            if isBombot:
                cookiebot.sendMessage(chat_id, "Olá, sou o BomBot!\nSou um clone do @CookieMWbot criado para os chats da Brasil FurFest (BFF)\n\nSe tiver qualquer dúvida ou quiser a lista de comandos completa, mande uma mensagem para o @MekhyW")
            else:
                cookiebot.sendMessage(chat_id, "Olá, sou o CookieBot!\n\nAtualmente estou presente em *98* chats!\nSinta-se à vontade para me adicionar no seu\n\nSou um bot com IA de conversa, Defesa de grupos, Pesquisa, Conteúdo customizado e Speech-to-text.\nUse /comandos para ver todas as minhas funcionalidades\n\nSe tiver qualquer dúvida ou quiser que algo seja adicionado, mande uma mensagem para o @MekhyW",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    #[InlineKeyboardButton(text="Acesse o Site 🌐", url="https://cookiebot-website.vercel.app/")],
                    [InlineKeyboardButton(text="Adicionar a um Grupo 👋", url="https://t.me/CookieMWbot?startgroup=new")],
                    [InlineKeyboardButton(text="Grupo de teste/assistência 🧪", url="https://t.me/+mX6W3tGXPew2OTIx")]
                ]))
        else:
            if chat_type != 'private':
                listaadmins, listaadmins_id = GetAdmins(cookiebot, msg, chat_id)
                FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask = GetConfig(chat_id)
                CheckNewName(msg, chat_id)
            if content_type == "new_chat_member":
                if 'username' in msg['new_chat_participant'] and msg['new_chat_participant']['username'] in ["MekhysBombot", "CookieMWbot"]:
                    isBlacklisted = GetRequestBackend(f"blacklist/{chat_id}")
                    if not 'error' in isBlacklisted:
                        LeaveAndBlacklist(cookiebot, chat_id)
                        cookiebot.sendMessage(mekhyID, f"Auto-left:\n{chat_id}")
                        return
                    cookiebot.sendMessage(mekhyID, f"Added:\n{cookiebot.getChat(chat_id)}")
                if msg['new_chat_participant']['id'] != cookiebot.getMe()['id'] and not CheckCAS(cookiebot, msg, chat_id, language) and not CheckRaider(cookiebot, msg, chat_id, language) and not CheckHumanFactor(cookiebot, msg, chat_id, language) and not CheckBlacklist(cookiebot, msg, chat_id, language):
                    if captchatimespan > 0 and ("CookieMWbot" in listaadmins or "MekhysBombot" in listaadmins):
                        Captcha(cookiebot, msg, chat_id, captchatimespan, language)
                    else:
                        Bemvindo(cookiebot, msg, chat_id, limbotimespan, language)
            elif content_type == "left_chat_member":
                left_chat_member(msg, chat_id)
            elif content_type == "voice":
                if utilityfunctions == True:
                    r = requests.get(f"https://api.telegram.org/file/bot{cookiebotTOKEN}/{cookiebot.getFile(msg['voice']['file_id'])['file_path']}", allow_redirects=True, timeout=10)
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
                if 'sender_chat' in msg and 'from' in msg and msg['from']['first_name'] == 'Telegram' and 'caption' in msg and publisherask == True:
                    AskPublisher(cookiebot, msg, chat_id, language)
            elif content_type == "video":
                if sfw == 1 and funfunctions == True:
                    AddtoRandomDatabase(msg, chat_id)
                if 'sender_chat' in msg and 'from' in msg and msg['from']['first_name'] == 'Telegram' and 'caption' in msg and publisherask == True:
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
                if msg['text'].startswith("/leave") and 'from' in msg and msg['from']['id'] == mekhyID:
                    LeaveAndBlacklist(cookiebot, chat_id)
                elif msg['text'].startswith(("/análise", "/análisis", "/analysis")):
                    if 'reply_to_message' in msg:
                        Analyze(cookiebot, msg, chat_id, language)
                    else:
                        Send(cookiebot, chat_id, "Responda uma mensagem com o comando para analisar", msg, language)
                elif msg['text'].startswith(("/pesquisaimagem", "/searchimage", "/buscarimagen")):
                    if 'reply_to_message' in msg:
                        ReverseImageSearch(cookiebot, msg['reply_to_message'], chat_id, language)
                    else:
                        Send(cookiebot, chat_id, "Responda uma imagem com o comando para procurar a fonte", msg, language)
                elif msg['text'].startswith(("/aleatorio", "/aleatório", "/random")) and funfunctions == True:
                    ReplyAleatorio(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/meme") and funfunctions == True:
                    Meme(cookiebot, msg, chat_id, language)
                elif (msg['text'].startswith(("/dado", "/dice")) or (msg['text'].lower().startswith("/d") and msg['text'].replace("@CookieMWbot", '').split()[0][2:].isnumeric())) and funfunctions == True:
                    Dado(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/idade", "/age", "/edad")) and funfunctions == True:
                    Idade(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/genero", "/gender")) and funfunctions == True:
                    Genero(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/shippar", "/ship")) and funfunctions == True:
                    Shippar(cookiebot, msg, chat_id, language)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone joins the group":
                    if str(msg['from']['username']) in listaadmins:
                        AtualizaBemvindo(cookiebot, msg, chat_id)
                    else:
                        cookiebot.sendMessage(chat_id, "You are not a group admin!", reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith(("/novobemvindo", "/newwelcome", "/nuevabienvenida")):
                    NovoBemvindo(cookiebot, msg, chat_id)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone asks for the rules":
                    if str(msg['from']['username']) in listaadmins:
                        AtualizaRegras(cookiebot, msg, chat_id)
                    else:
                        cookiebot.sendMessage(chat_id, "You are not a group admin!", reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith(("/novasregras", "/newrules", "/nuevasreglas")):
                    NovasRegras(cookiebot, msg, chat_id)
                elif msg['text'].startswith(("/regras", "/rules", "/reglas")) and FurBots == False:
                    Regras(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/tavivo", "/isalive", "/estavivo")):
                    TaVivo(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith("/everyone"):
                    Everyone(cookiebot, msg, chat_id, listaadmins, language)
                elif msg['text'].startswith("/adm"):
                    Adm(cookiebot, msg, chat_id, listaadmins)
                elif msg['text'].startswith(("/comandos", "/commands")):
                    Comandos(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/hoje", "/today", "/hoy")) and funfunctions == True and FurBots == False:
                    Hoje(cookiebot, msg, chat_id, language)
                elif (msg['text'].startswith("/cheiro") or msg['text'].startswith("/smell")) and funfunctions == True and FurBots == False:
                    Cheiro(cookiebot, msg, chat_id, language)
                elif any(x in msg['text'].lower() for x in ['eu faço', 'eu faco', 'i do', 'debo hacer']) and '?' in msg['text'] and funfunctions == True and FurBots == False:
                    QqEuFaço(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/ideiadesenho", "/drawingidea", "/ideadibujo")) and utilityfunctions == True:
                    IdeiaDesenho(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/qualquercoisa", "/anything", "/cualquiercosa")) and utilityfunctions == True:
                    PromptQualquerCoisa(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/configurar", "/configure")):
                    Configurar(cookiebot, msg, chat_id, listaadmins, language)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "REPLY THIS MESSAGE with the new variable value" in msg['reply_to_message']['text']:
                    ConfigurarSettar(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/") and " " not in msg['text'] and os.path.exists("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')) and utilityfunctions == True:
                    CustomCommand(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/") and "//" not in msg['text'] and (len(msg['text'].split('@')) < 2 or msg['text'].split('@')[1] in ['CookieMWbot', 'MekhysBombot']) and (FurBots==False or msg['text'] not in open("Static/FurBots_functions.txt", "r+", encoding='utf-8').read()) and utilityfunctions == True:
                    QualquerCoisa(cookiebot, msg, chat_id, sfw, language)
                elif (msg['text'].lower().startswith("cookiebot") or ('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot')) and any(x in msg['text'].lower() for x in ['quem', 'who', 'quién', 'quien']) and ("?" in msg['text']) and funfunctions == True:
                    Quem(cookiebot, msg, chat_id, language)
                elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and str(round(captchatimespan/60)) in msg['reply_to_message']['caption']:
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan, language)
                elif (('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and 'text' in msg['reply_to_message']) or "cookiebot" in msg['text'].lower() or "@CookieMWbot" in msg['text']) and funfunctions == True:
                    AnswerFinal = InteligenciaArtificial(cookiebot, msg, chat_id, language)
                    cookiebot.sendMessage(chat_id, AnswerFinal, reply_to_message_id=msg['message_id'])
                else:
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan, language)
                    CheckCaptcha(cookiebot, msg, chat_id, captchatimespan, language)
            if chat_type != 'private' and 'text' in msg:
                StickerCooldownUpdates(msg, chat_id)
            run_unnatendedthreads()
    except TooManyRequestsError:
        return
    except (UnauthorizedError, BotWasKickedError, BotWasBlockedError, MigratedToSupergroupChatError, NotEnoughRightsError) as e:
        print(e)
    except:
        if 'ConnectionResetError' in traceback.format_exc():
            handle(msg)
        else:
            Send(cookiebot, chat_id, "❗ERRO❗--Por favor, tente novamente.")
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
            cookiebot.sendMessage(mekhyID, str(msg))
    finally:
        if not isBombot:
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
        print(f"{len(unnatended_threads)} threads are still unnatended")
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
    try:
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)
        try:
            chat_id = msg['message']['reply_to_message']['chat']['id']
            listaadmins, listaadmins_id = GetAdmins(cookiebot, msg, chat_id)
        except Exception as e:
            print(e)
            chat_id = from_id
            listaadmins_id = []
        if 'CONFIG' in query_data:
            ConfigVariableButton(cookiebot, msg, query_data)
        elif 'Pub' in query_data and (str(from_id) in listaadmins_id or str(from_id) == str(mekhyID)):
            if query_data.startswith('SendToApproval'):
                AskApproval(cookiebot, query_data, from_id)
            elif query_data.startswith('Approve'):
                SchedulePost(cookiebot, query_data)
            DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
        elif query_data == 'CAPTCHA' and (str(from_id) in listaadmins_id or str(from_id) == str(mekhyID)):
            SolveCaptcha(cookiebot, msg, chat_id, True)
            DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
        run_unnatendedthreads()
    except:
        if 'ConnectionResetError' in traceback.format_exc():
            handle_query(msg)
        else:
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
            cookiebot.sendMessage(mekhyID, str(msg))
        

MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()