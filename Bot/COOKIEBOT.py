import threading
import gc
import os
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

if len(sys.argv) < 2:
    print("Usage: python COOKIEBOT.py [is_alternate_bot (int)]")
    sys.exit(1)
is_alternate_bot = int(sys.argv[1])
cookiebot = telepot.Bot(get_bot_token(is_alternate_bot))
myself = cookiebot.getMe()
updates = cookiebot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    cookiebot.getUpdates(offset=last_update_id+1)
unnatended_threads = list()
num_max_threads = 50
gc.enable()

send_message(cookiebot, mekhyID, 'I am online')

def thread_function(msg):
    try:
        if any(key in msg for key in ['dice', 'poll', 'voice_chat_started', 'voice_chat_ended', 'video_chat_scheduled', 'video_chat_started', 'video_chat_ended', 
                                      'voice_chat_participants_invited', 'video_chat_participants_invited',
                                      'forum_topic_created', 'forum_topic_edited','forum_topic_closed', 'forum_topic_reopened', 'story', 'poll_answer',
                                      'boost_added', 'chat_boost', 'removed_chat_boost', 'message_auto_delete_timer_changed']):
            return
        thread_id = msg['message_thread_id'] if 'message_thread_id' in msg else None
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id, msg['message_id'])
        FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = 0, 1, 5, 600, 300, 1, 1, "pt", 0, 1, "9999", 9999, 0
        if chat_type == 'private' and 'reply_to_message' not in msg:
            if 'text' in msg:
                if msg['text'].startswith("/start"):
                    set_private_commands(cookiebot, chat_id, is_alternate_bot=is_alternate_bot)
                if msg['text'].startswith(("/grupos", "/groups")) and 'from' in msg and msg['from']['id'] == mekhyID:
                    list_groups(cookiebot, chat_id)
                elif msg['text'].startswith(("/comandos", "/commands")):
                    list_commands(cookiebot, msg, chat_id, 'eng')
                elif msg['text'].startswith(("/privacy", "/privacidade", "/privacidad")):
                    privacy_statement(cookiebot, msg, chat_id, 'eng')
                elif msg['text'] == "/stop" and 'from' in msg and msg['from']['id'] == mekhyID:
                    os._exit(0)
                elif msg['text'] == "/restart" and 'from' in msg and msg['from']['id'] == mekhyID:
                    os.execl(sys.executable, sys.executable, *sys.argv)
                elif msg['text'].startswith("/leave") and 'from' in msg and msg['from']['id'] == mekhyID:
                    leave_and_blacklist(cookiebot, msg['text'].split()[1])
                elif msg['text'].startswith("/broadcast") and 'from' in msg and msg['from']['id'] == mekhyID:
                    broadcast_message(cookiebot, msg)
            pv_default_message(cookiebot, msg, chat_id, is_alternate_bot)
            run_unnatendedthreads()
            return
        if chat_type != 'private':
            listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id)
            FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = get_config(cookiebot, chat_id, is_alternate_bot=is_alternate_bot)
            check_new_name(msg, chat_id)
        if 'group_chat_created' in msg and msg['group_chat_created']:
            isCreatorBlacklisted = get_request_backend(f"blacklist/{msg['from']['id']}")
            chatinfo = cookiebot.getChat(chat_id)
            if (not 'error' in isCreatorBlacklisted) or len(chatinfo['title']) < 3:
                leave_and_blacklist(cookiebot, chat_id)
                send_message(cookiebot, mekhyID, f"Auto-left\n{chat_id}")
                return
        elif content_type == "new_chat_member":
            if msg['new_chat_participant']['id'] == myself['id']:
                isBlacklisted = get_request_backend(f"blacklist/{chat_id}")
                chatinfo = cookiebot.getChat(chat_id)
                if (not 'error' in isBlacklisted) or len(chatinfo['title']) < 3:
                    leave_and_blacklist(cookiebot, chat_id)
                    send_message(cookiebot, mekhyID, f"Auto-left\n{chat_id}")
                    return
                send_message(cookiebot, mekhyID, f"Added\n{chatinfo}")
                cookiebot.sendAnimation(chat_id, 'https://cdn.dribbble.com/users/4228736/screenshots/10874431/media/28ef00faa119065224429a0f94be21f3.gif',
                caption="Obrigado por me adicionar!\nThanks for adding me!\n\n--> Use /comandos para ver todas as minhas funcionalidades\n--> /configurar para ligar/desligar funções ou alterar valores\n--> Não esqueça de me dar direitos administrativos para poder defender o grupo de raiders/spammers ou apagar mensagens\n--> Website, painel de controle e tutoriais virão em breve. Estou em crescimento!\n\nIf this chat is not in portuguese language, you can use /configure to change my lang.\nIf you have any questions or want something added, message @MekhyW")
                if 'language_code' in msg['from']:
                    set_language(cookiebot, msg, chat_id, msg['from']['language_code'])
                    get_config(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
            elif msg['from']['id'] != msg['new_chat_participant']['id']:
                if msg['new_chat_participant']['is_bot']:
                    send_message(cookiebot, chat_id, "Um novo companheiro bot foi adicionado!\n<blockquote>Caso algum comando entre em conflito, fale com o Mekhy</blockquote>", msg, language)
                else:
                    welcome_message(cookiebot, msg, chat_id, limbotimespan, language, is_alternate_bot=is_alternate_bot)
            elif not check_human(cookiebot, msg, chat_id, language) and not check_cas(cookiebot, msg, chat_id, language) and not check_banlist(cookiebot, msg, chat_id, language) and not check_spamwatch(cookiebot, msg, chat_id, language):
                if captchatimespan > 0 and myself['username'] in listaadmins:
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
            if sfw and funfunctions:
                photo_id = msg['photo'][-1]['file_id']
                add_to_random_database(msg, chat_id, photo_id)
        elif content_type == "video":
            if sfw and funfunctions:
                add_to_random_database(msg, chat_id)
        elif content_type == "document":
            if funfunctions and 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                reply_sticker(cookiebot, msg, chat_id)
        elif content_type == "animation":
            if funfunctions and 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                reply_sticker(cookiebot, msg, chat_id)
        elif content_type == "sticker":
            sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language)
            if sfw:
                add_to_sticker_database(msg, chat_id)
            if funfunctions and 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                reply_sticker(cookiebot, msg, chat_id)
        elif 'text' in msg:
            if msg['text'].startswith("/") and len(msg['text']) > 1:
                if msg['text'].startswith("/start@CookieMWbot") or msg['text'].startswith("/start@MekhysBombot"):
                    cookiebot.sendAnimation(chat_id, 'https://cdn.dribbble.com/users/4228736/screenshots/10874431/media/28ef00faa119065224429a0f94be21f3.gif',
                    caption="Obrigado por me adicionar!\nThanks for adding me!\n\n--> Use /comandos para ver todas as minhas funcionalidades\n--> /configurar para ligar/desligar funções ou alterar valores\n--> Não esqueça de me dar direitos administrativos para poder defender o grupo de raiders/spammers ou apagar mensagens\n--> Website, painel de controle e tutoriais virão em breve. Estou em crescimento!\n\nIf this chat is not in portuguese language, you can use /configure to change my lang.\nIf you have any questions or want something added, message @MekhyW",
                    reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith("/leave") and 'from' in msg and msg['from']['id'] == mekhyID:
                    leave_and_blacklist(cookiebot, chat_id)
                elif msg['text'].startswith(("/privacy", "/privacidade", "/privacidad")):
                    privacy_statement(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/reload", "/recarregar")):
                    get_admins(cookiebot, chat_id, ignorecache=True)
                    get_config(cookiebot, chat_id, ignorecache=True, is_alternate_bot=is_alternate_bot)
                    send_message(cookiebot, chat_id, "Memória recarregada com sucesso!", msg, language)
                elif msg['text'].startswith(("/analise", "/analisis", "/analysis")):
                    analyze(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/repost", "/repostar", "/reenviar")):
                    listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True)
                    schedule_autopost(cookiebot, msg, chat_id, language, listaadmins_id, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/deletereposts", "/apagarreposts", "/apagarreenvios")):
                    listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True)
                    clear_autoposts(cookiebot, msg, chat_id, language, listaadmins_id, is_alternate_bot=is_alternate_bot)
                elif utilityfunctions and msg['text'].startswith(("/buscarfonte", "/searchsource", "/buscarfuente")):
                    reverse_search(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/aleatorio", "/aleatório", "/random", "/meme", "/idade", "/age", "/edad", "/genero", "/gênero", "/gender", 
                                                "/rojao", "/rojão", "/acende", "/fogos", "/shippar", "/ship", "/milton", "/reclamacao", "/reclamação", "/complaint", "/queja",
                                                "/batalha", "/battle", "/batalla", "/desenterrar", "/unearth", "/morte", "/death", "/muerte", "/sorte", "/fortunecookie", "/suerte",
                                                "/zoar", "/destroy", "/destruir")):
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
                    elif msg['text'].startswith(("/desenterrar", "unearth")):
                        unearth(cookiebot, msg, chat_id, thread_id=thread_id)
                    elif msg['text'].startswith(("/morte", "/muerte", "/death")):
                        death(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/sorte", "/fortunecookie", "/suerte")):
                        fortune_cookie(cookiebot, msg, chat_id, language)
                    elif msg['text'].startswith(("/zoar", "/destroy", "/destruir")):
                        destroy(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                elif utilityfunctions and (msg['text'].startswith(("/dado", "/dice")) or (msg['text'].lower().startswith("/d") and msg['text'].replace("@CookieMWbot", '').split()[0][2:].isnumeric())):
                    roll_dice(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/patas", "/bff", "/fursmeet", "/trex")):
                    event_countdown(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith(("/novobemvindo", "/newwelcome", "/nuevabienvenida")):
                    new_welcome_message(cookiebot, msg, chat_id)
                elif msg['text'].startswith(("/novasregras", "/newrules", "/nuevasreglas")):
                    new_rules_message(cookiebot, msg, chat_id)
                elif msg['text'].startswith(("/regras", "/rules", "/reglas")):
                    rules_message(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/tavivo", "/isalive", "/estavivo")):
                    is_alive(cookiebot, msg, chat_id, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith("/everyone"):
                    everyone(cookiebot, msg, chat_id, listaadmins, language, is_alternate_bot=is_alternate_bot)
                elif msg['text'].startswith("/adm"):
                    call_admins_ask(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/comandos", "/commands")):
                    list_commands(cookiebot, msg, chat_id, language)
                elif utilityfunctions and msg['text'].startswith(("/ideiadesenho", "/drawingidea", "/ideadibujo")):
                    drawing_idea(cookiebot, msg, chat_id, language)
                elif utilityfunctions and msg['text'].startswith(("/qualquercoisa", "/anything", "/cualquiercosa")):
                    prompt_qualquer_coisa(cookiebot, msg, chat_id, language)
                elif utilityfunctions and msg['text'].startswith("/youtube"):
                    youtube_search(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/configurar", "/configure")):
                    listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True)
                    configurar(cookiebot, msg, chat_id, listaadmins_id, language)
                elif utilityfunctions and " " not in msg['text'] and msg['text'].replace('/', '').replace("@CookieMWbot", '') in custom_commands:
                    custom_command(cookiebot, msg, chat_id)
                elif utilityfunctions and "//" not in msg['text'] and (len(msg['text'].split('@')) < 2 or msg['text'].split('@')[1] in ['CookieMWbot', 'MekhysBombot']):
                    if FurBots:
                        furbots_cmds = open("Static/FurBots_functions.txt", "r+", encoding='utf-8').readlines()
                        furbots_cmds = [x.strip() for x in furbots_cmds]
                        if msg['text'].split()[0].split('@')[0] in furbots_cmds:
                            return
                    QualquerCoisa(cookiebot, msg, chat_id, sfw, language)
            elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone joins the group.\n\nYou can include <user> to be replaced with the user name":
                listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True)
                update_welcome_message(cookiebot, msg, chat_id, listaadmins_id, is_alternate_bot=is_alternate_bot)
            elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone asks for the rules":
                listaadmins, listaadmins_id, _ = get_admins(cookiebot, chat_id, ignorecache=True)
                update_rules_message(cookiebot, msg, chat_id, listaadmins_id, is_alternate_bot=is_alternate_bot)
            elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "REPLY THIS MESSAGE with the new variable value" in msg['reply_to_message']['text']:
                configurar_set(cookiebot, msg, chat_id, is_alternate_bot=is_alternate_bot)
            elif funfunctions and (msg['text'].lower().startswith("cookiebot") or ('reply_to_message' in msg and msg['reply_to_message']['from']['id'] == myself['id'])) and any(x in msg['text'].lower() for x in ['quem', 'who', 'quién', 'quien']) and ("?" in msg['text']):
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
                    increase_remaining_responses_ai(msg['from']['id'])
                if captchatimespan > 0 and myself['username'] in listaadmins:
                    solve_captcha(cookiebot, msg, chat_id, False, limbotimespan, language, is_alternate_bot=is_alternate_bot)
                    check_captcha(cookiebot, msg, chat_id, captchatimespan, language)
        if chat_type != 'private' and content_type != "sticker":
            sticker_cooldown_updates(chat_id)
        run_unnatendedthreads()
    except (TooManyRequestsError, BotWasBlockedError, MigratedToSupergroupChatError, NotEnoughRightsError):
        print("Telegram Error")
    except Exception as e:
        errormsg = f"{traceback.format_exc()} {e}"
        if 'ConnectionResetError' in errormsg or 'RemoteDisconnected' in errormsg:
            handle(msg)
        else:
            send_message(cookiebot, mekhyID, traceback.format_exc())
            send_message(cookiebot, mekhyID, str(msg))
            send_message(cookiebot, mekhyID, str(e))

def thread_function_query(msg):
    try:
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)
        try:
            chat_id = msg['message']['reply_to_message']['chat']['id']
            listaadmins, listaadmins_id, listaadmins_status = get_admins(cookiebot, chat_id)
        except Exception:
            try:
                chat_id = msg['chat']['id']
            except Exception:
                chat_id = from_id
            listaadmins, listaadmins_id, listaadmins_status = [], [], []
        if 'CONFIG' in query_data:
            config_variable_button(cookiebot, msg, query_data)
        elif 'Pub' in query_data:
            if 'creator' in listaadmins_status and str(from_id) not in listaadmins_id:
                cookiebot.answerCallbackQuery(query_id, text="Only admins can do this")
            else:
                try:
                    delete_message(cookiebot, telepot.message_identifier(msg['message']))
                except Exception:
                    pass
                if query_data.startswith('SendToApproval'):
                    ask_approval(cookiebot, query_data, from_id, is_alternate_bot=is_alternate_bot)
                elif query_data.startswith('Approve'):
                    schedule_post(cookiebot, query_data)
                elif query_data.startswith('Deny'):
                    deny_post(query_data)
        elif query_data.startswith('Report'):
            command = query_data.split()[1]
            targetid = query_data.split()[2]
            language = query_data.split()[3]
            if command == 'Yes':
                report(cookiebot, chat_id, targetid, language)
            elif command == 'Blacklist':
                origin_chat_id = query_data.split()[4]
                post_request_backend(f'blacklist/{targetid}')
                send_message(cookiebot, mekhyID, f"Blacklisted {targetid}")
                send_message(cookiebot, origin_chat_id, f"Conta com ID {targetid} marcada como spam\n>Obrigado pela denúncia\!", language=language)
            delete_message(cookiebot, telepot.message_identifier(msg['message']))
        elif (query_data.startswith('CAPTCHAAPPROVE') and (str(from_id) in listaadmins_id or str(from_id) == str(mekhyID))) or (query_data.startswith('CAPTCHASELF') and str(from_id) == query_data.split()[2]):
            solve_captcha(cookiebot, msg, chat_id, True, is_alternate_bot=is_alternate_bot, language=query_data.split()[1])
        elif query_data.startswith('ADM'):
            yesno = query_data.split()[1]
            language = query_data.split()[2]
            if yesno == 'Yes':
                call_admins(cookiebot, msg, chat_id, listaadmins, language)
            else:
                send_message(cookiebot, chat_id, "Comando cancelado", language=language)
            delete_message(cookiebot, telepot.message_identifier(msg['message']))
        elif query_data.startswith('RULES'):
            rules_message(cookiebot, msg['message'], msg['message']['chat']['id'], query_data.split()[1])
            cookiebot.editMessageReplyMarkup((msg['message']['chat']['id'], msg['message']['message_id']), reply_markup=None)
        run_unnatendedthreads()
    except Exception as e:
        errormsg = f"{traceback.format_exc()} {e}"
        if 'ConnectionResetError' in errormsg or 'RemoteDisconnected' in errormsg:
            handle_query(msg)
        else:
            send_message(cookiebot, mekhyID, traceback.format_exc())
            send_message(cookiebot, mekhyID, str(msg))
            send_message(cookiebot, mekhyID, str(e))

def run_unnatendedthreads():
    num_running_threads = threading.active_count()
    for unnatended_thread in list(unnatended_threads):
        if unnatended_thread.is_alive():
            unnatended_threads.remove(unnatended_thread)
        elif num_running_threads < num_max_threads:
            unnatended_thread.start()
            num_running_threads += 1
            try:
                unnatended_threads.remove(unnatended_thread)
            except ValueError:
                pass
    if len(unnatended_threads) > 20 * num_max_threads:
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif len(unnatended_threads) > 0:
        print(f"{len(unnatended_threads)} threads are still unnatended")

def handle(msg):
    try:
        new_thread = threading.Thread(target=thread_function, args=(msg,))
        unnatended_threads.append(new_thread)
        run_unnatendedthreads()
    except Exception:
        send_message(cookiebot, mekhyID, traceback.format_exc())

def handle_query(msg):
    try:
        new_thread = threading.Thread(target=thread_function_query, args=(msg,))
        unnatended_threads.append(new_thread)
        run_unnatendedthreads()
    except Exception:
        send_message(cookiebot, mekhyID, traceback.format_exc())

def scheduler_check():
    print("SCHEDULER CHECK")
    try:
        scheduler_pull(cookiebot, is_alternate_bot=is_alternate_bot)
    except Exception:
        send_message(cookiebot, mekhyID, traceback.format_exc())
    finally:
        timer_scheduler_check = threading.Timer(300, scheduler_check)
        timer_scheduler_check.start()
        
if __name__ == '__main__':
    if not is_alternate_bot:
        scheduler_check()
    MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()
