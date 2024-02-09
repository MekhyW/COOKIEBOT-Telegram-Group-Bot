import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, Message
import requests
import urllib3
token = ''
mekhyID = 780875868
testgroupID = -1001499400382
bot = telepot.Bot(token)

pfps = bot.getUserProfilePhotos(mekhyID, limit=1)
bot.sendPhoto(mekhyID, pfps['photos'][0][-1]['file_id'])
bot.sendPoll(mekhyID, 'Teste de enquete', ['Opção 1', 'Opção 2'], is_anonymous=False, allows_multiple_answers=False, open_period=60)

def changecmds(bot):
    url = 'https://api.telegram.org/bot{}/setMyCommands'.format(token)
    data = {'commands': [{'command': 'start', 'description': 'start bot'},
                         {'command': 'help', 'description': 'help'},
                         {'command': 'test', 'description': 'test'}],
            'scope': {'type': 'chat', 'chat_id': mekhyID}}
    requests.get(url, json=data)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, msg)
    if content_type == 'photo':
        path = bot.getFile(msg['photo'][-1]['file_id'])['file_path']
        image_url = 'https://api.telegram.org/file/bot{}/{}'.format(token, path)
        print(msg['caption'])
        bot.sendPhoto(mekhyID, msg['photo'][-1]['file_id'], caption=image_url)
    elif content_type == 'video':
        path = bot.getFile(msg['video']['file_id'])['file_path']
        video_url = 'https://api.telegram.org/file/bot{}/{}'.format(token, path)
        bot.sendVideo(mekhyID, msg['video']['file_id'], caption=video_url)

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    print(msg)

def Send(cookiebot, chat_id, text, msg_to_reply=None, language="pt", thread_id=None, isBombot=False, reply_markup=None):
    try:
        if msg_to_reply:
            reply_id = msg_to_reply['message_id']
            cookiebot.sendMessage(chat_id, text, reply_to_message_id=reply_id, reply_markup=reply_markup)
        elif thread_id is not None:
            url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}&message_thread_id={thread_id}"
            requests.get(url)
        else:
            cookiebot.sendMessage(chat_id, text, reply_markup=reply_markup)
    except urllib3.exceptions.ProtocolError:
        Send(cookiebot, chat_id, text, msg_to_reply, language, thread_id, isBombot, reply_markup)
    except Exception as e:
        print(e)


MessageLoop(bot, {'chat': handle, 'callback_query': handle_query}).run_forever()