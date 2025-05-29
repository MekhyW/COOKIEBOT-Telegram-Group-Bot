from threading import Thread, Lock, Timer
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import gc
import sys
import traceback
import telepot
from telepot.loop import MessageLoop
from telepot.exception import TooManyRequestsError, BotWasBlockedError, MigratedToSupergroupChatError, NotEnoughRightsError
from universal_funcs import *
from Audio import *
from Configurations import *
from Cooldowns import *
from GroupShield import *
from Miscellaneous import *
from NaturalLanguage import *
from Publisher import *
from SocialContent import *
from UserRegisters import *
from Birthdays import *
from Giveaways import *
from Server import *

if len(sys.argv) < 2:
    print("Usage: python COOKIEBOT.py [is_alternate_bot (int)]")
    sys.exit(1)
for file in os.listdir():
    if not (os.path.isdir(file) or file.endswith('.py') or file.endswith('.db') or file.endswith('.txt')):
        os.remove(file)
current_date_utc = None
current_date_mutex = Lock()
is_alternate_bot = int(sys.argv[1])
furbots_cmds = [x.strip() for x in open("Static/FurBots_functions.txt", "r+", encoding='utf-8').readlines()]
unnatended_threads = list()
IGNORED_MSG_TYPES = {
    'dice', 'poll', 'voice_chat_started', 'voice_chat_ended', 
    'video_chat_scheduled', 'video_chat_started', 'video_chat_ended',
    'voice_chat_participants_invited', 'video_chat_participants_invited',
    'forum_topic_created', 'forum_topic_edited', 'forum_topic_closed', 
    'forum_topic_reopened', 'story', 'poll_answer', 'boost_added',
    'chat_boost', 'removed_chat_boost', 'message_auto_delete_timer_changed'
}
MAX_THREADS = 50
THREAD_TIMEOUT = 15
executor = ThreadPoolExecutor(max_workers=MAX_THREADS)
cookiebot = telepot.Bot(get_bot_token(is_alternate_bot))
myself = cookiebot.getMe()
updates = cookiebot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    cookiebot.getUpdates(offset=last_update_id+1)
send_message(cookiebot, ownerID, 'I am online')
gc.enable()

