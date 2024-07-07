import logging
import os
import re
import sys
if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv

    load_dotenv()


from fastapi import FastAPI, HTTPException, Request
from datetime import datetime
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

import uvicorn
import requests

logging.basicConfig(level=os.getenv('LOG', 'WARNING'))
logger = logging.getLogger(__file__)

app = FastAPI()

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

configuration = Configuration(
    access_token=channel_access_token
)

async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)


import google.generativeai as genai
from firebase import firebase
# from utils import check_image_quake, check_location_in_message, get_current_weather, get_weather_data, simplify_data


firebase_url = os.getenv('FIREBASE_URL')
gemini_key = os.getenv('GEMINI_API_KEY')

# Initialize the Gemini Pro API
genai.configure(api_key=gemini_key)

#######################

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

def content_call(mname:str, query:str):
    model = genai.GenerativeModel(mname)
    prompt = "Fact check the message. If it is a recent event and you can't check the fact, you should obey the truthfulness of the message to reply. Reply in traditional Chinese."
    response = model.generate_content(
        contents=f"{query}\n{prompt}",
        generation_config={'temperature': 0.0},
        safety_settings=safety_settings
    )
    return response.text

def image_call(mname:str, img_path:str):
    model = genai.GenerativeModel(mname)
    file = genai.upload_file(path=img_path, display_name='image')
    response = model.generate_content(
        [file, "Do the Fact check on the image and reply in traditional chinese."],
        generation_config={'temperature': 0.0},
        safety_settings=safety_settings
    )
    return response.text

def extract_image_text(mname:str, img_path:str):
    model =genai.GenerativeModel(mname)
    file = genai.upload_file(path=img_path, display_name='image')
    response = model.generate_content(
        [file, "Extract the text from the image and reply in traditional chinese."],
        generation_config={'temperature': 0.0},
        safety_settings=safety_settings
    )
    return response.text

def summarize_html(mname:str, query:str):
    model = genai.GenerativeModel(mname)
    response = model.generate_content(
        contents=f"Given a HTML files, summarize the news article and reply in traditional chinese.\nHTML files: {query}",
        generation_config={'temperature': 0.0},
        safety_settings=safety_settings
    )
    return response.text #str

def relavance_check(mname:str, message:str, article:str):
    model = genai.GenerativeModel(mname)
    PROMPT = """Here are the message and the article:
    Yes means the message is related to the article.
    No means the message is not related to the article.
    Print the Yes or No only.
    """
    response = model.generate_content(
        contents=f"{PROMPT}\nMessage: {message}\nArticle: {article}", 
        generation_config={'temperature': 0.0}, 
        safety_settings=safety_settings)
    return response.text # Faithfulness, Neural, Contradict

def save_txt_file(output:str, path:str):
    with open(path, 'w') as f:
        f.write(output)

#######################



@app.get("/health")
async def health():
    return 'ok'


