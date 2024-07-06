import google.generativeai as genai
gemini_api_key = 'AIzaSyBt8nrTzyzWU3vThxqRaSRww7ktVxhCUAg'
genai.configure(api_key=gemini_api_key) #use bo-jyun's API key
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
    response = model.generate_content(
        contents=query,
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

def faithfulness_check(mname:str, message:str, article:str):
    model = genai.GenerativeModel(mname)
    PROMPT = """Here are the message and the article:
    Faithful if the message is faithful to the article.
    Neural if the message and article is not related.
    Contradict if the message contradicts the article.
    Fact check the following message by the article and reply "Faithful", "Neural" or "Contradict" only.
    """
    response = model.generate_content(
        contents=f"{PROMPT}\nMessage: {message}\nArticle: {article}", 
        generation_config={'temperature': 0.0}, 
        safety_settings=safety_settings)
    return response.text # Faithfulness, Neural, Contradict

def save_txt_file(output:str, path:str):
    with open(path, 'w') as f:
        f.write(output)