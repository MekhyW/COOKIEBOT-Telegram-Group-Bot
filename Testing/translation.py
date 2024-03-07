from deep_translator import GoogleTranslator

def translate(text, dest='en'):
    return GoogleTranslator(source='auto', target=dest).translate(text) 

translated = translate("Olá, como vai?", dest='es')
print(translated)