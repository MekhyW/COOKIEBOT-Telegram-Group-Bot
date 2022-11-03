from universal_funcs import *

def AskPublisher(cookiebot, msg, chat_id, language):
    cookiebot.sendMessage(chat_id, "Publish post?", reply_to_message_id=msg['message_id'], 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data='ApprovePub {}-{}'.format(str(chat_id)))],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))

def SchedulePost(cookiebot, query_data, from_id):
    origin_chatid = query_data.split()[1].split('-')[0]
    origin_messageid = query_data.split()[1].split('-')[1]
    #use backend to get list of active jobs
    #if there is a job with the same origin_chatid, delete all jobs with that origin_chatid
    answer = "Post marcado para os horários:\n"
    for group in os.listdir('Registers'):
        #if floor(number_of_people_in_group/50) < 0:
        #    continue
        #schedule post on random time for the group, for the next 3 days
        #if the number of posts scheduled for the group is larger than 2*floor(number_of_people_in_group/50), unschedule oldest post for that group
        #append destination_chatid and time to answer
        pass
    try:
        Send(cookiebot, from_id, answer)
    except:
        Send(cookiebot, origin_chatid, "Post adicionado à fila porém não consegui te mandar uma mensagem. Mande /start no meu privado para eu poder te mandar mensagens.")

def Post(post):
    #called by scheduler
    #posts post
    pass