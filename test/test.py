import requests


text = '太可怕了！連知名大公司統一愛之味皆如此惡劣大量毒害群眾？可惡之極！好可怕的黑心商家！可能引發一些莫名的病毒🦠、及找不出的病源可能都與這些食物有關。台灣號稱洗腎亡國( 王國 )的由來！黑心錢利多最好賺！'
URL = f'https://www.googleapis.com/customsearch/v1?cx=339feef75a8d2425c&key=AIzaSyCZP6s7zMt6Srq00v4a6EsZnTgvPGRv004&q={text}'
response = requests.get(URL)
if response.status_code == 200:
    print('success')
    reply_msg = response.text
else:
    print('fail')
    reply_msg = 'fail'

print(reply_msg)