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

def extract_image_text(mname:str, img_path:str):
    model =genai.GenerativeModel(mname)
    file = genai.upload_file(path=img_path, display_name='image')
    response = model.generate_content(
        [file, "Extract the text from the image and reply in traditional chinese."],
        generation_config={'temperature': 0.0},
        safety_settings=safety_settings
    )
    return response.text

def save_txt_file(output:str, path:str):
    with open(path, 'w') as f:
        f.write(output)

if __name__ == "__main__":
    argparse = argparse.ArgumentParser()
    argparse.add_argument("--model", type=str, default='gemini-1.5-flash', help="Model name")
    argparse.add_argument("--file_path", type=str, help="File path")
    argparse.add_argument("--output_path", type=str, help="Output path")
    argparse.add_argument("--type", type=str, help="Type of using function")
    # content, image, extract
    args = argparse.parse_args()
    result = ""
    if(args.type == "content"):
        result = content_call(args.model, args.file_path)
    elif(args.type == "image"):
        result = image_call(args.model, args.file_path)
    elif(args.type == "extract"):
        result = extract_image_text(args.model, args.file_path)
    else:
        raise ValueError("Invalid type of function")