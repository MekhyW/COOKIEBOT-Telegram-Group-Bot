from forex_python.converter import CurrencyRates
from forex_python.converter import CurrencyCodes
from price_parser import Price
currencyRates = CurrencyRates()
currencyCodes = CurrencyCodes()

parsed = Price.fromstring('$1.000,00')
code_target = 'BRL'
if parsed.amount is None or parsed.currency is None:
    print('Invalid price')
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
    print(f"Amount: {parsed.amount_float}\nOriginal currency: {parsed.currency}\nCode: {code_from}")
    rate = currencyRates.get_rate(code_from, code_target)    
    converted = round(parsed.amount_float * rate, 2)
    print(f"RESULT: {code_target} {converted}")