def thread_function(msg):
    global current_date_utc
    try:
        if any(key in msg for key in IGNORED_MSG_TYPES):
            return
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id, msg['message_id'])
        if chat_type == 'channel':
            return
        if chat_type == 'private':
            if 'text' not in msg:
                send_message(cookiebot, chat_id, "This is a private chat, send a message in a group chat to use me!", msg)
                return
            if msg['text'].startswith("/start"):
                set_private_commands(cookiebot, chat_id, is_alternate_bot=is_alternate_bot)
            elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "REPLY THIS MESSAGE with the new variable value" in msg['reply_to_message']['text']:
                configurar_set(cookiebot, msg, chat_id, is_alternate_bot=is_alternate_bot)
            elif msg['text'].startswith(("/grupos", "/groups")) and 'from' in msg and msg['from']['id'] == ownerID:
                list_groups(cookiebot, chat_id)
            elif msg['text'].startswith(("/comandos", "/commands")):
                list_commands(cookiebot, msg, chat_id, 'eng')
            elif msg['text'].startswith(("/privacy", "/privacidade", "/privacidad")):
                privacy_statement(cookiebot, msg, chat_id, 'eng')
            elif msg['text'] == "/stop" and 'from' in msg and msg['from']['id'] == ownerID:
                kill_api_server()
                os._exit(0)
            elif msg['text'] == "/restart" and 'from' in msg and msg['from']['id'] == ownerID:
                kill_api_server()
                os.execl(sys.executable, sys.executable, *sys.argv)
            elif msg['text'].startswith("/leave") and 'from' in msg and msg['from']['id'] == ownerID:
                leave_and_blacklist(cookiebot, msg['text'].split()[1])
                send_message(cookiebot, ownerID, f"Auto-left\n{chat_id}")
            elif msg['text'].startswith("/blacklist") and 'from' in msg and msg['from']['id'] == ownerID:
                blacklist_user(msg['text'].split()[1])
                send_message(cookiebot, ownerID, f"Blacklisted user with ID {msg['text'].split()[1]}")
            elif msg['text'].startswith("/unblacklist") and 'from' in msg and msg['from']['id'] == ownerID:
                unblacklist_user(msg['text'].split()[1])
                send_message(cookiebot, ownerID, f"Unblacklisted user with ID {msg['text'].split()[1]}")
            elif msg['text'].startswith("/broadcast") and 'from' in msg and msg['from']['id'] == ownerID:
                broadcast_message(cookiebot, msg)
            elif msg['text'].startswith("/"):
                send_message(cookiebot, chat_id, "Commands must be used in a group chat!", msg)
            else:
                pv_default_message(cookiebot, msg, chat_id, is_alternate_bot)       
            run_unnatendedthreads()
            return
        thread_id = msg['message_thread_id'] if 'message_thread_id' in msg else None
        listaadmins, listaadmins_id, listaadmins_status = get_admins(cookiebot, chat_id, is_alternate_bot=is_alternate_bot)
        FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = get_config(cookiebot, chat_id, is_alternate_bot=is_alternate_bot)
        if 'group_chat_created' in msg and msg['group_chat_created']:
            isCreatorBlacklisted = get_request_backend(f"blacklist/{msg['from']['id']}")
            chatinfo = cookiebot.getChat(chat_id)
            if (not 'error' in isCreatorBlacklisted and 'id' in isCreatorBlacklisted and isCreatorBlacklisted['id'] == str(msg['from']['id'])) or len(chatinfo['title']) < 3 or '卐' in chatinfo['title']:
                leave_and_blacklist(cookiebot, chat_id)
                send_message(cookiebot, ownerID, f"Auto-left\n{chat_id}")
                return
        elif content_type == "new_chat_member":
            if msg['new_chat_participant']['id'] == myself['id']:
                isBlacklisted = get_request_backend(f"blacklist/{chat_id}")
                chatinfo = cookiebot.getChat(chat_id)
                if (not 'error' in isBlacklisted and 'id' in isBlacklisted and isBlacklisted['id'] == str(chat_id)) or len(chatinfo['title']) < 3 or myself['first_name'] in chatinfo['title']:
                    leave_and_blacklist(cookiebot, chat_id)
                    send_message(cookiebot, ownerID, f"Auto-left\n{chat_id}")
                    return
                send_message(cookiebot, ownerID, f"Added\n{chatinfo}")
                if not is_alternate_bot:
                    cookiebot.sendAnimation(chat_id, 'https://cdn.dribbble.com/users/4228736/screenshots/10874431/media/28ef00faa119065224429a0f94be21f3.gif',
                    caption="Obrigado por me adicionar!\nThanks for adding me!\n\n--> Use /comandos para ver todas as minhas funcionalidades\n--> /novobemvindo e /novasregras para alterar as mensagens de boas-vindas e regras\n--> Não esqueça de me dar direitos administrativos para poder defender o grupo de raiders/spammers ou apagar mensagens\n--> Website, painel de controle e novas features virão em breve. Estou em crescimento!\n\nIf this chat is not in portuguese language, you can use /configure to change my lang.\nIf you have any questions or want something added, message @MekhyW")
                if 'language_code' in msg['from']:
                    set_language(cookiebot, msg, chat_id, msg['from']['language_code'])
                    get_config(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
            elif msg['from']['id'] != msg['new_chat_participant']['id']:
                if msg['new_chat_participant']['is_bot']:
                    text = "Um novo companheiro bot foi adicionado!\n<blockquote> Caso algum comando entre em conflito, fale com o Mekhy </blockquote>" if language == 'pt' else "¡Un nuevo compañero bot ha sido agregado!\n<blockquote> Si algún comando entra en conflicto, hable con el Mekhy </blockquote>" if language == 'es' else "A new bot companion has been added!\n<blockquote> If any command conflicts, talk to Mekhy </blockquote>"
                    send_message(cookiebot, chat_id, text, msg)
                else:
                    welcome_message(cookiebot, msg, chat_id, limbotimespan, language, is_alternate_bot=is_alternate_bot)
            elif check_human(cookiebot, msg, chat_id, language) or check_cas(cookiebot, msg, chat_id, language) or check_banlist(cookiebot, msg, chat_id, language) or check_spamwatch(cookiebot, msg, chat_id, language):
                if (funfunctions or is_alternate_bot) and random.randint(1, 10) == 1:
                    with open('Static/silence_scammer.jpg', 'rb') as silence_scammer:
                        send_photo(cookiebot, chat_id, silence_scammer)
            elif captchatimespan > 0 and myself['username'] in listaadmins:
                captcha_message(cookiebot, msg, chat_id, captchatimespan, language)
            else:
                welcome_message(cookiebot, msg, chat_id, limbotimespan, language, is_alternate_bot=is_alternate_bot)
        elif content_type == "left_chat_member":
            left_chat_member(msg, chat_id)
            if not msg['left_chat_member']['is_bot'] and msg['left_chat_member']['id'] != msg['from']['id'] and myself['id'] not in [msg['from']['id'], msg['left_chat_member']['id']]:
                report_ask(cookiebot, msg, chat_id, msg['left_chat_member']['id'], language)
        elif content_type == "voice":
            if utilityfunctions or funfunctions:
                audio = get_media_content(cookiebot, msg, 'voice', is_alternate_bot=is_alternate_bot)
                if utilityfunctions:
                    identify_music(cookiebot, msg, chat_id, audio, language)
                if funfunctions and 'reply_to_message' in msg and msg['reply_to_message']['from']['id'] == myself['id']:
                    msg['text'] = speech_to_text(audio)
                    send_message(cookiebot, chat_id, conversational_ai(cookiebot, msg, chat_id, language, sfw), msg_to_reply=msg)
        elif content_type == "audio":
            pass
        elif content_type in ["photo", "video", "document", "animation"] and all(key in msg for key in ['sender_chat', 'forward_from_chat', 'from', 'caption']) and msg['from']['first_name'] == 'Telegram' and publisherask:
            ask_publisher(cookiebot, msg, chat_id, language)
        elif content_type == "photo":
            if sfw and funfunctions and not publisherpost:
                add_to_random_database(msg, chat_id, msg['photo'][-1]['file_id'])
        elif content_type == "video":
            if sfw and funfunctions and not publisherpost:
                add_to_random_database(msg, chat_id)
        elif content_type == "document":
            if funfunctions and 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                reply_sticker(cookiebot, msg, chat_id)
        elif content_type == "animation":
            if funfunctions and 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                reply_sticker(cookiebot, msg, chat_id)
        elif content_type == "sticker":
            sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language)
            if sfw and 'username' in msg['from']:
                add_to_sticker_database(msg)
            if funfunctions and 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                reply_sticker(cookiebot, msg, chat_id)
        elif 'text' in msg:
            if msg['text'].startswith("/") and len(msg['text']) > 1:
                if FurBots and msg['text'].split()[0].split('@')[0] in furbots_cmds:
                    return
                if msg['text'].startswith("/start@CookieMWbot") or msg['text'].startswith("/start@MekhysBombot"):
                    cookiebot.sendAnimation(chat_id, 'https://cdn.dribbble.com/users/4228736/screenshots/10874431/media/28ef00faa119065224429a0f94be21f3.gif',
                    caption="Obrigado por me adicionar!\nThanks for adding me!\n\n--> Use /comandos para ver todas as minhas funcionalidades\n--> /configurar para ligar/desligar funções ou alterar valores\n--> Não esqueça de me dar direitos administrativos para poder defender o grupo de raiders/spammers ou apagar mensagens\n--> Website, painel de controle e tutoriais virão em breve. Estou em crescimento!\n\nIf this chat is not in portuguese language, you can use /configure to change my lang.\nIf you have any questions or want something added, message @MekhyW",
                    reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith("/leave") and 'from' in msg and msg['from']['id'] == ownerID:
                    leave_and_blacklist(cookiebot, chat_id)
                elif msg['text'].startswith(("/privacy", "/privacidade", "/privacidad")):
                    privacy_statement(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/reload", "/recarregar")):
                    get_admins(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
                    get_config(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
                    text = "Memória recarregada com sucesso!" if language == 'pt' else "¡Memoria recargada con éxito!" if language == 'es' else "Memory reloaded successfully!"
                    send_message(cookiebot, chat_id, text, msg)
                elif msg['text'].startswith(("/analise", "/analisis", "/analysis")):
                    analyze(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/divulgar", "/publish", "/publicar")):
                    ask_publisher_command(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/repost", "/repostar", "/reenviar")):
                    listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
                    schedule_autopost(cookiebot, msg, chat_id, language, listaadmins_id, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/deleteposts", "/apagarposts", "/apagarposts")):
                    listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
                    cancel_posts(cookiebot, msg, chat_id, language, listaadmins_id, is_alternate_bot=is_alternate_bot)
                elif utilityfunctions and msg['text'].startswith(("/buscarfonte", "/searchsource", "/buscarfuente")):
                    reverse_search(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/aleatorio", "/aleatório", "/random", "/meme", "/idade", "/age", "/edad", "/genero", "/gênero", "/gender", 
                                                "/rojao", "/rojão", "/acende", "/fogos", "/firecracker", "/shippar", "/ship", "/milton", "/reclamacao", "/reclamação", "/complaint", "/queja",
                                                "/batalha", "/battle", "/batalla", "/desenterrar", "/unearth", "/morte", "/death", "/muerte", "/sorte", "/fortunecookie", "/suerte",
                                                "/zoar", "/destroy", "/destruir", "/aniversário", "/aniversario", "/birthday", "/cumpleanos", "/cumpleaños", "/proximosaniversarios", "/nextbirthdays", "/proximoscumpleanos")):
                    if not funfunctions:
                        notify_fun_off(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/aleatorio", "/aleatório", "/random")):
                        random_media(cookiebot, msg, chat_id, thread_id=thread_id, is_alternate_bot=is_alternate_bot)
                    elif msg['text'].startswith("/meme"):
                        meme(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/batalha", "/battle", "/batalla")):
                        battle(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                    elif msg['text'].startswith(("/idade", "/age", "/edad")):
                        age(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/genero", "/gênero", "/gender")):
                        gender(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/rojao", "/rojão", "/acende", "/fogos", "/firecracker")):
                        firecracker(cookiebot, msg, chat_id, thread_id=thread_id, is_alternate_bot=is_alternate_bot)
                    elif msg['text'].startswith(("/shippar", "/ship")):
                        shipp(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                    elif msg['text'].startswith(("/milton", "/reclamacao", "/reclamação", "/complaint", "/queja")):
                        complaint(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/desenterrar", "/unearth")):
                        unearth(cookiebot, msg, chat_id, thread_id=thread_id)
                    elif msg['text'].startswith(("/morte", "/muerte", "/death")):
                        death(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/sorte", "/fortunecookie", "/suerte")):
                        fortune_cookie(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/zoar", "/destroy", "/destruir")):
                        destroy(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                    elif msg['text'].startswith(("/aniversário", "/aniversario", "/birthday", "/cumpleaños", "/cumpleanos")):
                        birthday(cookiebot, current_date_utc, msg=msg, manual_chat_id=chat_id, language=language)
                    elif msg['text'].startswith(("/proximosaniversarios", "/nextbirthdays", "/proximoscumpleanos")):
                        next_birthdays(cookiebot, msg, chat_id, language, current_date_utc)
                elif msg['text'].startswith(("/dado", "/dice", "/patas", "/bff", "/furcamp", "/fursmeet", "/trex", "/ideiadesenho", "/drawingidea", "/ideadibujo", 
                                             "/qualquercoisa", "/anything", "/cualquiercosa", "/youtube", "/giveaway")) or (msg['text'].startswith("/d") and msg['text'].split()[0].split('/d')[1].isdigit()):
                    if msg['text'].startswith(("/patas", "/bff", "/furcamp", "/fursmeet", "/trex")):
                        event_countdown(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                    elif not utilityfunctions:
                        notify_utility_off(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/dado", "/dice", "/d")):
                        roll_dice(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/ideiadesenho", "/drawingidea", "/ideadibujo")):
                        drawing_idea(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/qualquercoisa", "/anything", "/cualquiercosa")):
                        prompt_qualquer_coisa(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/youtube")):
                        youtube_search(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith("/giveaway"):
                        giveaways_ask(cookiebot, msg, chat_id, language, listaadmins_id, listaadmins_status)
                elif msg['text'].startswith(("/novobemvindo", "/newwelcome", "/nuevabienvenida")):
                    new_welcome_message(cookiebot, msg, chat_id)
                elif msg['text'].startswith(("/novasregras", "/newrules", "/nuevasreglas")):
                    new_rules_message(cookiebot, msg, chat_id)
                elif msg['text'].startswith(("/regras", "/rules", "/reglas")):
                    rules_message(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/tavivo", "/isalive", "/estavivo")):
                    is_alive(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/everyone", "@everyone")):
                    everyone(cookiebot, msg, chat_id, listaadmins, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/adm", "@admin")):
                    call_admins_ask(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/comandos", "/commands")):
                    list_commands(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/configurar", "/configure")):
                    listaadmins, listaadmins_id, listaadmins_status = get_admins(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
                    configurar(cookiebot, msg, chat_id, listaadmins_id, listaadmins_status, language)
                elif funfunctions and msg['text'].replace('/', '').replace("@CookieMWbot", '').replace("@pawstralbot", '').split()[0] in custom_commands:
                    custom_command(cookiebot, msg, chat_id, language)
                elif utilityfunctions and "//" not in msg['text'] and (len(msg['text'].split('@')) < 2 or msg['text'].split('@')[1] in ['CookieMWbot', 'MekhysBombot', 'pawstralbot', 'SCTarinBot', 'MekhysConnectBot']):
                    decrease_remaining_image_searches(msg['from']['id'])
                    if remaining_image_searches[msg['from']['id']]['remaining'] >= 0 and remaining_image_searches['total_remaining']['remaining'] >= 0:
                        qualquer_coisa(cookiebot, msg, chat_id, sfw, language)
                    else:
                        text = "Limite de buscas de imagens atingido" if language == 'pt' else "Límite de búsquedas de imágenes alcanzado" if language == 'es' else "Image search limit reached"
                        send_message(cookiebot, chat_id, text, msg)
            elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone joins the group.\n\nYou can include <user> to be replaced with the user name":
                listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
                update_welcome_message(cookiebot, msg, chat_id, listaadmins_id, is_alternate_bot=is_alternate_bot)
            elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone asks for the rules":
                listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
                update_rules_message(cookiebot, msg, chat_id, listaadmins_id, is_alternate_bot=is_alternate_bot)
            elif funfunctions and (msg['text'].lower().startswith("cookiebot") or ('reply_to_message' in msg and 'from' in msg and msg['reply_to_message']['from']['id'] == myself['id'])) and any(x in msg['text'].lower() for x in ['quem', 'who', 'quién', 'quien']) and ("?" in msg['text']) and not any(x in msg['text'].lower() for x in ['você', 'voce', 'vc', 'you', 'usted', 'tú']):
                who(cookiebot, msg, chat_id, language)
            elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and any(x in msg['reply_to_message']['caption'] for x in [f"{round(captchatimespan/60)} minutes", f"{round(captchatimespan/60)} minutos"]):
                solve_captcha(cookiebot, msg, chat_id, False, limbotimespan, language, is_alternate_bot=is_alternate_bot)
            elif funfunctions and 'reply_to_message' in msg and 'caption' in msg['reply_to_message'] and any(x in msg['reply_to_message']['caption'] for x in ['Milton do RH.', 'Milton from HR.']):
                complaint_answer(cookiebot, msg, chat_id, language)
            elif 'reply_to_message' in msg and msg['reply_to_message']['from']['id'] == myself['id'] and 'reply_markup' in msg['reply_to_message']:
                check_notify_post_reply(cookiebot, msg, chat_id, language)
            elif funfunctions and (('reply_to_message' in msg and msg['reply_to_message']['from']['id'] == myself['id'] and 'text' in msg['reply_to_message']) or "cookiebot" in msg['text'].lower() or "@CookieMWbot" in msg['text']):
                if 'from' in msg:
                    decrease_remaining_responses_ai(msg['from']['id'])
                if 'from' not in msg or remaining_responses_ai[msg['from']['id']] > 0:
                    send_message(cookiebot, chat_id, conversational_ai(cookiebot, msg, chat_id, language, sfw), msg_to_reply=msg)
            else:
                if 'from' in msg:
                    if utilityfunctions:
                        check_reply_embed(cookiebot, msg, chat_id, is_alternate_bot)
                    increase_remaining_responses_ai(msg['from']['id'])
                if captchatimespan > 0 and myself['username'] in listaadmins:
                    solve_captcha(cookiebot, msg, chat_id, False, limbotimespan, language, is_alternate_bot=is_alternate_bot)
                    check_captcha(cookiebot, msg, chat_id, captchatimespan, language)
        if chat_type != 'private' and content_type != "sticker":
            sticker_cooldown_updates(chat_id)
        run_unnatendedthreads()
    except TooManyRequestsError:
        print("Too many requests")
    except BotWasBlockedError:
        print("Bot was blocked")
    except MigratedToSupergroupChatError:
        print("Migrated to supergroup chat")
    except NotEnoughRightsError:
        print("Not enough rights")
    except requests.exceptions.ReadTimeout:
        print("Read timeout")
    except Exception:
        errormsg = traceback.format_exc()
        if 'ConnectionResetError' in errormsg or 'RemoteDisconnected' in errormsg:
            handle(msg)
            return
        send_error_traceback(cookiebot, msg, errormsg)
    finally:
        check_new_name(cookiebot, msg, chat_id, chat_type)
        if is_alternate_bot or current_date_mutex.locked():
            return
        msg_date_utc = datetime.datetime.now(datetime.timezone.utc).timestamp()
        msg_date = datetime.datetime.fromtimestamp(msg_date_utc, tz=datetime.timezone.utc).strftime('%Y-%m-%d')
        with current_date_mutex:
            current_stored_date = datetime.datetime.fromtimestamp(current_date_utc, tz=datetime.timezone.utc).strftime('%Y-%m-%d') if current_date_utc else None
            if current_stored_date != msg_date:
                current_date_utc = msg_date_utc
                birthday(cookiebot, current_date_utc, msg=msg)

def thread_function_query(msg):
    try:
        if any(key in msg for key in IGNORED_MSG_TYPES):
            return
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)
        try:
            chat_id = msg['message']['reply_to_message']['chat']['id']
            listaadmins, listaadmins_id, listaadmins_status = get_admins(cookiebot, chat_id, is_alternate_bot=is_alternate_bot)
        except Exception:
            chat_id = msg['chat']['id'] if 'chat' in msg else from_id
            listaadmins, listaadmins_id, listaadmins_status = [], [], []
        if 'CONFIG' in query_data:
            config_variable_button(cookiebot, msg, query_data)
        elif 'Pub' in query_data:
            if 'creator' in listaadmins_status and str(from_id) not in listaadmins_id and str(from_id) != str(ownerID):
                cookiebot.answerCallbackQuery(query_id, text="Only admins can do this")
                return
            try:
                delete_message(cookiebot, telepot.message_identifier(msg['message']))
            except Exception:
                pass
            if query_data.startswith('SendToApproval'):
                ask_approval(cookiebot, query_data, from_id, is_alternate_bot=is_alternate_bot)
            elif query_data.startswith('y'):
                schedule_post(cookiebot, query_data)
            elif query_data.startswith('n'):
                deny_post(query_data)
            else:
                cookiebot.answerCallbackQuery(query_id, text="ERROR! please contact @MekhyW")
        elif query_data.startswith('Report'):
            command = query_data.split()[1]
            targetid = query_data.split()[2]
            language = query_data.split()[3]
            if command == 'Yes':
                report(cookiebot, chat_id, targetid, language)
            elif command == 'Blacklist':
                origin_chat_id = query_data.split()[4]
                post_request_backend(f'blacklist/{targetid}')
                send_message(cookiebot, ownerID, f"Blacklisted {targetid}")
                text = f"Conta com ID {targetid} marcada como spam\n<blockquote> Obrigado pela denúncia! </blockquote>" if language == 'pt' else f"Cuenta con ID {targetid} marcada como spam\n<blockquote> ¡Gracias por la denuncia! </blockquote>" if language == 'es' else f"Account with ID {targetid} marked as spam\n<blockquote> Thank you for the report! </blockquote>"
                send_message(cookiebot, origin_chat_id, text)
            delete_message(cookiebot, telepot.message_identifier(msg['message']))
        elif (query_data.startswith('CAPTCHAAPPROVE') and (str(from_id) in listaadmins_id or str(from_id) == str(ownerID))) or (query_data.startswith('CAPTCHASELF') and str(from_id) == query_data.split()[2]):
            solve_captcha(cookiebot, msg, chat_id, True, is_alternate_bot=is_alternate_bot, language=query_data.split()[1])
        elif query_data.startswith('ADM'):
            yesno = query_data.split()[1]
            language = query_data.split()[2]
            message_id = query_data.split()[3]
            delete_message(cookiebot, telepot.message_identifier(msg['message']))
            if yesno == 'Yes':
                call_admins(cookiebot, msg, chat_id, listaadmins, language, message_id)
            else:
                text = "Comando cancelado" if language == 'pt' else "Comando cancelado" if language == 'es' else "Command canceled"
                send_message(cookiebot, chat_id, text)
        elif query_data.startswith('RULES'):
            rules_message(cookiebot, msg['message'], msg['message']['chat']['id'], query_data.split()[1])
            cookiebot.editMessageReplyMarkup((msg['message']['chat']['id'], msg['message']['message_id']), reply_markup=None)
        elif query_data.startswith('GIVEAWAY'):
            if 'creator' in listaadmins_status and str(from_id) not in listaadmins_id and str(from_id) != str(ownerID):
                cookiebot.answerCallbackQuery(query_id, text="Only admins can do this")
                return
            if query_data.split()[1].isnumeric():
                delete_message(cookiebot, telepot.message_identifier(msg['message']))
                giveaways_create(cookiebot, msg, int(query_data.split()[1]), msg['message']['chat']['id'], " ".join(query_data.replace('"', '').split()[2:]))
            elif query_data.split()[1] == 'enter':
                giveaways_enter(cookiebot, msg, msg['message']['chat']['id'])
            elif query_data.split()[1] == 'end':
                giveaways_end(cookiebot, msg, msg['message']['chat']['id'], listaadmins_id)
            elif query_data.split()[1] == 'delete':
                giveaways_delete(cookiebot, msg, msg['message']['chat']['id'])
            else:
                cookiebot.answerCallbackQuery(query_id, text="ERROR! please contact @MekhyW")
        else:
            cookiebot.answerCallbackQuery(query_id, text="ERROR! please contact @MekhyW")
        run_unnatendedthreads()
    except Exception:
        errormsg = f"{traceback.format_exc()}"
        if 'ConnectionResetError' in errormsg or 'RemoteDisconnected' in errormsg:
            handle_query(msg)
        else:
            send_error_traceback(cookiebot, msg, errormsg)

def thread_with_timeout(msg, isquery):
    future = executor.submit(thread_function if not isquery else thread_function_query, msg)
    try:
        future.result(timeout = THREAD_TIMEOUT if not isquery else None)
    except TimeoutError:
        print("Timeout")
    except Exception as e:
        print(f"Error in thread: {str(e)}")
        traceback.print_exc()

def run_unnatendedthreads():
    num_running_threads = len([t for t in threading.enumerate() if t.is_alive() and not t.daemon])
    for unnatended_thread in list(unnatended_threads):
        if unnatended_thread.is_alive() and unnatended_thread in unnatended_threads:
            unnatended_threads.remove(unnatended_thread)
        elif num_running_threads < MAX_THREADS:
            if unnatended_thread.is_alive():
                continue
            unnatended_thread.daemon = True
            unnatended_thread.start()
            num_running_threads += 1
            if unnatended_thread in unnatended_threads:
                unnatended_threads.remove(unnatended_thread)
    if len(unnatended_threads):
        print(f"{len(unnatended_threads)} threads are still unnatended")

def handle(msg):
    try:
        new_thread = Thread(target=thread_with_timeout, args=(msg,False,))
        unnatended_threads.append(new_thread)
        run_unnatendedthreads()
    except Exception:
        send_error_traceback(cookiebot, msg, traceback.format_exc())

def handle_query(msg):
    try:
        new_thread = Thread(target=thread_with_timeout, args=(msg,True,))
        unnatended_threads.append(new_thread)
        run_unnatendedthreads()
    except Exception:
        send_error_traceback(cookiebot, msg, traceback.format_exc())

def scheduler_check():
    print("SCHEDULER CHECK")
    try:
        scheduler_pull(cookiebot, is_alternate_bot=is_alternate_bot)
    except Exception:
        send_error_traceback(cookiebot, None, traceback.format_exc())
    finally:
        timer_scheduler_check = Timer(300, scheduler_check)
        timer_scheduler_check.start()

if __name__ == '__main__':
    if is_alternate_bot:
        MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()
    else:
        scheduler_check()
        MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_as_thread()
        run_api_server()
