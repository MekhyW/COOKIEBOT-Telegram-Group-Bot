import re
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
MY_STRING = 'MAS QUE BAITA NOTÍCIA, TCHÊ! 😱 FurSMeetinho 2023 chegou e vai estar cheio de revelações!! 🤯 \n5 HORAS DE MUITA DIVERSÃO GARANTIDA 🎉\n\n🎟️Valor do ingresso: R$25\n🎟️🎳Valor do ingresso + boliche pós evento: R$40\n👉 Compre aqui 👉 https://forms.gle/YrU1TxKaUmi3FUhv9\n\nNesse evento teremos a REVELAÇÃO AO VIVO DA DATA DO FurSMeet 2023 E VENDA DOS SEUS INGRESSOS!!! Os ingressos comprados pela gurizada no FurSMeetinho terão uma surpresa 😱 NÃO ACABA AI!!! Vamos ter 2 atividades surpresas pros piá do evento, conseguem adivinhar oq é?? 🎤📹\nVocês estão prontos pra tantas revelações??\n\nSe você leu até aqui,vou te dar de presente um SPOILERZÃO:\n⚠️ESSE FURSMEETINHO SERÁ REALIZADO NO HOTEL DO FURSMEET 2023⚠️\n\nDúvidas?? Mande uma mensagem para nós!\nTem interesse em ser Estande no FurSMeetinho 2023? Entre em contato conosco nas nossas redes sociais ou com @prisma_arco_iris no telegram ❤️\nNão conhece ninguém que vá?? Da uma bizoiada no nosso chat do telegram pra fazer amizades e não ficar perdido! 👉  https://t.me/fursmeetchat'
urls = re.findall(URL_REGEX, MY_STRING)
for url in urls:
    name = url[0]
    if name.endswith('/'):
        name = name[:-1]
    name = name.split('/')[-1].replace('www.', '')
    print(name, url)
