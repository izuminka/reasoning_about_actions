import json
from pathlib import Path
from promping_stencils import *
import sys
sys.path.append('../../')
from questions_construction.domains import *

# pip install -q -U google-generativeai
import google.generativeai as genai
# GEMINI_API_KEY = 'AIzaSyCGKrdLLppJg3aXB-uAsWaSSGXqfhLUpV8'    # My Key (zero_shot)
# GEMINI_API_KEY = 'AIzaSyBAVf02zVYCgKxd-DTd9_PKEZMEbV4hons'    # Pavel's Key (few_shot_4)
# GEMINI_API_KEY = 'AIzaSyByew5dQG7MP2NYZgD_K4gc2qroI9s4y_8'    # Rajeev's Key (goldminer) -- Issues
# GEMINI_API_KEY = 'AIzaSyByew5dQG7MP2NYZgD_K4gc2qroI9s4y_8'    # Shri's Key (grippers)
GEMINI_API_KEY = 'AIzaSyA5ev80w-RFdIeD61Bq23SXomTUDni-S44'    # Aswin's Key (logistics)
# GEMINI_API_KEY = 'AIzaSyBx62LMT9y7mT2UJ_h2htLZQLEseUTtiRE'    # Nayem's Key (few_shot_4_cot)
# GEMINI_API_KEY = ''    # 's Key (mystery)
# GEMINI_API_KEY = 'AIzaSyDUhq_5iRBgB9ohEFw20R3mBqweTzt28zA'    # Nemika's Key (npuzzle)
# GEMINI_API_KEY = 'AIzaSyAEIrcO3WI-0CheJy8_ns_TISBmgMQqhy4'    # Amir's Key (satellite)
# GEMINI_API_KEY = 'AIzaSyD_FekLlCwlqo5SDy0xB1DbzxI5Iz8YHyw'    # Mihir's Key (depots)
# GEMINI_API_KEY = ''    # 's Key (spanner)
# GEMINI_API_KEY = ''    # 's Key (visitall)
# GEMINI_API_KEY = ''    # 's Key (zenotravel)
genai.configure(api_key=GEMINI_API_KEY)

# pip install openai
from openai import OpenAI
OPENAI_API_KEY = ''
client = OpenAI(api_key=OPENAI_API_KEY)

LLAMA_SYSTEM_PROMPT = '''You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.'''

def get_prompt(domain_name, instance, json_ele, prompt_tech, examples=1):
    '''
    Returns the final prompt for the instance.
    Parameters:
        domain_name - String representing the name of the domain
        instance - String containing the instance that the prompt belongs to
        json_ele - Dictionary containing all the information
        prompt_tech - String containing the prompting technique (cot, few_shot, self_consistency, zero_shot)
        examples - Integer containing the number of examples for few-shot prompting (Default=1, Max=9)
    '''
    if domain_name == 'blocksworld':
        domain_class = Blocksworld()
    elif domain_name == 'depots':
        domain_class = Depots()
    elif domain_name == 'driverlog':
        domain_class = Driverlog()
    elif domain_name == 'goldminer':
        domain_class = Goldminer()
    elif domain_name == 'grippers':
        domain_class = Grippers()
    elif domain_name == 'logistics':
        domain_class = Logistics()
    elif domain_name == 'miconic':
        domain_class = Miconic()
    elif domain_name == 'mystery':
        domain_class = Mystery()
    elif domain_name == 'npuzzle':
        domain_class = Npuzzle()
    elif domain_name == 'satellite':
        domain_class = Satellite()
    elif domain_name == 'spanner':
        domain_class = Spanner()
    elif domain_name == 'zenotravel':
        domain_class = Zenotravel()
    elif domain_name == 'visitall':
        domain_class = Visitall()
    else:
        raise Exception(f'{domain_name} is an invalid domain')
    prompt_obj = Generate_prompting_template('../../../data/questions/', domain_class, int(instance.split('_')[1].split('.')[0]), domain_name+'/', json_ele)

    if prompt_tech == 'zero_shot':
        return prompt_obj.zero_shot_prompt()
    elif prompt_tech == 'few_shot':
        return prompt_obj.few_shot_prompt(examples, cot_key=False)
    elif prompt_tech == 'few_shot_cot':
        return prompt_obj.few_shot_prompt(examples, cot_key=True)
    else:
        raise Exception(f'{prompt_tech} is an invalid prompting technique')

def write_data(data, file_path):
    '''
    Function that stores the response of the prompt at given index.
    Parameters:
        data - String containing the response of the model
        file_path - String containing the location where the data is to be saved
    '''
    file_dir = '/'.join(file_path.split('/')[:-1])
    Path(file_dir).mkdir(parents=True, exist_ok=True)
    with open(file_path, 'a+') as f:
        f.write(json.dumps(data)+'\n')

def get_response(model_name, prompt, pipeline_obj=None):
    '''
    Returns the string containing the response of the model
    Parameters:
        model_name - String containing the name of the model
        prompt - String containing the prompt to be fed to the model
        pipeline_obj - pipeline object from transformers
    '''
    if model_name == 'gemini-pro':
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        try:
            return response.text
        except:
            return "RECITATION"
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
    elif model_name == 'llama':
        return pipeline_obj(f"<s>[INST] <<SYS>>\n{LLAMA_SYSTEM_PROMPT}\n<</SYS>>\n\n{prompt} [/INST]")[0]['generated_text'].split('[/INST]')[1].strip()
    elif model_name == 'mistral':
        output = pipeline_obj(prompt, do_sample=False)
        start_index = output[0]['generated_text'].find('[ANSWER]:\n')
        return output[0]['generated_text'][start_index:]
    else:
        raise Exception(f'{model_name} is an invalid model')