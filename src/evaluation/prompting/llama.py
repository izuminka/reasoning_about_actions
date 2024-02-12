from transformers import pipeline
from helper import *

MODEL_NAME = 'meta-llama/Llama-2-7b-chat-hf'

if __name__ == '__main__':
    generate_text = pipeline('text-generation', model=MODEL_NAME, device_map='auto')
    get_response('llama', 'What is your name?', generate_text)