import sqlite3
from universal_funcs import send_chat_action, send_message, send_photo, delete_message, ownerID, logger
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
        text = "Você não tem permissão para criar sorteios! \n <blockquote> Se está falando como usuário e não como canal? A permissão 'permanecer anônimo' deve estar desligada! </blockquote>" if language == 'pt' else "¡No tienes permiso para crear sorteos! \n <blockquote> ¿Si hablas como usuario y no como canal? ¡El permiso de anonimato debe estar desactivado! </blockquote>" if language == 'es' else "You don't have permission to create giveaways! \n <blockquote> If you are speaking as a user and not as a channel? The 'stay anonymous' permission must be turned off! </blockquote>"
        send_message(cookiebot, chat_id, text, msg)
        return
    if len(msg['text'].split()) == 1:
        text = "Você precisa digitar o que está sendo sorteado! \n <blockquote> EXEMPLO: /giveaway Fursuit do Mekhy 🐾🦝 </blockquote>" if language == 'pt' else "¡Necesitas escribir lo que se está sorteando! \n <blockquote> EJEMPLO: /giveaway Fursuit de Mekhy 🐾🦝 </blockquote>" if language == 'es' else "You need to type what is being raffled! \n <blockquote> EXAMPLE: /giveaway Fursuit of Mekhy 🐾🦝 </blockquote>"
        send_message(cookiebot, chat_id, text, msg)
        return
    prize_text = " ".join(msg["text"].split()[1:])
    prize = json.dumps(prize_text)[:20]
    text = "Vamos criar um sorteio! \n Quantos usuários serão sorteados?" if language == 'pt' else "¡Vamos a crear un sorteo! \n ¿Cuántos usuarios serán sorteados?" if language == 'es' else "Let's create a giveaway! \n How many users will be drawn?"
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
        logger.log_text(f"Invalid number of giveaway winners: {n_winners}", severity="WARNING")
        return
    language = get_config(cookiebot, chat_id)[7]
    text = f"🎰 É HORA DO SORTEIO! 🎰 \n \n 🎯 O Prêmio é: <b> {prize} </b> \n 👥 Número de vencedores: {n_winners} \n ⌛ Começou em: {datetime.datetime.now().strftime('%d/%m, %H:%M')}" if language == 'pt' else f"🎰 ¡ES HORA DEL SORTEO! 🎰 \n \n 🎯 El premio es: <b>{prize}</b> \n 👥 Número de ganadores: {n_winners} \n ⌛ Comenzó el: {datetime.datetime.now().strftime('%d/%m, %H:%M')}" if language == 'es' else f"🎰 IT'S GIVEAWAY TIME! 🎰 \n \n 🎯 The Prize is: <b>{prize}</b> \n 👥 Number of winners: {n_winners} \n ⌛ Started on: {datetime.datetime.now().strftime('%m/%d, %H:%M')}"
    giveaways_msg_id = send_message(cookiebot, chat_id, text,
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text="Quero Entrar!" if language=='pt' else "Put me in!", callback_data=f'GIVEAWAY enter')],
                                     [InlineKeyboardButton(text="ADMINS: Finalizar Sorteio" if language=='pt' else "ADMINS: End Giveaway", callback_data=f'GIVEAWAY end')],
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
    logger.log_text(f"Giveaway created in chat with ID {chat_id}", severity="INFO")

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
                cookiebot.answerCallbackQuery(msg['id'], text="Sorteio não encontrado" if language =='pt' else "Giveaway not found")
                return
            current_participants = result[0]
            if participant in (current_participants.split(", ") if current_participants else []):
                cookiebot.answerCallbackQuery(msg['id'], text="Você já está participando!" if language =='pt' else "You are already participating!")
                return
            updated_participants = (current_participants + ", " + participant).strip(", ") if current_participants else participant
            cursor.execute("UPDATE giveaways SET participants = ? WHERE message_id = ?", (updated_participants, giveaways_msg_id,))
            db.commit()
        cookiebot.answerCallbackQuery(msg['id'], text="YAY! Você entrou no sorteio!" if language =='pt' else "YAY! You entered the giveaway!")
    except Exception as e:
        logger.log_text(f"Error entering giveaway: {str(e)}", severity="ERROR")
        cookiebot.answerCallbackQuery(msg['id'], text="Erro ao entrar no sorteio" if language =='pt' else "Error entering giveaway")

