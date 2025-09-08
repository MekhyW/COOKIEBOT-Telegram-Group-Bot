import sqlite3
from universal_funcs import send_chat_action, send_message, send_photo, delete_message, ownerID
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import random
import cv2
import numpy as np
import threading
import json
import datetime
from Configurations import get_config
from SocialContent import get_profile_image
from loc import i18n
local_storage = threading.local()
db_lock = threading.RLock()

def get_db_connection():
    if not hasattr(local_storage, 'giveaways_db'):
        local_storage.giveaways_db = sqlite3.connect('Giveaways.db')
        local_storage.giveaways_cursor = local_storage.giveaways_db.cursor()
        local_storage.giveaways_cursor.execute("CREATE TABLE IF NOT EXISTS giveaways (creator_id INT, message_id INT, chat_id INT, prize TEXT, number_of_winners INT, participants TEXT)")
        local_storage.giveaways_db.commit()
    return local_storage.giveaways_db, local_storage.giveaways_cursor

def giveaways_ask(cookiebot, msg, chat_id, language, listaadmins_id, listaadmins_status):
    send_chat_action(cookiebot, chat_id, 'typing')
    if 'creator' in listaadmins_status and str(msg['from']['id']) not in listaadmins_id and str(msg['from']['id']) != str(ownerID):
        text = i18n.get("giveaway.permission", lang=language)
        send_message(cookiebot, chat_id, text, msg)
        return
    if len(msg['text'].split()) == 1:
        text = i18n.get("giveaway.raffled", lang=language)
        send_message(cookiebot, chat_id, text, msg)
        return
    prize_text = " ".join(msg["text"].split()[1:])
    prize = json.dumps(prize_text)[:20]
    text = i18n.get("giveaway.create", lang=language)
    send_chat_action(cookiebot, chat_id, 'typing')
    send_message(cookiebot, chat_id, text, msg, 
                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="1", callback_data=f'GIVEAWAY 1 {prize}')],
                     [InlineKeyboardButton(text="2", callback_data=f'GIVEAWAY 2 {prize}')],
                     [InlineKeyboardButton(text="3", callback_data=f'GIVEAWAY 3 {prize}')],
                     [InlineKeyboardButton(text="4", callback_data=f'GIVEAWAY 4 {prize}')],
                     [InlineKeyboardButton(text="5", callback_data=f'GIVEAWAY 5 {prize}')],
                 ]))
    
def giveaways_create(cookiebot, msg, n_winners, chat_id, prize):
    if not isinstance(n_winners, int) or n_winners <= 0 or n_winners > 5:
        return
    language = get_config(cookiebot, chat_id)[7]
    ctx = {
        "prize" = prize,
        "win": n_winners,
        "date": datetime.datetime.now().strftime(i18n.get("giveaway.strftime", lang=language))
    }
    text = i18n.get("giveaway.time", lang=language, **ctx)
    buttons = i18n.get("giveaway.buttons", lang=language)
    giveaways_msg_id = send_message(cookiebot, chat_id, text,
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text=buttons[0], callback_data=f'GIVEAWAY enter')],
                                     [InlineKeyboardButton(text=buttons[1], callback_data=f'GIVEAWAY end')],
                                 ])
                                )['message_id']
    with db_lock:
        db, cursor = get_db_connection()
        cursor.execute("INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?)", (int(msg['from']['id']), int(giveaways_msg_id), int(chat_id), str(prize), int(n_winners), ""))
        db.commit()
    try:
        cookiebot.pinChatMessage(chat_id, giveaways_msg_id)
    except Exception:
        pass

def giveaways_enter(cookiebot, msg, chat_id):
    try:
        language = get_config(cookiebot, chat_id)[7]
        participant = "@" + msg['from']['username'] if 'username' in msg['from'] else msg['from']['first_name']
        giveaways_msg_id = msg['message']['message_id']
        with db_lock:
            db, cursor = get_db_connection()
            cursor.execute("SELECT participants FROM giveaways WHERE message_id = ?", (giveaways_msg_id,))
            result = cursor.fetchone()
            if not result:
                text = i18n.get("giveaway.not_found", lang=language)
                cookiebot.answerCallbackQuery(msg['id'], text=text)
                return
            current_participants = result[0]
            if participant in (current_participants.split(", ") if current_participants else []):
                text = i18n.get("giveaway.in", lang=language)
                cookiebot.answerCallbackQuery(msg['id'], text=text)
                return
            updated_participants = (current_participants + ", " + participant).strip(", ") if current_participants else participant
            cursor.execute("UPDATE giveaways SET participants = ? WHERE message_id = ?", (updated_participants, giveaways_msg_id,))
            db.commit()
        text = i18n.get("giveaway.enter", lang=language)
        cookiebot.answerCallbackQuery(msg['id'], text=text)
    except Exception as e:
        text = i18n.get("giveaway.error", lang=language)
        cookiebot.answerCallbackQuery(msg['id'], text=text)

