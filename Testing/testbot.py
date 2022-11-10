import telepot
token = ''
mekhyID = 780875868

bot = telepot.Bot(token)

def changecmds(bot):
    bot.setMyCommands(commands=[{'command': 'idk', 'description': 'description'}], scope={"type": "chat", 'chat_id': mekhyID})

changecmds(bot)