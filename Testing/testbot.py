import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, Message
token = ''
mekhyID = 780875868
testgroupID = -1001618375433

bot = telepot.Bot(token)

#bot.sendMessage(testgroupID, 'test query', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#                   [InlineKeyboardButton(text='test', callback_data='test')]]))

def changecmds(bot):
    bot.setMyCommands(commands=[{'command': 'idk', 'description': 'description'}], scope={"type": "chat", 'chat_id': mekhyID})

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    if content_type == 'photo':
        path = bot.getFile(msg['photo'][-1]['file_id'])['file_path']
        image_url = 'https://api.telegram.org/file/bot{}/{}'.format(token, path)
        bot.sendMessage(chat_id, image_url)

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

MessageLoop(bot, {'chat': handle, 'callback_query': handle_query}).run_forever()