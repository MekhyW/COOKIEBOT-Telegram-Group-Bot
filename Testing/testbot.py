import os
from dotenv import load_dotenv
import telepot
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
    content_type, _, _ = telepot.glance(msg)
    print(content_type, msg)

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    print(msg)

MessageLoop(bot, {'chat': handle, 'callback_query': handle_query}).run_forever()
