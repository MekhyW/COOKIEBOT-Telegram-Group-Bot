from universal_funcs import *
from google.cloud import scheduler_v1
from google.cloud import pubsub_v1
client = scheduler_v1.CloudSchedulerClient.from_service_account_json("cookiebot_pubsub.json")
subscriber = pubsub_v1.SubscriberClient.from_service_account_json("cookiebot_pubsub.json")
project_id = "cookiebot-309512"
project_path = f"projects/{project_id}"
parent = f"{project_path}/locations/southamerica-east1"

def AskPublisher(cookiebot, msg, chat_id, language):
    if language == "pt":
        answer = "Publicar postagem?"
    else:
        answer = "Publish post?"
    cookiebot.sendMessage(chat_id, answer, reply_to_message_id=msg['message_id'], 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data='ApprovePub {}-{}'.format(str(chat_id), str(msg['message_id'])))],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))

def create_job(job_name, job_description, job_data, job_schedule):
    job = {
        'name': client.job_path(project_id, 'southamerica-east1', job_name),
        'description': job_description,
        'pubsub_target': {
            'topic_name': 'projects/cookiebot-309512/topics/cookiebot-publisher-topic',
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

def SchedulePost(cookiebot, query_data, from_id):
    origin_chatid = query_data.split()[1].split('-')[0]
    origin_messageid = query_data.split()[1].split('-')[1]
    jobs = list_jobs()
    #if there is a job with the same origin_chatid, delete all jobs with that origin_chatid
    answer = "Post marcado para os horários:\n"
    for group in os.listdir('Registers'):
        number_of_people_in_group = cookiebot.getChatMembersCount(group.replace('.txt', ''))
        if math.floor(number_of_people_in_group/50) < 0:
            continue
        #if the number of posts scheduled for the group is larger than 2*floor(number_of_people_in_group/50), unschedule oldest post for that group
        #schedule post on random time for the group, for the next 3 days
        #append destination_chatid and time to answer
        pass
    try:
        Send(cookiebot, from_id, answer)
    except:
        Send(cookiebot, origin_chatid, "Post adicionado à fila porém não consegui te mandar uma mensagem. Mande /start no meu privado para eu poder te mandar mensagens.")

def publisher_topic_callback(post):
    #called by scheduler
    #posts post
    print("Posted post: {}".format(post))
    post.ack()

def startPublisher(isBombot):
    if isBombot:
        subscription_path = subscriber.subscription_path(project_id, "bombot-subscription")
    else:
        subscription_path = subscriber.subscription_path(project_id, "cookiebot-subscription")
    subscriber.subscribe(subscription_path, callback=publisher_topic_callback)