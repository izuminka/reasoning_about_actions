import json
from pathlib import Path

# pip install -q -U google-generativeai
import google.generativeai as genai
GEMINI_API_KEY = 'AIzaSyCGKrdLLppJg3aXB-uAsWaSSGXqfhLUpV8'
genai.configure(api_key=GEMINI_API_KEY)

# pip install openai
from openai import OpenAI
OPENAI_API_KEY = ''
client = OpenAI(api_key=OPENAI_API_KEY)


def read_data(file_path):
    '''
    Should return a list containing the prompts that are to be fed to the model.
    Parameters:
        file_path - String containing the location of the file
    '''
    with open(file_path, 'r') as f:
        data = [json.loads(jline) for jline in f.readlines()]
    return data
        

def write_data(data, idx, file_path):
    '''
    Function that stores the response of the prompt at given index.
    Parameters:
        data - String containing the response of the model
        idx - Index of the response
        file_path - String containing the location where the data is to be saved
    '''
    file_dir = '/'.join(file_path.split('/')[:-1])
    Path(file_dir).mkdir(parents=True, exist_ok=True)
    with open(file_path, 'a+') as f:
        f.write(json.dumps({'response':data})+'\n')

def get_response(model_name, prompt):
    '''
    Returns the string containing the response of the model
    Parameters:
        model_name - String containing the name of the model
        prompt - String containing the prompt to be fed to the model
    '''
    if model_name == 'gemini-pro':
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        print(response.candidates)
        try:
            return response.text
        except:
            return response.text
    elif model_name == 'gpt4':
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    elif model_name == 'gpt3.5':
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content