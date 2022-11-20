from universal_funcs import *
from google.cloud import scheduler_v1
from google.cloud import pubsub_v1
client = scheduler_v1.CloudSchedulerClient.from_service_account_json("cookiebot_pubsub.json")
subscriber = pubsub_v1.SubscriberClient.from_service_account_json("cookiebot_pubsub.json")
project_id = "cookiebot-309512"
project_path = f"projects/{project_id}"
parent = f"{project_path}/locations/southamerica-east1"
topic_name = 'projects/cookiebot-309512/topics/cookiebot-publisher-topic'
subscription_path = None

def AskPublisher(cookiebot, msg, chat_id, language):
    if language == "pt":
        answer = "Publicar postagem?"
    else:
        answer = "Publish post?"
    cookiebot.sendMessage(chat_id, answer, reply_to_message_id=msg['message_id'], 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data='SendToApprovalPub {} {} {}'.format(str(chat_id), str(msg['message_id']), str(msg['from']['id'])))],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))

def AskApproval(cookiebot, query_data):
    origin_chatid = query_data.split()[1]
    origin_messageid = query_data.split()[2]
    origin_userid = query_data.split()[3]
    cookiebot.forwardMessage(mekhyID, origin_chatid, origin_messageid)
    cookiebot.sendMessage(mekhyID, 'Approve post?', 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data='ApprovePub {}-{}-{}'.format(origin_chatid, origin_messageid, origin_userid))],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))

def create_job(job_name, job_description, job_data, job_schedule):
    job = {
        'name': client.job_path(project_id, 'southamerica-east1', job_name),
        'description': job_description,
        'pubsub_target': {
            'topic_name': topic_name,
            'data': job_data,
        },
        'schedule': job_schedule,
    }
    response = client.create_job(parent=parent, job=job)
    print('Created job: {}'.format(response.name))
    return response

def list_jobs():
    response = client.list_jobs(parent=parent)
    jobs = []
    for job in response:
        jobs.append(job)
    return jobs

def delete_job(job_name):
    response = client.delete_job(job_name)
    print('Deleted job: {}'.format(response))
    return response

def SchedulePost(cookiebot, query_data):
    origin_chatid = query_data.split()[1]
    origin_messageid = query_data.split()[2]
    origin_userid = query_data.split()[3]
    jobs = list_jobs()
    for job in jobs:
        if job.name == origin_chatid:
            delete_job(job.name)
    answer = "Post marcado para os horários (3 dias):\n"
    for group in os.listdir('Registers'):
        group_id = group.split('.')[0]
        num_posts_for_group = 0
        for job in jobs:
            if job.description == group_id:
                num_posts_for_group += 1
        if num_posts_for_group < 2*math.floor(cookiebot.getChatMembersCount(group_id)/50):
            hour = random.randint(0,23)
            minute = random.randint(0,59)
            create_job(origin_chatid, group_id, "3 "+origin_chatid+" "+group_id+" "+origin_messageid, f"{minute} {hour} * * *")
            answer += f"{hour}:{minute} - {cookiebot.getChat(group_id)['title']}\n"
    try:
        Send(cookiebot, origin_userid, answer)
    except:
        Send(cookiebot, origin_chatid, "Post adicionado à fila porém não consegui te mandar uma mensagem. Mande /start no meu privado para eu poder te mandar mensagens.")

def SchedulerPull(cookiebot):
    response = subscriber.pull(subscription=subscription_path, max_messages=1, return_immediately=True)
    received_messages = response.received_messages
    for message in received_messages:
        print(message.message.data)
        remaining_times = int(message.message.data.split()[0]) - 1
        origin_chatid = message.message.data.split()[1]
        group_id = message.message.data.split()[2]
        origin_messageid = message.message.data.split()[3]
        message.ack()
        if remaining_times <= 0:
            delete_job(origin_chatid)
        #cookiebot.forwardMessage(group_id, origin_chatid, origin_messageid)
    return received_messages

def startPublisher(isBombot):
    global subscription_path
    if isBombot:
        subscription_path = subscriber.subscription_path(project_id, "bombot-subscription")
    else:
        subscription_path = subscriber.subscription_path(project_id, "cookiebot-subscription")