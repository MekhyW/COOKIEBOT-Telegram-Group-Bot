from price_parser import Price
import requests, json
exchangerate_key = ''
import googletrans
translator = googletrans.Translator()

raw_text = "🌈1600BRL + shipping 🌈"
translated_text = translator.translate(raw_text, dest='pt').text

def ConvertPricesinText(text, code_target):
    final_text = ''
    text = text.replace('Reais', 'R$').replace('reais', 'R$')
    for paragraph in text.split('\n'):
        parsed = Price.fromstring(paragraph)
        print(parsed.currency, parsed.amount)
        if parsed.amount is None or parsed.currency is None:
            final_text += f"{paragraph}\n"
        else:
            if parsed.currency in ('$', 'US$', 'USD', 'U$'):
                code_from = 'USD'
            elif parsed.currency in ('€', 'EUR'):
                code_from = 'EUR'
            elif parsed.currency in ('£', 'GBP'):
                code_from = 'GBP'
            elif parsed.currency in ('R$', 'BRL'):
                code_from = 'BRL'
            else:
                final_text += f"{paragraph}\n"
                continue
            if code_from != code_target or code_from != 'USD':
                try:
                    if code_from != 'USD':
                        rate = json.loads(requests.get(f"https://v6.exchangerate-api.com/v6/{exchangerate_key}/latest/{code_from}").text)['conversion_rates']['USD']
                        converted = round(parsed.amount_float * rate, 2)
                        final_text += f"{paragraph} (USD ≈{converted})\n"
                    else:
                        rate = json.loads(requests.get(f"https://v6.exchangerate-api.com/v6/{exchangerate_key}/latest/{code_from}").text)['conversion_rates'][code_target]
                        converted = round(parsed.amount_float * rate, 2)
                        final_text += f"{paragraph} ({code_target} ≈{converted})\n"
                except Exception as e:
                    print(e)
                    final_text += f"{paragraph}\n"
            else:
                final_text += f"{paragraph}\n"
    return final_text

final_text = ConvertPricesinText(translated_text, 'USD')

print(final_text)