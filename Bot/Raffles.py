import sqlite3
from universal_funcs import send_chat_action, send_message, forward_message, get_request_backend, react_to_message, emojis_to_numbers, ownerID, exchangerate_key, logger, translate
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
raffles_db = sqlite3.connect('Raffles.db', check_same_thread=False)
raffles_cursor = raffles_db.cursor()
raffles_cursor.execute("CREATE TABLE IF NOT EXISTS raffles (message_id INT, chat_id INT, prize TEXT, number_of_winners INT, participants TEXT)")
raffles_db.commit()

def raffle_ask(cookiebot, msg, chat_id, language, listaadmins_id, listaadmins_status):
    send_chat_action(cookiebot, chat_id, 'typing')
    if 'creator' in listaadmins_status and str(msg['from']['id']) not in listaadmins_id and str(msg['from']['id']) != str(ownerID):
        send_message(cookiebot, chat_id, "Você não tem permissão para criar sorteios! \n <blockquote> Se está falando como usuário e não como canal? A permissão 'permanecer anônimo' deve estar desligada! </blockquote>", msg, language)
        return
    if len(msg['text'].split()) == 1:
        send_message(cookiebot, chat_id, "Você precisa digitar o que está sendo sorteado!\n<blockquote> EXEMPLO: /sorteio Fursuit do Mekhy 🐾🦝 </blockquote>", msg, language)
        return
    prize = {" ".join(msg["text"].split()[1:])}
    send_message(cookiebot, chat_id, "Vamos criar um sorteio! \n Quantos usuários serão sorteados?", msg, language, 
                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="1", callback_data=f'RAFFLE 1 {language} {prize}')],
                     [InlineKeyboardButton(text="2", callback_data=f'RAFFLE 2 {language} {prize}')],
                     [InlineKeyboardButton(text="3", callback_data=f'RAFFLE 3 {language} {prize}')],
                     [InlineKeyboardButton(text="4", callback_data=f'RAFFLE 4 {language} {prize}')],
                     [InlineKeyboardButton(text="5", callback_data=f'RAFFLE 5 {language} {prize}')],
                 ]))
    
def raffle_create(cookiebot, n_winners, chat_id, language, prize):
    raffle_msg_id = send_message(cookiebot, chat_id, f"🎰 É HORA DO SORTEIO! 🎰 \n 🎯 O Prêmio é: {prize}", language=language,
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text="Quero Entrar!" if language=='pt' else "Put me in!", callback_data=f'RAFFLE ENTER')],
                                     [InlineKeyboardButton(text="ADMINS: Finalizar Sorteio" if language=='pt' else "ADMINS: End Raffle", callback_data=f'RAFFLE END')],
                                 ])
                                )['message_id']
    raffles_cursor.execute("INSERT INTO raffles VALUES (?, ?, ?, ?, ?)", (int(raffle_msg_id), int(chat_id), prize, n_winners, ""))

def raffle_enter(cookiebot, msg, chat_id, language):
    pass

def raffle_end(cookiebot, message_id, chat_id, language):
    pass
