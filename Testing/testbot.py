import os
import telepot
import threading
from dotenv import load_dotenv
from telepot.loop import MessageLoop
load_dotenv()
token = os.getenv('cookiebotTOKEN')
ownerID = 780875868
bot = telepot.Bot(token)
updates = bot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    bot.getUpdates(offset=last_update_id+1)
bot.sendMessage(ownerID, 'testbot started')

def handle(msg):
    def handle_message():
        content_type, _, _ = telepot.glance(msg)
        print(content_type, msg)
    threading.Thread(target=handle_message).start()

def handle_query(msg):
    def handle_callback():
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)
        print(msg)
    threading.Thread(target=handle_callback).start()

MessageLoop(bot, {'chat': handle, 'callback_query': handle_query}).run_forever()