def giveaways_end(cookiebot, msg, chat_id, listaadmins_id):
    try:
        language = get_config(cookiebot, chat_id)[7]
        giveaways_msg_id = msg['message']['message_id']
        with db_lock:
            db, cursor = get_db_connection()
            cursor.execute("SELECT creator_id, prize, number_of_winners, participants FROM giveaways WHERE message_id = ?", (giveaways_msg_id,))
            result = cursor.fetchone()
            if not result:
                text = i18n.get("giveaway.not_found", lang=language)
                cookiebot.answerCallbackQuery(msg['id'], text=text)
                return
            creator_id, prize, n_winners, participants_str = result
            if msg['from']['id'] not in [int(admin_id) for admin_id in listaadmins_id] and msg['from']['id'] != creator_id and msg['from']['id'] != ownerID:
                text = i18n.get("giveaway.end_adm", lang=language)
                cookiebot.answerCallbackQuery(msg['id'], text=text)
                return
            if not participants_str:
                text = i18n.get("giveaway.no_one", lang=language)
                send_message(cookiebot, chat_id, text, language=language)
                cursor.execute("DELETE FROM giveaways WHERE message_id = ?", (giveaways_msg_id,))
                db.commit()
                text = i18n.get("giveaway.end", lang=language)
                cookiebot.answerCallbackQuery(msg['id'], text=text)
                delete_message(cookiebot, telepot.message_identifier(msg['message']))
                return
            participants = participants_str.split(", ")
            actual_winners = min(n_winners, len(participants))
            winners = random.sample(participants, actual_winners)
            for winner_idx, winner in enumerate(winners):
                key = "giveaway.winnner.one" if n_winners  == 1 else "giveaway.winnner.more"
                ctx = {
                    "idx": winner_idx + 1,
                    "winner": winner,
                    "prize": prize
                }
                caption = i18n.get(key, lang=language, **ctx)
                try:
                    user_img = get_profile_image(winner.replace('@',''))
                    user_img = cv2.imdecode(np.asarray(bytearray(user_img.read()), dtype="uint8"), cv2.IMREAD_COLOR)
                except Exception as e:
                    user_img = None
                if user_img is not None:
                    cv2.imwrite('temp.jpg', user_img)
                    with open('temp.jpg', 'rb') as final_img:
                        send_photo(cookiebot, chat_id, final_img, caption, language=language)
                else:
                    send_message(cookiebot, chat_id, caption, language=language)
        text = i18n.get("giveaway.draw_more", lang=language)
        giveaways_msg_id_new = send_message(cookiebot, chat_id, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅", callback_data="GIVEAWAY end")],
            [InlineKeyboardButton(text="❌", callback_data="GIVEAWAY delete")],
        ]))['message_id']
        with db_lock:
            db, cursor = get_db_connection()
            cursor.execute("UPDATE giveaways SET message_id = ? WHERE message_id = ?", (giveaways_msg_id_new, giveaways_msg_id))
            db.commit()
        text = i18n.get("giveaway.selected", lang=language)
        cookiebot.answerCallbackQuery(msg['id'], text=text)
        delete_message(cookiebot, telepot.message_identifier(msg['message']))
    except Exception as e:
         = i18n.get("giveaway.end_error", lang=language)
        cookiebot.answerCallbackQuery(msg['id'], text=text)

def giveaways_delete(cookiebot, msg, chat_id):
    language = get_config(cookiebot, chat_id)[7]
    with db_lock:
        db, cursor = get_db_connection()
        cursor.execute("DELETE FROM giveaways WHERE message_id = ?", (msg['message']['message_id'],))
        db.commit()
    text = i18n.get("giveaway.end", lang=language)
    cookiebot.answerCallbackQuery(msg['id'], text=text)
    delete_message(cookiebot, telepot.message_identifier(msg['message']))