from google.cloud import translate_v2
import re
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'cookiebot-bucket-key.json'
translate_client = translate_v2.Client()

def translate(text, dest='en'):
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    tags = {}
    count = 0
    def replace_tag(match):
        nonlocal count
        placeholder = f" htmltag{count} "
        tags[placeholder] = match.group(0)
        count += 1
        return placeholder
    newline_token = " NEWLINE_TOKEN_XYZ "
    text_with_placeholders = re.sub(r'<[^>]*>', replace_tag, text)
    text_with_tokens = text_with_placeholders.replace('\n', newline_token)
    translated = translate_client.translate(text_with_tokens, target_language=dest)["translatedText"]
    for placeholder, tag in tags.items():
        translated = re.sub(re.escape(placeholder.strip()), tag, translated, flags=re.IGNORECASE)
    translated = re.sub(re.escape(newline_token.strip()), '\n', translated, flags=re.IGNORECASE)
    translated = translated.replace('R $', 'R$')
    return translated

mytext = "❤️Fazerei 3 sketchs desse... Serão sorteados \n\n 🌸Para participar sigam as regras  \n\n 🌙Apenas pra inscritos  \n Compartilhar num grupo ou com amigo \n\n ✨Postar print + a oc  \n ⚡️Acaba amanhã"
translated = translate(mytext, dest='en')
print(translated)
