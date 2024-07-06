import json
import requests

cx = '339feef75a8d2425c'
key = 'AIzaSyCZP6s7zMt6Srq00v4a6EsZnTgvPGRv004'

def google_search(user_input):
    url1 = f'https://www.googleapis.com/customsearch/v1?cx={cx}&key={key}&q={user_input}' # Google 搜尋

    response = requests.get(url1)
    if response.status_code == 200:
        data = response.json() # 得到的 json 檔案
        print("JSON檔案已成功擷取。")
    else:
        print(f"擷取失敗，狀態碼：{response.status_code}")

    url2 = data['items'][0]['link'] # Google 搜尋結果的第一個連結
    response = requests.get(url2)
    if response.status_code == 200:
        content = response.text
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    return url2, content
