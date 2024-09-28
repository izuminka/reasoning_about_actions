import random
import concurrent.futures  # for multithreading
import multiprocessing  # for multiprocessing
import matplotlib.pyplot as plt
import numpy as np

from together_ai_common import *

DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo" #"meta-llama/Llama-3-70b-chat-hf"
OUTPUT_TOKEN_LIMIT = 5000

# de74b851-4128-4925-822f-ae293ebfea33
# 87a6d1f0-41ec-41d7-8a7e-7eb16bbdf667
# b4b774e9-b795-48bd-a666-433cca536dee
def eval_free_answers_prompt(llm_response, true_response):
    return f"""Evaluate whether the LLM response and the ground truth response are semantically the same. Examine the responses, 
provide reasoning for your evaluation, and then Write "True" if the responses are the same or "False" if they are different.

Example 1:

[LLM Response]
Location f1_4f is connected to f1_3f, f0_4f, and f2_4f.

[Ground Truth]
location f1_4f and location f0_4f are connected, location f1_4f and location f2_4f are connected, 
location f0_4f and location f1_4f are connected, location f1_3f and location f1_4f are connected, 
there is a connection between location f2_4f and location f1_4f, there is a connection between location f1_4f and location f1_3f

[Reasoning for the evaluation]
all of the connections are the same

[Answer]
True

Example 2:

[LLM Response]
loc_x0_y3 is visited, loc_x0_y4 is visited, loc_x1_y3 is visited, 
loc_x1_y4 is visited, loc_x2_y4 is visited, loc_x3_y4 is visited, 
loc_x3_y3 is visited, loc_x2_y3 is visited, loc_x2_y2 is visited, 
loc_x2_y1 is visited, loc_x1_y1 is visited, loc_x0_y1 is visited, 
loc_x0_y0 is visited

[Ground Truth]
loc_x0_y0 is visited, loc_x0_y1 is marked as visited, loc_x0_y3 is visited, loc_x0_y4 is visited, 
loc_x1_y0 is not visited, loc_x1_y1 is visited, loc_x1_y3 is marked as visited, loc_x1_y4 is marked as visited, 
loc_x2_y0 is not visited, loc_x2_y1 is visited, loc_x2_y2 is visited, loc_x2_y3 is marked as visited, 
loc_x2_y4 is marked as visited, loc_x3_y0 is not marked as visited, loc_x3_y1 is not visited, loc_x3_y2 is not visited, 
loc_x3_y3 is visited, loc_x3_y4 is marked as visited, loc_x4_y0 is not visited, 
loc_x4_y1 is not visited and loc_x4_y2 is not visited

[Reasoning for the evaluation]
Lots of inconsistencies including: loc_x1_y0 is not visited, loc_x2_y0 is not visited, loc_x4_y0 is not visited but missing from the LLM response

[Answer]
False

Example 3:

[LLM Response]
airport l0_0 is located in city c0, airport l0_1 is located in city c0, 
airport l0_2 is in city c0, airport l1_0 is in city c1, airport l1_1 is in city c1, 
airport l1_2 is in city c1, airport l2_0 is in city c2, airport l2_1 is in city c2, 
airport l2_2 is in city c2, object t1 is located at airport l1_0, object a0 is located at airport l2_0, 
object a1 is located at airport l2_0, object p0 is located at airport l0_2, object p1 is located at airport l1_2, 
object p2 is located at airport l1_2, object p3 is located at airport l2_0, object t0 is located at airport l0_2, 
object t2 is located at airport l2_0, package p0 is not present in vehicle t0, package p0 is not present in vehicle t1, 
package p0 is not present in vehicle t2, package p0 is not present in vehicle a1, package p1 is not present in vehicle t0, 
package p1 is not present in vehicle t1, package p1 is not present in vehicle t2, package p1 is not present in vehicle a1, 
package p2 is not present in vehicle t0, package p2 is not present in vehicle t1, package p2 is not present in vehicle t2, 
package p2 is not present in vehicle a1, package p3 is not present in vehicle t0, package p3 is not present in vehicle t1, 
package p3 is present in vehicle t2, package p3 is not present in vehicle a1

[Ground Truth]
airport l0_1 is located in city c0, airport l0_2 is in city c0, airport l1_0 is in city c1, airport l1_2 is located in city c1, 
airport l2_1 is located in city c2, airport l2_2 is located in city c2, at airport l0_2, object p0 is located, at airport l1_2, 
object p1 is located, at airport l2_0, object a0 is located, at airport l2_0, object a1 is located, city c0 contains airport l0_0, 
city c1 contains airport l1_1, city c2 contains airport l2_0, object p2 is at airport l1_2, object t0 is located at airport l0_2, 
object t1 is at airport l1_0, object t2 is located at airport l2_0 and package p3 is located in vehicle t2

[Reasoning for the evaluation]
package p3 is located in vehicle t2, but LLM response has(contradition, misslabeling of p3) package p3 is present in vehicle t2,  object p3 is located at airport l2_0

[Answer]
False


Example 4:

[LLM Response]
{llm_response}

[Ground Truth]
{true_response}
"""

def process_data(data_d, free_answers_completed_ids, massive_dump_dir, args):
    if data_d[OUT_OBJ_ID] in free_answers_completed_ids:
        return False

    for k_input, k_output in [[OUT_OBJ_QUESTION, OUT_OBJ_QUESTION_PARAPHRASED], [OUT_OBJ_INITIAL_STATE_NL, OUT_OBJ_INITIAL_STATE_NL_PARAPHRASED]]:
        prompt = eval_free_answers_prompt(data_d[k_input])
        response = api_call(prompt, DEFAULT_MODEL, OUTPUT_TOKEN_LIMIT)
        if not response:
            return False
        data_d[k_output] = response.strip()

    with open(f'{massive_dump_dir}/{data_d[OUT_OBJ_ID]}.json', 'w') as f:
        json.dump(data_d, f)

    return True



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    massive_dump_dir = f'{PROJECT_PATH}/data/free_answers'
    os.makedirs(massive_dump_dir, exist_ok=True)

    free_answers_completed_ids = set([f.strip('.json') for f in os.listdir(massive_dump_dir) if f.endswith('.json')])
    print(len(free_answers_completed_ids))
    print('gathered ids')

    test_data = open_jsonl(f'{PROJECT_PATH}/data/test_dataset.jsonl')
    random.shuffle(test_data)

    # Multithreading: Using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for data_d in test_data:
            if data_d[OUT_OBJ_ID] not in free_answers_completed_ids:
                futures.append(executor.submit(process_data, data_d, free_answers_completed_ids, massive_dump_dir, args))

        # Iterate over the results to ensure all tasks complete
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(test_data)):
            try:
                future.result()  # Get the result (or raise exceptions if any occurred)
            except Exception as e:
                print(f"Exception occurred: {e}")
