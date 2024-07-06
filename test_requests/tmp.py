import json
import requests

user_input = input()
url1 = f'https://www.googleapis.com/customsearch/v1?cx=339feef75a8d2425c&key=AIzaSyCZP6s7zMt6Srq00v4a6EsZnTgvPGRv004&q={user_input}'

response = requests.get(url1)
if response.status_code == 200:
    with open('downloaded_file.json', 'wb') as file:
        file.write(response.content)
    print("JSON檔案已成功下載。")
else:
    print(f"下載失敗，狀態碼：{response.status_code}")

file_path = 'downloaded_file.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

'''
for query in data['items']:
    print(query['link'])
'''

url2 = data['items'][0]['link']
response = requests.get(url2)
if response.status_code == 200:
    content = response.text
    with open('output.html', 'w', encoding='utf-8') as file:
        file.write(content)
    print(content)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
