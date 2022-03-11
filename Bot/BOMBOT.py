from universal_funcs import *
#cookiebot = telepot.Bot(cookiebotTOKEN)
cookiebot = telepot.Bot(bombotTOKEN)
from Configurations import *
from GroupShield import *
from Publisher import *
from UserRegisters import *
from Cooldowns import *
from NaturalLanguage import *
from SocialContent import *
from Audio import *
from Miscellaneous import *
import threading, gc
unnatended_threads = list()

updates = cookiebot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    cookiebot.getUpdates(offset=last_update_id+1)

cookiebot.sendMessage(mekhyID, 'I am online')

def thread_function(msg):
    try:
        if any(key in msg for key in ['dice', 'poll', 'voice_chat_started', 'voice_chat_ended']) or 'from' not in msg:
            return
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id, msg['message_id'])
        publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions = 1, 0, 1, 5, 600, 300, 1, 1
        if chat_type == 'private' and 'reply_to_message' not in msg:
            if 'text' in msg and msg['text'] == "/stop" and msg['from']['id'] == mekhyID:
                os._exit(0)
            elif 'text' in msg and msg['text'] == "/restart" and msg['from']['id'] == mekhyID:
                os.execl(sys.executable, sys.executable, *sys.argv)
            elif content_type in ['photo', 'video', 'document']:
                ReceivePublisher(cookiebot, msg, chat_id)
            else:
                cookiebot.sendMessage(chat_id, "Olá, sou o CookieBot!\n\n**Para agendar uma postagem, envie a sua mensagem por aqui (lembrando que deve conter uma foto, vídeo, gif ou documento)**\n\nSou um bot com IA de conversa, conteúdo infinito, conteúdo customizado e speech-to-text.\nSe quiser me adicionar no seu chat ou obter a lista de comandos comentada, mande uma mensagem para o @MekhyW")
        else:
            if chat_type != 'private':
                listaadmins, listaadmins_id = GetAdmins(cookiebot, msg, chat_id)
                publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions = GetConfig(chat_id)
                CheckNewName(msg, chat_id)
                lastmessagedate, lastmessagetime = CheckLastMessageDatetime(msg, chat_id)
                PublisherController(msg, chat_id, publisher)
            if content_type == "new_chat_member":
                if CheckCAS(cookiebot, msg, chat_id) == False and CheckRaider(cookiebot, msg, chat_id) == False:
                    if captchatimespan > 0 and ("CookieMWbot" in listaadmins or "MekhysBombot" in listaadmins):
                        Captcha(cookiebot, msg, chat_id, captchatimespan)
                    else:
                        Bemvindo(cookiebot, msg, chat_id, limbotimespan)
            elif content_type == "left_chat_member":
                left_chat_member(msg, chat_id)
            elif content_type == "voice":
                if utilityfunctions == True:
                    Speech_to_text(cookiebot, msg, chat_id, sfw)
            elif content_type == "audio":
                pass
            elif content_type == "photo":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
            elif content_type == "video":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
            elif content_type == "document":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and funfunctions == True:
                    ReplySticker(cookiebot, msg, chat_id)
            elif content_type == "sticker":
                Sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit)
                if sfw == 1:
                    AddtoStickerDatabase(msg, chat_id)
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and funfunctions == True:
                    ReplySticker(cookiebot, msg, chat_id)
            elif 'text' in msg:
                if cookiebot.getMe()['username'] == "MekhysBombot" and msg['text'].startswith("/") and " " not in msg['text'] and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and str(datetime.date.today()) == lastmessagedate and float(lastmessagetime)+60 >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                    CooldownAction(cookiebot, msg, chat_id)
                elif (msg['text'].startswith("/aleatorio") or msg['text'].startswith("/aleatório")) and funfunctions == True:
                    ReplyAleatorio(cookiebot, msg, chat_id)
                elif (msg['text'].startswith("/dado") or (msg['text'].lower().startswith("/d") and msg['text'].replace("@CookieMWbot", '').split()[0][2:].isnumeric())) and funfunctions == True:
                    Dado(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/idade") and funfunctions == True:
                    Idade(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/genero") and funfunctions == True:
                    Genero(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/shippar") and funfunctions == True:
                    Shippar(cookiebot, msg, chat_id)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, DÊ REPLY NESTA MENSAGEM com a mensagem que será exibida quando alguém entrar no grupo":
                    if str(msg['from']['username']) in listaadmins:
                        AtualizaBemvindo(cookiebot, msg, chat_id)
                    else:
                        cookiebot.sendMessage(chat_id, "Você não é um admin do grupo!", reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith("/novobemvindo"):
                    NovoBemvindo(cookiebot, msg, chat_id)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, DÊ REPLY NESTA MENSAGEM com a mensagem que será exibida quando alguém pedir as regras":
                    if str(msg['from']['username']) in listaadmins:
                        AtualizaRegras(cookiebot, msg, chat_id)
                    else:
                        cookiebot.sendMessage(chat_id, "Você não é um admin do grupo!", reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith("/novasregras"):
                    NovasRegras(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/regras"):
                    Regras(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/tavivo"):
                    TaVivo(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/everyone"):
                    Everyone(cookiebot, msg, chat_id, listaadmins)
                elif msg['text'].startswith("/adm"):
                    Adm(cookiebot, msg, chat_id, listaadmins)
                elif msg['text'].startswith("/comandos"):
                    Comandos(cookiebot, msg, chat_id)
                elif (msg['text'].startswith("/hoje") or msg['text'].startswith("/today")) and funfunctions == True:
                    if FurBots == False:
                        Hoje(cookiebot, msg, chat_id)
                    else:
                        return
                elif (msg['text'].startswith("/cheiro") or msg['text'].startswith("/smell")) and funfunctions == True:
                    if FurBots == False:
                        Cheiro(cookiebot, msg, chat_id)
                    else:
                        return
                elif ('eu faço' in msg['text'] or 'eu faco' in msg['text']) and '?' in msg['text'] and funfunctions == True:
                    if FurBots == False:
                        QqEuFaço(cookiebot, msg, chat_id)
                    else:
                        return
                elif msg['text'].startswith("/ideiadesenho") and utilityfunctions == True:
                    IdeiaDesenho(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/contato"):
                    Contato(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/qualquercoisa") and utilityfunctions == True:
                    PromptQualquerCoisa(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/configurar"):
                    Configurar(cookiebot, msg, chat_id, listaadmins)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "DÊ REPLY NESTA MENSAGEM com o novo valor da variável" in msg['reply_to_message']['text']:
                    ConfigurarSettar(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/") and " " not in msg['text'] and os.path.exists("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')) and utilityfunctions == True:
                    CustomCommand(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/") and "//" not in msg['text'] and " " not in msg['text'] and (len(msg['text'].split('@')) < 2 or msg['text'].split('@')[1] in ['CookieMWbot', 'MekhysBombot']) and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and utilityfunctions == True:
                    QualquerCoisa(cookiebot, msg, chat_id, sfw)
                elif (msg['text'].startswith("Cookiebot") or msg['text'].startswith("cookiebot") or 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') and ("quem" in msg['text'] or "Quem" in msg['text']) and ("?" in msg['text']):
                    Quem(cookiebot, msg, chat_id)
                elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and msg['reply_to_message']['caption'] == "Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo te removerei do chat\n(OBS: Se não aparecem 4 digitos, abra a foto completa)".format(str(round(captchatimespan/60))):
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan)
                elif (('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') or "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']) and funfunctions == True:
                    if not OnSay(cookiebot, msg, chat_id):
                        InteligenciaArtificial(cookiebot, msg, chat_id)
                        if 'reply_to_message' in msg and 'text' in msg['reply_to_message']:
                            ChatterbotAbsorb(msg)
                else:
                    if 'reply_to_message' in msg and 'text' in msg['reply_to_message']:
                        ChatterbotAbsorb(msg)
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan)
                    CheckCaptcha(cookiebot, msg, chat_id, captchatimespan)
                    OnSay(cookiebot, msg, chat_id)
            if chat_type != 'private':
                CooldownUpdates(msg, chat_id, lastmessagetime)
            run_unnatendedthreads()
    except:
        if 'ConnectionResetError' not in traceback.format_exc():
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
            cookiebot.sendMessage(mekhyID, str(msg))

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
            except:
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
        if 'ConnectionResetError' not in traceback.format_exc():
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
            cookiebot.sendMessage(mekhyID, str(msg))

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    if 'CONFIG' in query_data:
        ConfigVariableButton(cookiebot, msg, query_data)
    elif 'PUBLISHER' in query_data:
        PublisherQuery(cookiebot, msg, query_data, mekhyID)
    elif 'PUBLISH' in query_data:
        PublishQuery(cookiebot, msg, query_data, mekhyID)
    else:
        listaadmins_id = []
        for admin in cookiebot.getChatAdministrators(msg['message']['reply_to_message']['chat']['id']):
            listaadmins_id.append(str(admin['user']['id']))
        if query_data == 'CAPTCHA' and str(from_id) in listaadmins_id:
            SolveCaptcha(cookiebot, msg, msg['message']['reply_to_message']['chat']['id'], True)
            DeleteMessage(telepot.message_identifier(msg['message']))
    run_unnatendedthreads()
        

MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()