@app.post("/webhooks/line")
async def handle_callback(request: Request):
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        logging.info(event)
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue
        text = event.message.text
        user_id = event.source.user_id

        msg_type = event.message.type
        fdb = firebase.FirebaseApplication(firebase_url, None)
        if event.source.type == 'group':
            user_chat_path = f'chat/{event.source.group_id}'
        else:
            user_chat_path = f'chat/{user_id}'
            chat_state_path = f'state/{user_id}'
        chatgpt = fdb.get(user_chat_path, None)

        if msg_type == 'text':

            if chatgpt is None:
                messages = []
            else:
                messages = chatgpt

            cx = '339feef75a8d2425c'
            key = 'AIzaSyAtcaJBfsyntOQvBtndhQufp3CVxkKQDXE'
            URL = f'https://www.googleapis.com/customsearch/v1?cx={cx}&key={key}&q={text}'
            response = requests.get(URL)

            if response.status_code == 200:
                data = response.json()
                print('success')
            else:
                print('fail')

            find = False

            for i in range(1):
                URL = data['items'][i]['link']
                response = requests.get(URL)

                # LLM summarize
                # llm_summarize = summarize_html(mname='gemini-1.5-flash', query=response.text)
                title = data['items'][i]['pagemap']['metatags'][0]['og:title']
                description = data['items'][i]['pagemap']['metatags'][0]['og:description']
                llm_summarize = title + '\n' + description

                # Compare
                relevance = relavance_check(mname='gemini-1.5-flash', message=text, article=llm_summarize)
                #print(relevance)
                relevance = relevance.strip()
                if relevance == "Yes":
                    reply_msg = llm_summarize
                    find = True
                    break
                # else: continue

            if find == False:
                reply_msg = content_call(mname='gemini-1.5-flash', query=text)

            # bot_condition = {
            #     "清空": 'A',
            #     "摘要": 'B',
            #     "地震": 'C',
            #     "氣候": 'D',
            #     "其他": 'E'
            # }

            # model = genai.GenerativeModel('gemini-1.5-pro')
            # response = model.generate_content(
            #     f'請判斷 {text} 裡面的文字屬於 {bot_condition} 裡面的哪一項？符合條件請回傳對應的英文文字就好，不要有其他的文字與字元。')
            # print('='*10)
            # text_condition = re.sub(r'[^A-Za-z]', '', response.text)
            # print(text_condition)
            # print('='*10)
            # if text_condition == 'A':
            #     fdb.delete(user_chat_path, None)
            #     reply_msg = '已清空對話紀錄'
            # elif text_condition == 'B':
            #     model = genai.GenerativeModel('gemini-pro')
            #     response = model.generate_content(
            #         f'Summary the following message in Traditional Chinese by less 5 list points. \n{messages}')
            #     reply_msg = response.text
            # elif text_condition == 'C':
            #     print('='*10)
            #     print("地震相關訊息")
            #     print('='*10)
            #     model = genai.GenerativeModel('gemini-pro-vision')
            #     OPEN_API_KEY = os.getenv('OPEN_API_KEY')
            #     earth_res = requests.get(f'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/E-A0015-003?Authorization={OPEN_API_KEY}&downloadType=WEB&format=JSON')
            #     url = earth_res.json()["cwaopendata"]["Dataset"]["Resource"]["ProductURL"]
            #     reply_msg = check_image_quake(url)+f'\n\n{url}'
            # elif text_condition == 'D':
            #     location_text = '台北市'
            #     location = check_location_in_message(location_text)
            #     print('Location is: ' + location)
            #     weather_data = get_weather_data(location)
            #     simplified_data = simplify_data(weather_data)
            #     current_weather = get_current_weather(simplified_data)

            #     print('The Data is: ' + str(current_weather))

            #     now = datetime.now()
            #     formatted_time = now.strftime("%Y/%m/%d %H:%M:%S")

            #     if current_weather is not None:
            #         total_info = f'位置: {location}\n氣候: {current_weather["Wx"]}\n降雨機率: {current_weather["PoP"]}\n體感: {current_weather["CI"]}\n現在時間: {formatted_time}'

            #     response = model.generate_content(
            #         f'你現在身處在台灣，相關資訊 {total_info}，我朋友說了「{text}」，請問是否有誇張、假裝的嫌疑？ 回答是或否。')
            #     reply_msg = response.text
            # else:

            #     # model = genai.GenerativeModel('gemini-pro')
            #     messages.append({'role': 'user', 'parts': [text]})
            #     response = model.generate_content(messages)
            #     messages.append({'role': 'model', 'parts': [text]})
            #     # 更新firebase中的對話紀錄
            #     fdb.put_async(user_chat_path, None, messages)
            #     reply_msg = response.text

            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_msg)]
                ))

    return 'OK'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', default=8080))
    debug = True if os.environ.get(
        'API_ENV', default='develop') == 'develop' else False
    logging.info('Application will start...')
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)