import os
from dotenv import load_dotenv
import telepot
from telepot.loop import MessageLoop
load_dotenv()
token = os.getenv('testbotTOKEN')
mekhyID = 780875868
bot = telepot.Bot(token)
updates = bot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    bot.getUpdates(offset=last_update_id+1)
bot.sendMessage(mekhyID, 'testbot started')

def handle(msg):
    content_type, _, _ = telepot.glance(msg)
    print(content_type, msg)
    if content_type == 'photo':
        path = bot.getFile(msg['photo'][-1]['file_id'])['file_path']
        image_url = f'https://api.telegram.org/file/bot{token}/{path}'
        print(msg['caption'])
        bot.sendPhoto(mekhyID, msg['photo'][-1]['file_id'], caption=image_url)
    elif content_type == 'video':
        path = bot.getFile(msg['video']['file_id'])['file_path']
        video_url = f'https://api.telegram.org/file/bot{token}/{path}'
        bot.sendVideo(mekhyID, msg['video']['file_id'], caption=video_url)

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    print(msg)

MessageLoop(bot, {'chat': handle, 'callback_query': handle_query}).run_forever()
