from deep_translator import GoogleTranslator
import re

def translate(text, dest='en'):
    tags = {}
    count = 0
    def replace_tag(match):
        nonlocal count
        placeholder = f"htmltag{count}"
        tags[placeholder] = match.group(0)
        count += 1
        return placeholder
    text_with_placeholders = re.sub(r'<[^>]*>', replace_tag, text)
    translated = GoogleTranslator(source='auto', target=dest).translate(text_with_placeholders)
    for placeholder, tag in tags.items():
        translated = re.sub(re.escape(placeholder), tag, translated, flags=re.IGNORECASE)
    return translated

translated = translate("Kickei o novo usuário por <b> suspeita de ser um robô </b>\n<blockquote> Se isso foi um erro, peça para ele adicionar um username (@) ou foto de perfil e um ADM adicioná-lo de volta </blockquote>", dest='es')
print(translated)
