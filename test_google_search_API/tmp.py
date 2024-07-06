import requests
import google.generativeai as genai
safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


def google_search(api_key, cse_id, query, num_results=10):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': num_results
    }
    response = requests.get(url, params=params)
    return response.json()

# Sample
api_key = 'AIzaSyDjvZHfMooBcO0sf-cm2j9gydH9mFrGuqE'
gemini_api_key = 'AIzaSyBt8nrTzyzWU3vThxqRaSRww7ktVxhCUAg'
cse_id = 'b0be1ab353ad04e22'
query = '台電回饋金採「登錄制」!  6/30前要登入，7/1就截止申請! 504元不拿白不拿！馬上就去辦。沒登錄，無法拿到獎勵，台電也不會感激咱們民眾！是每個月都有補貼呦~504x12個月=6048元呢~已查證屬實！https://tpcuip.taipower.com.tw/savepower/'
results = google_search(api_key, cse_id, query)
# print(results) # {}

genai.configure(api_key=gemini_api_key) #use bo-jyun's API key
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(
    contents=query,
    generation_config={'temperature': 0.0},
    safety_settings=safety_settings
)
print(response.text)




for i, item in enumerate(results['items']):
    print(f"{i+1}: {item['title']} - {item['link']}")
