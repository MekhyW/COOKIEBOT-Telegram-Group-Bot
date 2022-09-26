from multiprocessing.connection import wait
from universal_funcs import *

def AskPublisher(cookiebot, msg, chat_id, language):
    cookiebot.sendMessage(chat_id, "Publish post?", reply_to_message_id=msg['message_id'], 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data='ApprovePub {}-{}'.format(str(chat_id)))],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))

def GetActivity(chat_id):
    wait_open('MessageActivity/{}.json'.format(str(chat_id)))
    with open('MessageActivity/{}.json'.format(str(chat_id)), 'r') as f:
        activity = json.load(f)
    f.close()
    return activity

def GetPostQueue():
    wait_open('PostQueue.json')
    with open('PostQueue.json', 'r', encoding='utf-8') as f:
        queue = json.load(f)
    f.close()
    return queue

def SchedulePost(cookiebot, query_data, from_id):
    origin_chatid = query_data.split()[1].split('-')[0]
    origin_messageid = query_data.split()[1].split('-')[1]
    #use google cloud scheduler to get list of active jobs
    #if there is a job with the same origin_chatid, delete all jobs with that origin_chatid
    queue = GetPostQueue()
    answer = "Post marcado para os horários:\n"
    for group in os.listdir('Registers'):
        activity = GetActivity(group)
        #use formula score=A/min(dt) to schedule post on best time for the group
        #append destination_chatid and time to answer
        if not any(d['origin_chatid'] == origin_chatid and d['destination_chatid'] == group for d in queue):
            queue.append({'origin_chatid':origin_chatid, 'destination_chatid':group, 'origin_messageid':origin_messageid, 'remaining':3})
    with open('PostQueue.json', 'w') as f:
        json.dump(queue, f)
    f.close()
    try:
        Send(cookiebot, from_id, answer)
    except:
        Send(cookiebot, origin_chatid, "Post adicionado à fila porém não consegui te mandar uma mensagem. Mande /start no meu privado para eu poder te mandar mensagens.")

def Post(post):
    #called by scheduler
    #posts post
    queue = GetPostQueue()
    for d in queue:
        if d['origin_chatid'] == origin_chatid and d['destination_chatid'] == group:
            d['remaining'] -= 1
            if d['remaining'] <= 0:
                queue.remove(d)

def RestartActivityRegister(date, chat_id):
    activity = {'date': date, 'activity': [0]*(24*60)}
    with open('MessageActivity/{}.json'.format(str(chat_id)), 'w') as f:
        json.dump(activity, f)
    f.close()

def RegisterActivity(msg, chat_id):
    messageTime = datetime.datetime.utcfromtimestamp(msg['date'])
    messageTime = messageTime.strftime('%Y-%m-%d %H:%M:%S')
    date = messageTime.split()[0]
    time = messageTime.split()[1].split(':')
    hour = int(time[0])
    minute = int(time[1])
    bin = hour*60 + minute
    if not os.path.exists('MessageActivity/{}.json'.format(str(chat_id))) or not os.path.getsize('MessageActivity/{}.json'.format(str(chat_id))):
        RestartActivityRegister(date, chat_id)
    activity = GetActivity(chat_id)
    if activity['date'] != date:
        RestartActivityRegister(date, chat_id)
    activity[bin] += 1
    with open('MessageActivity/{}.json'.format(str(chat_id)), 'w') as f:
        json.dump(activity, f)
    f.close()