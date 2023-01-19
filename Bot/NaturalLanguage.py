from universal_funcs import *
from chatterbot import ChatBot
from chatterbot import comparisons
from chatterbot import response_selection

AI_ptbr = ChatBot(
    'Cookiebot_AI',  
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'statement_comparison_function': comparisons.LevenshteinDistance,
            'response_selection_method': response_selection.get_most_frequent_response
        }
    ],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'
    ],
    database_uri='sqlite:///../AI/AI_ptbr.db',
    read_only=True
)


def InteligenciaArtificial(cookiebot, msg, chat_id, language, sfw):
    SendChatAction(cookiebot, chat_id, 'typing')
    message = ""
    AnswerFinal = ""
    if "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']:
        message = msg['text'].replace("Cookiebot", '').replace("cookiebot", '').replace("@CookieMWbot", '').replace("COOKIEBOT", '').replace("CookieBot", '').replace("\n", '').capitalize()
    else:
        message = msg['text'].replace("\n", '').capitalize()
    if len(message) == 0:
        AnswerFinal = "?"
    else:
        if sfw == "True":
            if language == "pt":
                AnswerFinal = AI_ptbr.get_response(message).text.capitalize()
            else:
                AnswerFinal = "Sorry, my SFW AI is currently only available in Portuguese."
        else:
            if language == "eng":
                r = requests.post('https://api.simsimi.vn/v2/simtalk', data={'text': message, 'lc': 'en'})
            else:    
                r = requests.post('https://api.simsimi.vn/v2/simtalk', data={'text': message, 'lc': language})
            if 'message' in r.json() and len(r.json()['message']) > 0:
                AnswerFinal = r.json()['message'].capitalize()
            else:
                AnswerFinal = "Sorry, I don't understand."
    return AnswerFinal