def giveaways_end(cookiebot, msg, chat_id, listaadmins_id):
    try:
        language = get_config(cookiebot, chat_id)[7]
        giveaways_msg_id = msg['message']['message_id']
        with db_lock:
            db, cursor = get_db_connection()
            cursor.execute("SELECT creator_id, prize, number_of_winners, participants FROM giveaways WHERE message_id = ?", (giveaways_msg_id,))
            result = cursor.fetchone()
            if not result:
                cookiebot.answerCallbackQuery(msg['id'], text="Sorteio não encontrado" if language =='pt' else "Giveaway not found")
                return
            creator_id, prize, n_winners, participants_str = result
            if msg['from']['id'] not in [int(admin_id) for admin_id in listaadmins_id] and msg['from']['id'] != creator_id and msg['from']['id'] != ownerID:
                cookiebot.answerCallbackQuery(msg['id'], text="Apenas admins podem encerrar!" if language =='pt' else "Only admins can end!")
                return
            if not participants_str:
                send_message(cookiebot, chat_id, "Nenhum participante no sorteio!" if language =='pt' else "No participants in the giveaway!", language=language)
                cursor.execute("DELETE FROM giveaways WHERE message_id = ?", (giveaways_msg_id,))
                db.commit()
                cookiebot.answerCallbackQuery(msg['id'], text="Sorteio encerrado" if language =='pt' else "Giveaway ended")
                delete_message(cookiebot, telepot.message_identifier(msg['message']))
                return
            participants = participants_str.split(", ")
            actual_winners = min(n_winners, len(participants))
            if actual_winners < n_winners:
                logger.log_text(f"Warning: Only {actual_winners} winners selected for giveaway (requested {n_winners})", severity="WARNING")
            winners = random.sample(participants, actual_winners)
            for winner_idx, winner in enumerate(winners):
                caption = f"Temos um vencedor! \n 🎉 Parabéns {winner}, você ganhou <b> {prize} </b>! 🎉" if n_winners == 1 else f"Nosso {winner_idx + 1}º vencedor é... \n 🎉 Parabéns {winner}, você ganhou <b> {prize} </b>! 🎉"
                try:
                    user_img = get_profile_image(winner.replace('@',''))
                    user_img = cv2.imdecode(np.asarray(bytearray(user_img.read()), dtype="uint8"), cv2.IMREAD_COLOR)
                except Exception as e:
                    logger.log_text(f"Error getting profile image: {str(e)}", severity="WARNING")
                    user_img = None
                if user_img is not None:
                    cv2.imwrite('temp.jpg', user_img)
                    with open('temp.jpg', 'rb') as final_img:
                        send_photo(cookiebot, chat_id, final_img, caption, language=language)
                else:
                    send_message(cookiebot, chat_id, caption, language=language)
        text = "Sortear mais ganhadores?" if language =='pt' else "Sortear más ganadores?" if language == 'es' else "Draw more winners?"
        giveaways_msg_id_new = send_message(cookiebot, chat_id, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅", callback_data="GIVEAWAY end")],
            [InlineKeyboardButton(text="❌", callback_data="GIVEAWAY delete")],
        ]))['message_id']
        with db_lock:
            db, cursor = get_db_connection()
            cursor.execute("UPDATE giveaways SET message_id = ? WHERE message_id = ?", (giveaways_msg_id_new, giveaways_msg_id))
            db.commit()
        cookiebot.answerCallbackQuery(msg['id'], text="Ganhadores sorteados" if language =='pt' else "Winners selected")
        delete_message(cookiebot, telepot.message_identifier(msg['message']))
    except Exception as e:
        logger.log_text(f"Error ending giveaway: {str(e)}", severity="ERROR")
        cookiebot.answerCallbackQuery(msg['id'], text="Erro ao encerrar sorteio" if language =='pt' else "Error ending giveaway")

def giveaways_delete(cookiebot, msg, chat_id):
    language = get_config(cookiebot, chat_id)[7]
    with db_lock:
        db, cursor = get_db_connection()
        cursor.execute("DELETE FROM giveaways WHERE message_id = ?", (msg['message']['message_id'],))
        db.commit()
    cookiebot.answerCallbackQuery(msg['id'], text="Sorteio encerrado" if language =='pt' else "Giveaway ended")
    delete_message(cookiebot, telepot.message_identifier(msg['message']))