from forex_python.converter import CurrencyCodes
from price_parser import Price
import requests, json
exchangerate_key = ''
currencyCodes = CurrencyCodes()
import googletrans
translator = googletrans.Translator()

raw_text = "Hi, This is a direct buy YCH\nTotal price 30$\n\n\n- I can draw any species- YCH is set for all genders- No clothes included- Penis state can be modified or removed\n\nhttps://www.furaffinity.net/view/50644740/?upload-successful\n\nIf you want to buy, please request the slot you'll like in the place for the slot down in the comments\n\nCommissions are arranged over NOTES or preferably Telegram with my manager @Sagikb"
translated_text = translator.translate(raw_text, dest='pt').text

final_text = ''
for paragraph in translated_text.split('\n'):
    parsed = Price.fromstring(paragraph)
    code_target = 'BRL'
    if parsed.amount is None or parsed.currency is None:
        print('Invalid price')
        final_text += f"{paragraph}\n"
    else:
        if parsed.currency == '$':
            code_from = 'USD'
        elif parsed.currency == '€':
            code_from = 'EUR'
        elif parsed.currency == '£':
            code_from = 'GBP'
        elif parsed.currency == 'R$':
            code_from = 'BRL'
        else:
            code_from = currencyCodes.get_currency_code(parsed.currency)
        if code_from != code_target:
            print(f"Amount: {parsed.amount_float}\nOriginal currency: {parsed.currency}\nCode: {code_from}")
            rate = json.loads(requests.get(f"https://v6.exchangerate-api.com/v6/{exchangerate_key}/latest/{code_from}").text)['conversion_rates'][code_target]
            converted = round(parsed.amount_float * rate, 2)
            final_text += f"{paragraph} ({code_target} ≈{converted})\n"
        else:
            final_text += f"{paragraph}\n"

print(final_text)