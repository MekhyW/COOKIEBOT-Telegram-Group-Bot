import os
from dotenv import load_dotenv
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup
import time
load_dotenv()
token = os.getenv('testbotTOKEN')
ownerID = 780875868
bot = telepot.Bot(token)
updates = bot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    bot.getUpdates(offset=last_update_id+1)
bot.sendMessage(ownerID, 'testbot started', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    [telepot.namedtuple.InlineKeyboardButton(text='test', callback_data='test')]
]))

def handle(msg):
    content_type, _, chat_id = telepot.glance(msg)
    print(content_type, msg)
    time.sleep(2)
    bot.forwardMessage(ownerID, chat_id, msg['message_id'])

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    chat_id = msg['chat']['id'] if 'chat' in msg else from_id
    bot.sendMessage(chat_id, f"{query_id}\n{from_id}\n{query_data}")
    print('Callback Query:', query_id, from_id, query_data)
    print(msg)

MessageLoop(bot, {'chat': handle, 'callback_query': handle_query}).run_forever()
