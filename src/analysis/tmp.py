import sys, os
sys.path.append(os.path.realpath('__file__'))
sys.path.append(os.path.dirname(os.path.realpath('__file__')))
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('__file__'))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath('__file__')))))

from src.common import *

domain_name = DOMAIN_NAMES[0]
i = 1
instance_name = f'Instance_{i}'
questions = open_jsonl(QUESTIONS_PATH + f'/{domain_name}/{instance_name}.jsonl')

qa_dict = {}

for qa_object in questions:
    qa_dict[(qa_object['question_category'], qa_object['question_name'])] = qa_object

for key, qa_object in qa_dict.items():
    print('--------------------------',key, '--------------------------')
    print(qa_object['question'])
    print('\n')
    print(qa_object['answer'])
    print('\n')