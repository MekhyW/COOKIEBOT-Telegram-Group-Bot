from universal_funcs import *

def AskPublisher(cookiebot, msg, chat_id, language):
    cookiebot.sendMessage(chat_id, "Publish post?", reply_to_message_id=msg['message_id'], 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data='ApprovePub {}-{}'.format(str(chat_id)))],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))

def RestartActivityRegister(date, chat_id):
    with open('MessageActivity/{}.txt'.format(str(chat_id)), 'w') as f:
        f.write(date+'\n')
        for bin in range(24*60):
            f.write(str(bin) + ': 0\n')
    f.close()

def RegisterActivity(msg, chat_id):
    messageTime = datetime.datetime.utcfromtimestamp(msg['date'])
    messageTime = messageTime.strftime('%Y-%m-%d %H:%M:%S')
    date = messageTime.split()[0]
    time = messageTime.split()[1].split(':')
    hour = int(time[0])
    minute = int(time[1])
    bin = hour*60 + minute
    if not os.path.exists('MessageActivity/{}.txt'.format(str(chat_id))):
        RestartActivityRegister(date, chat_id)
    wait_open('MessageActivity/{}.txt'.format(str(chat_id)))
    with open('MessageActivity/{}.txt'.format(str(chat_id)), 'r') as f:
        lines = f.readlines()
    f.close()
    if line[0] != date:
        RestartActivityRegister(date, chat_id)
    with open('MessageActivity/{}.txt'.format(str(chat_id)), 'w') as f:
        for line in lines:
            if line.startswith(str(bin)+':'):
                line = line.split(' ')
                line[1] = str(int(line[1]) + 1)
                line = ' '.join(line)
            f.write(line)
        f.truncate()
    f.close()