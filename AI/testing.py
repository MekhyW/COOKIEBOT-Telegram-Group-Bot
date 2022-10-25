from chatterbot import ChatBot
bot = ChatBot(
    'Cookiebot_AI',  
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'statement_comparison_function': 'chatterbot.comparisons.LevenshteinDistance',
        }
    ],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'
    ],
    database_uri='sqlite:///AI_ptbr.db',
    read_only=True
)

while True:
    try:
        bot_input = bot.get_response(input())
        print(bot_input.text.capitalize(), bot_input.confidence)
    except(KeyboardInterrupt, EOFError, SystemExit):
        break
