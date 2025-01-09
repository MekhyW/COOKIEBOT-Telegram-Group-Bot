import spamwatch
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('spamwatch_token')
client = spamwatch.Client(TOKEN)

my_token = client.get_self()
stats = client.stats()
ban = client.get_ban(5360556225)
print(my_token)
print(stats)
if ban:
    print(ban.id)
    print(ban.reason)
else:
    print('Not banned')
