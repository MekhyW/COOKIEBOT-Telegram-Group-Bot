from price_parser import Price
import requests, json
exchangerate_key = ''
import googletrans
translator = googletrans.Translator()

raw_text = "♡ Gift I made for my boyfriend a while ago ♡\n\n➵ Funko commissions for only 70$ + shipping 🇺🇸 (R$90 para BRs)\n\n• Channels for More \n@raposastudios\n• DM to claim: \n@IsaFoxy ✩"
translated_text = translator.translate(raw_text, dest='pt').text

def ConvertPricesinText(text, code_target):
    if (code_target == 'BRL') and any([x in text for x in ('R$', 'BRL', 'Reais', 'reais')]):
        return text
    final_text = ''
    text = text.replace('Reais', 'R$').replace('reais', 'R$')
    for paragraph in text.split('\n'):
        parsed = Price.fromstring(paragraph)
        if parsed.amount is None or parsed.currency is None:
            final_text += f"{paragraph}\n"
            continue
        if parsed.currency in ('$', 'US$', 'USD', 'U$'):
            code_from = 'USD'
        elif parsed.currency in ('€', 'EUR'):
            code_from = 'EUR'
        elif parsed.currency in ('£', 'GBP'):
            code_from = 'GBP'
        elif parsed.currency in ('R$', 'BRL'):
            code_from = 'BRL'
        elif parsed.currency in ('¥', 'JPY'):
            code_from = 'JPY'
        elif parsed.currency in ('C$', 'CAD'):
            code_from = 'CAD'
        elif parsed.currency in ('A$', 'AUD'):
            code_from = 'AUD'
        elif parsed.currency in ('ARS'):
            code_from = 'ARS'
        else:
            code_from = parsed.currency
        if code_from == code_target:
            return text
        try:
            rate_url = f"https://v6.exchangerate-api.com/v6/{exchangerate_key}/latest/{code_from}"
            rate = json.loads(requests.get(rate_url).text)['conversion_rates'][code_target]
            converted = round(parsed.amount_float * rate, 2)
            final_text += f"{paragraph} ({code_target} ≈{converted})\n"
        except Exception as e:
            print(e)
            final_text += f"{paragraph}\n"
    return final_text

final_text = ConvertPricesinText(translated_text, 'BRL')

print(final_text)