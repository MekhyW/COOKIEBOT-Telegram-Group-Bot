from universal_funcs import *
from Configurations import *
from google.cloud import scheduler_v1
from google.cloud import pubsub_v1
from forex_python.converter import CurrencyRates
from forex_python.converter import CurrencyCodes
from price_parser import Price
currencyRates = CurrencyRates()
currencyCodes = CurrencyCodes()
client = scheduler_v1.CloudSchedulerClient.from_service_account_json("cookiebot_pubsub.json")
subscriber = pubsub_v1.SubscriberClient.from_service_account_json("cookiebot_pubsub.json")
project_id = "cookiebot-309512"
project_path = f"projects/{project_id}"
parent = f"{project_path}/locations/southamerica-east1"
topic_name = 'projects/cookiebot-309512/topics/cookiebot-publisher-topic'
subscription_path = None

def ConvertCurrency(snippet, to_currency):
    parsed = Price.fromstring(snippet)
    if parsed.amount is None or parsed.currency is None:
        return None
    if parsed.currency == '$':
        from_currency = 'USD'
    elif parsed.currency == '€':
        from_currency = 'EUR'
    elif parsed.currency == '£':
        from_currency = 'GBP'
    elif parsed.currency == 'R$':
        from_currency = 'BRL'
    else:
        from_currency = currencyCodes.get_currency_code(parsed.currency)
    rate = currencyRates.get_rate(from_currency, to_currency)    
    converted = round(parsed.amount_float * rate, 2)
    return f"{to_currency} {converted}"

def AskPublisher(cookiebot, msg, chat_id, language):
    if language == "pt":
        answer = "Divulgar postagem?"
    else:
        answer = "Share post?"
    Send(cookiebot, chat_id, answer, msg_to_reply=msg, 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data=f"SendToApprovalPub {chat_id} {msg['message_id']}")],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))

def AskApproval(cookiebot, query_data, from_id, isBombot=False):
    origin_chatid = query_data.split()[1]
    origin_messageid = query_data.split()[2]
    origin_userid = from_id
    Forward(cookiebot, mekhyID, origin_chatid, origin_messageid, isBombot=isBombot)
    Send(cookiebot, mekhyID, 'Approve post?', 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️ 10 days",callback_data=f'ApprovePub {origin_chatid} {origin_messageid} {origin_userid} 10')],
            [InlineKeyboardButton(text="✔️ 3 days",callback_data=f'ApprovePub {origin_chatid} {origin_messageid} {origin_userid} 3')],
            [InlineKeyboardButton(text="✔️ 1 day",callback_data=f'ApprovePub {origin_chatid} {origin_messageid} {origin_userid} 1')],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))

def create_job(job_name, job_description, job_data, job_schedule):
    job = {
        'name': client.job_path(project_id, 'southamerica-east1', job_name),
        'description': job_description,
        'pubsub_target': {
            'topic_name': topic_name,
            'data': bytes(job_data,'utf-8'),
        },
        'schedule': job_schedule,
    }
    response = client.create_job(parent=parent, job=job)
    print(f'Created job: {response.name}')
    return response

def list_jobs():
    response = client.list_jobs(parent=parent)
    jobs = []
    for job in response:
        jobs.append(job)
    return jobs

def delete_job(job_name):
    try:
        response = client.delete_job(name=client.job_path(project_id, 'southamerica-east1', job_name))
    except:
        response = client.delete_job(name=job_name)
    print(f'Deleted job: {response}')
    return response

def edit_job_data(job_name, job_data):
    job = {
        'name': client.job_path(project_id, 'southamerica-east1', job_name),
        'pubsub_target': {
            'topic_name': topic_name,
            'data': bytes(job_data,'utf-8'),
        },
    }
    response = client.update_job(job=job, update_mask={'paths': ['pubsub_target']})
    print(f'Updated job: {response.name}')
    return response

def SchedulePost(cookiebot, query_data):
    origin_chatid = query_data.split()[1]
    origin_messageid = query_data.split()[2]
    origin_userid = query_data.split()[3]
    days = query_data.split()[4]
    origin_chattitle = cookiebot.getChat(origin_chatid)['title']
    jobs = list_jobs()
    for job in jobs:
        if job.name.startswith(f"{parent}/jobs/{origin_chatid}"):
            delete_job(job.name)
    answer = f"Post set for the following times ({days} days):\n"
    language_origin = GetConfig(origin_chatid)[7]
    for group in GetRequestBackend('registers'):
        group_id = group['id']
        FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts = GetConfig(group_id)
        if publisherpost and language_origin == language:
            num_posts_for_group = 0
            for job in jobs:
                if f"--> {group_id}" in job.description:
                    num_posts_for_group += 1
            try:
                if maxPosts is None or num_posts_for_group < maxPosts:
                    hour = random.randint(0,23)
                    minute = random.randint(0,59)
                    target_chattitle = cookiebot.getChat(group_id)['title']
                    create_job(origin_chatid+group_id, 
                    f"{origin_chattitle} --> {target_chattitle}, at {hour}:{minute} ", 
                    f"{days} {origin_chatid} {group_id} {origin_messageid}", 
                    f"{minute} {hour} * * *")
                    answer += f"{hour}:{minute} - {target_chattitle}\n"
            except Exception as e:
                print(e)
    try:
        Send(cookiebot, origin_userid, answer)
        Send(cookiebot, origin_chatid, "Post adicionado à fila de publicação!")
    except Exception as e:
        Send(cookiebot, mekhyID, traceback.format_exc())
        Send(cookiebot, origin_chatid, "Post adicionado à fila de publicação, mas não consegui te mandar os horários. Mande /start no meu PV para eu poder te mandar mensagens.")

def SchedulerPull(cookiebot, isBombot=False):
    response = subscriber.pull(subscription=subscription_path, max_messages=100, return_immediately=True)
    received_messages = response.received_messages
    for message in received_messages:
        subscriber.acknowledge(subscription=subscription_path, ack_ids=[message.ack_id])
        print(message.message.data)
        data = message.message.data.decode('utf-8')
        remaining_times = int(data.split()[0]) - 1
        origin_chatid = data.split()[1]
        group_id = data.split()[2]
        origin_messageid = data.split()[3]
        if remaining_times <= 0:
            delete_job(origin_chatid+group_id)
        else:
            edit_job_data(origin_chatid+group_id, f"{remaining_times} {origin_chatid} {group_id} {origin_messageid}")
        try:
            target_chat = cookiebot.getChat(group_id)
            if 'is_forum' in target_chat and target_chat['is_forum']:
                #for thread_id in [472148, 566548, 603]:
                config = GetConfig(group_id)
                Forward(cookiebot, group_id, origin_chatid, origin_messageid, thread_id=int(config[10]), isBombot=isBombot)
            else:
                Forward(cookiebot, group_id, origin_chatid, origin_messageid, isBombot=isBombot)
        except TelegramError as e:
            delete_job(origin_chatid+group_id)
    return received_messages

def startPublisher(isBombot):
    global subscription_path
    if isBombot:
        subscription_path = subscriber.subscription_path(project_id, "bombot-subscription")
    else:
        subscription_path = subscriber.subscription_path(project_id, "cookiebot-subscription")