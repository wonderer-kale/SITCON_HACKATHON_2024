import argparse
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

if __name__ == "__main__":
    argparse = argparse.ArgumentParser()
    argparse.add_argument("--model", type=str, help="Model name")
    argparse.add_argument("--input_text", type=str, help="Input text File path")
    argparse.add_argument("--input_image", type=str, help="Input image File path")
    args = argparse.parse_args()
    if args.input_text:
        print(content_call(args.model, args.input_text))
    elif args.input_image:
        print(image_call(args.model, args.input_image))
    else:
        raise ValueError("Please provide either input text or input image path")