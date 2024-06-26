import sys
import json
sys.path.append('..')
from common import *
from analysis.model_performances import *

TO_PRETTY = {
    WITH_RAMIFICATIONS : 'W R',
    WITHOUT_RAMIFICATIONS : 'W/O R',

    'few_shot_1': 'FS-1',
    'few_shot_3': 'FS-3',
    'few_shot_5': 'FS-5',

    'gemma-2b': 'G-2b',
    'gemma-7b': 'G-7b',
    'llama2-7b-chat': 'L-7b',
    'llama2-13b-chat': 'L-13b',
    'gemini': 'Gemini',

    'base_fluents': 'Base Fl',
    'persistent_fluents': 'Base Fl + Cnstr.',
    'derived_fluents': 'Derived Fl',
    'static_fluents': 'Static Fl',

    'object_tracking': 'Object Trk.',
    'fluent_tracking': 'Fluent Trk.',
    'state_tracking': 'State Trk.',
    'action_executability': 'Action Exec.',
    'effects': 'Effects',
    'numerical_reasoning': 'Num. Reas.',
    'hallucination': 'Hallucination',
    'composite': 'Composite',
    ALL_QUESTION_CATEGORIES_KEY: 'AVG',
}

def prettify(text):
    for k,v in TO_PRETTY.items():
        string = string.replace(k, v)
    return text



def to_latex_table(df, caption_nl, label='', index=True):
    latex_table = df.to_latex(index=index, formatters={"name": str.upper}, float_format="{:.2f}".format)
    latex_table = latex_table.replace('\\$', '$').replace('\\{', '{').replace('\\}', '}').replace('\\_', '_')

    latex_table_all = r"""
\begin{table}[h!]
\begin{adjustbox}{width=\textwidth,center}
""" + latex_table + """
\end{adjustbox}
\caption{""" + caption_nl + """}
\label{table:""" + label + """}
\end{table}
"""
    return latex_table_all.replace('${None}_{None}$', '---')



# def save_table():
#     os.makedirs(os.path.join(save_main_dir, 'tables'), exist_ok=True)
#     with open(os.path.join(save_main_dir, 'tables', f'{save_key}.tex'), 'w') as f:
#         f.write(latex_table_all)