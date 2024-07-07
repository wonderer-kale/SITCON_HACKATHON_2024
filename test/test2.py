import json
import requests

cx = '339feef75a8d2425c'
key = 'AIzaSyCClHSsoa0VReJOqZoG2fSjv_RPO0hnt1g'

def google_search(user_input):
    url1 = f'https://www.googleapis.com/customsearch/v1?cx={cx}&key={key}&q={user_input}' # Google 搜尋

    response = requests.get(url1)
    if response.status_code == 200:
        data = response.json() # 得到的 json 檔案
        print("JSON檔案已成功擷取。")
    else:
        print(f"擷取失敗，狀態碼：{response.status_code}")
    if 'items' not in data.keys():
        return None, None, None
    url2 = data['items'][0]['link'] # Google 搜尋結果的第一個連結
    title = data['items'][0]['title']
    if 'og:description' in data['items'][0]['pagemap']['metatags'][0].keys():
        description = data['items'][0]['pagemap']['metatags'][0]['og:description']
    else:
        description = data['items'][0]['snippet']

    return url2, title, description
