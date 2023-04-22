from universal_funcs import *
import openai
openai.api_key = openai_key
data_initial = json.load(open('static/AI_SFW.json'))
questions_list = [q_a['prompt'] for q_a in data_initial['questions_answers']]
answers_list = [q_a['completion'] for q_a in data_initial['questions_answers']]

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
        if sfw == True:
            prompt_beginning = "Você é um assistente útil, bobo e furry que adora zoar com os outros. Seu nome é CookieBot, e seu criador/pai se chama Mekhy. Responda as perguntas abaixo e você será recompensado com um biscoito!"
            messages=[{"role": "system", "content": prompt_beginning}]
            for i in range(len(questions_list)):
                messages.append({"role": "user", "content": questions_list[i]})
                messages.append({"role": "system", "content": answers_list[i], "name": "CookieBot"})
            messages.append({"role": "user", "content": message})
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0.9)
            AnswerFinal = completion.choices[0].message.content
            questions_list.pop(0)
            answers_list.pop(0)
            questions_list.append(message)
            answers_list.append(AnswerFinal)
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
