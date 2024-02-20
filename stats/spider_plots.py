#pip install -U plotly kaleido
import json
import math
import matplotlib.pyplot as plt
import glob
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PLAN_LENGTHS = [1, 5, 10, 15, 19]
DATA_PATHS = ['free_answer.jsonl', 'true_false_answer.jsonl']

LINE_WIDTH = 5
FONT_SIZE = 30

def extract_data(data, model, category):
    scores = []
    for ele in data:
        if ele['model'] == model and ele['question_category'] == category and ele['result'] and not math.isnan(ele['result']):
            scores.append(ele['result'])
    return sum(scores)/len(scores)

def plot(data, plan_length, data_path):
    categories = set()
    models = set()
    for ele in data:
        categories.add(ele['question_category'])
        models.add(ele['model'])
    
    categories = list(categories)
    categories_list = categories * len(models)
    
    models = list(models)
    model_list = []
    for ele in models:
        for _ in range(len(categories)):
            model_list.append(ele)
    
    score = []
    for model in models:
        for category in categories:
            score.append(extract_data(data, model, category))

    df_score = pd.DataFrame({
        'model' : model_list,
        'category' : categories_list,
        'score' : score
    })

    fig = px.line_polar(df_score, r='score', theta='category', line_close=True, 
                        category_orders={"category": categories_list}, color='model',
                        markers=True, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(line=dict(width=LINE_WIDTH))
    fig.update_traces(marker=dict(size=15))

    fig.update_layout(
        legend_font=dict(
            size=FONT_SIZE,              # Specify the font size
            color="black"                # Specify the font color
        ),
        polar=dict(
            # radialaxis=dict(tickfont=dict(size=FONT_SIZE)),  # Change 12 to your desired size
            radialaxis=dict(
                tickmode='array',
                tickvals=[0, 1], # Define the tick values you want to display
                tickfont=dict(size=FONT_SIZE)
            ),
            angularaxis=dict(tickfont=dict(size=FONT_SIZE))   # Change 12 to your desired size
        ),
        legend_title_text=None,
    )
    fig.update_layout(height=600, width=2000) # You can change these values as needed
    fig.write_image(f"{data_path.split('.')[0]}_{plan_length}.pdf")

if __name__ == '__main__':
    for plan_length in PLAN_LENGTHS:
        for data_path in DATA_PATHS:
            print(f'Plotting for {data_path} with plan length {plan_length}')
            with open(data_path, 'r') as f:
                data = [json.loads(ele) for ele in f.readlines()]
            data = [ele for ele in data if ele['plan_length']==plan_length]
            plot(data, plan_length, data_path)