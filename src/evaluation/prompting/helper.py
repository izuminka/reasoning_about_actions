# pip install -q -U google-generativeai
import google.generativeai as genai
GEMINI_API_KEY = ''
genai.configure(api_key=GEMINI_API_KEY)


from openai import OpenAI
OPENAI_API_KEY = ''
client = OpenAI(api_key=OPENAI_API_KEY)


def read_data(file_path):
    '''
    Should return a list containing the prompts that are to be fed to the model.
    Parameters:
        file_path - String containing the location of the file
    '''
    pass

def write_data(data, idx):
    '''
    Function that stores the response of the prompt at given index.
    Parameters:
        data - String containing the response of the model
        idx - Index of the response
    '''
    pass

def get_response(model_name, prompt):
    '''
    Returns the string containing the response of the model
    Parameters:
        model_name - String containing the name of the model
        prompt - String containing the prompt to be fed to the model
    '''
    if model_name == 'gemini-pro':
        model = genai.GenerativeModel(model_name)
        return model.generate_content(prompt).text
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