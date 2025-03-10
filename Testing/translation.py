from deep_translator import GoogleTranslator
import re

def translate(text, dest='en'):
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
    translated = GoogleTranslator(source='auto', target=dest).translate(text_with_tokens)
    for placeholder, tag in tags.items():
        translated = re.sub(re.escape(placeholder.strip()), tag, translated, flags=re.IGNORECASE)
    translated = re.sub(re.escape(newline_token.strip()), '\n', translated, flags=re.IGNORECASE)
    translated = translated.replace('R $', 'R$')
    return translated

translated = translate("❕ Vendo base de fursuit! ❕\n\n R$80 + FRETE 💵\n Se for de SP posso entregar em mãos (posso entregar gratuitamente no furboliche)\n\nInteressados chamar @aspenfoxy 📣", dest='en')
print(translated)
