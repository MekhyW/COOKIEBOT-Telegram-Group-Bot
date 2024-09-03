import json
import requests
from price_parser import Price
EXCHANGERATE_KEY = ''

RAW_TEXT = "Stickers - pack com 5 R$ 25,00"

def convert_prices_in_text(text, code_target):
    if (code_target == 'BRL') and any([x in text for x in ('R$', 'BRL', 'Reais', 'reais')]):
        return text
    final_text = ''
    text = text.replace('Reais', 'R$').replace('reais', 'R$')
    for paragraph in text.split('\n'):
        amount = 0
        currency = None
        for word in paragraph.split():
            parsed = Price.fromstring(word, currency_hint='usd')
            if parsed.amount is not None and parsed.amount_float > amount:
                amount = parsed.amount_float
            if parsed.currency is not None:
                currency = parsed.currency
        if amount == 0 or currency is None:
            final_text += f"{paragraph}\n"
            continue
        if currency in ('$', 'US$', 'USD', 'U$'):
            code_from = 'USD'
        elif currency in ('€', 'EUR'):
            code_from = 'EUR'
        elif currency in ('£', 'GBP'):
            code_from = 'GBP'
        elif currency in ('R$', 'BRL'):
            code_from = 'BRL'
        elif currency in ('¥', 'JPY'):
            code_from = 'JPY'
        elif currency in ('C$', 'CAD'):
            code_from = 'CAD'
        elif currency in ('A$', 'AUD'):
            code_from = 'AUD'
        elif currency in ('ARS'):
            code_from = 'ARS'
        else:
            code_from = currency
        if code_from == code_target:
            return text
        try:
            rate_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_KEY}/latest/{code_from}"
            rate = json.loads(requests.get(rate_url, timeout=10).text)['conversion_rates'][code_target]
            converted = round(amount * rate, 2)
            final_text += f"{paragraph} ({code_target} ≈{converted})\n"
        except Exception as e:
            print(e)
            final_text += f"{paragraph}\n"
    return final_text

print(convert_prices_in_text(RAW_TEXT, 'USD'))
