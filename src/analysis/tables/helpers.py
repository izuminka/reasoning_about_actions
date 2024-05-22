
TO_PRETTY = {
    'base_fluents': 'Base Fl',
    'persistent_fluents': 'Base Fl + Cnstr.',
    'derived_fluents': 'Derived Fl',
    'static_fluents': 'Static Fl',

    # 'action_executability': 'Action Ex.',
    # 'effects': 'Effects',
    # 'fluent_tracking': 'Fl. Trk.',
}

def prettify(text):
    for k,v in TO_PRETTY.items():
        string = string.replace(k, v)
    return text



def to_latex_table(df, caption_nl, label=''):
    latex_table = df.to_latex(index=True, formatters={"name": str.upper}, float_format="{:.2f}".format)
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
    return latex_table_all



# def save_table():
#     os.makedirs(os.path.join(save_main_dir, 'tables'), exist_ok=True)
#     with open(os.path.join(save_main_dir, 'tables', f'{save_key}.tex'), 'w') as f:
#         f.write(latex_table_all)