import random
import concurrent.futures  # for multithreading
import multiprocessing  # for multiprocessing
import matplotlib.pyplot as plt
import numpy as np

from together_ai_common import *
from analysis.model_performances import clean_response, EVALUATED_FREE_ANSWER_RESPONSE_KEY

DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo" #"meta-llama/Llama-3-70b-chat-hf"
OUTPUT_TOKEN_LIMIT = 5000

# de74b851-4128-4925-822f-ae293ebfea33
# 87a6d1f0-41ec-41d7-8a7e-7eb16bbdf667
# b4b774e9-b795-48bd-a666-433cca536dee
# 3b23da0f-228f-4cb3-a133-db983c86dbe5
# 05bb6907-7037-4962-8495-f8ae22c296f0
# f087c771-8f88-4c84-82f9-b9bcc637877d
# a095c436-cbfe-41d6-b8ac-366e9b01ae6e
def eval_free_answers_prompt(llm_response, true_response):
    return f"""Evaluate whether the LLM response and the ground truth response are semantically the same. Examine the responses, 
provide reasoning for your evaluation, and then Write "True" if the responses are the same or "False" if they are different.
LLM Response or Ground Truth could be "None".

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
package p3 is located in vehicle t2, but LLM response has(contradition, misslabeling of p3) package p3 is present in vehicle t2,  
object p3 is located at airport l2_0

[Answer]
False

Example 4:

[LLM Response]
a link between location2 and location3 exists, a link between location7 and location8 exists, bob is at gate, 
location1 is linked to location2, location3 is linked to location4, location4 is linked to location5, 
location5 and location6 are linked, location6 and location7 are linked, location8 and location9 are linked, 
location9 is linked to gate, nut1 is currently at gate, nut1 is tightened, nut2 is located at gate, nut2 is tightened, 
nut3 is currently at gate, nut3 is tightened, nut4 is at gate, nut4 is tightened, nut5 is at gate, nut5 is tightened, 
shed is linked to location1, spanner1 is carried by bob, spanner2 is carried by bob, spanner3 is carried by bob, 
spanner4 is carried by bob, spanner5 is carried by bob

[Ground Truth]
a link between location8 and location9 exists, bob is carrying spanner1, bob is carrying spanner3, 
a link between location2 and location3 exists, a link between location5 and location6 exists,
location3 is linked to location4, location4 and location5 are linked, location6 is linked to location7, 
nut2 is tightened, nut3 is at gate, nut3 is tightened, nut4 is currently at gate, nut5 is currently at gate, 
bob is carrying spanner4, bob is carrying spanner5, bob is currently at gate, location1 is linked to location2, 
location7 is linked to location8, location9 and gate are linked, bob is carrying spanner2, 
nut1 is located at gate, nut2 is located at gate, nut5 is tightened, shed is linked to location1, 
tightening of nut1 is complete and tightening of nut4 is complete

[Reasoning for the evaluation]
They are semantically the same

[Answer]
True

Example 5:

[LLM Response]
City c2 contains airport l2_0, City c2 contains airport l2_2

[Ground Truth]
airport l2_1 is located in city c2, airport l2_1 is located in city c2, airport l2_2 is located in city c2, 
airport l2_2 is located in city c2, city c2 contains airport l2_0 and city c2 contains airport l2_0

[Reasoning for the evaluation]
airport l2_1 is located in city c2, airport l2_1 is located in city c2, airport l2_2 is located in city c2 are missing

[Answer]
False

Example 6:

[LLM Response]
airport l0_1 is in city c0, airport l1_0 is in city c1, airport l1_1 is in city c1, airport l1_2 is located in city c1, 
at airport l0_0, object t3 is located, at airport l0_1, object t2 is located, city c0 contains airport l0_0, 
city c0 contains airport l0_2, object a0 is at airport l1_0, object a1 is located at airport l0_0, object t0 is located at airport l0_2, 
package p1 is in vehicle t3, package p0 is in vehicle t3, package p2 is at airport l1_2, object t1 is located at airport l1_0, 
object p3 is located at airport l0_1

[Ground Truth]
airport l0_2 is in city c0, airport l1_0 is located in city c1, airport l1_1 is located in city c1, airport l1_2 is in city c1,
at airport l0_0, object a1 is located, at airport l0_1, object p3 is located, at airport l1_0, object a0 is located, 
city c0 contains airport l0_0, city c0 contains airport l0_1, object p2 is located at airport l1_2, 
object t0 is located at airport l0_2, object t1 is at airport l1_0, object t2 is at airport l0_1, 
object t3 is at airport l0_0, package p0 is located in vehicle t3 and package p1 is in vehicle t3

[Reasoning for the evaluation]
They are semantically the same

[Answer]
True

Example 7:

[LLM Response]
ball1 is at room2, ball2 is at room2, ball3 is at room4, ball4 is at room1, ball5 is at room1, ball6 is at room4, 
ball7 is being carried by robot1's lgripper1, ball8 is at room4, robot1 is at room2, robot1's lgripper1 is not free, 
robot1's rgripper1 is not free, robot1 is carrying ball7 with lgripper1, robot1 is carrying ball6 with rgripper1

[Ground Truth]
ball1 is present at room2, ball2 is at room2, ball3 is present at room4, ball4 is at room1, ball5 is located at room1, 
ball7 is being carried by robot1's lgripper1, ball8 is present at room4, rgripper1 of robot1 is carrying ball6 and robot1 is present in room2

[Reasoning for the evaluation]
According to the ground truth, robot1 is carrying ball6, but LLM gives a contradictory response: that ball6 is at room4

[Answer]
False

----------------------------------------------------------------------------
Given the examples and instructions above, evaluate the following responses:

[LLM Response]
{llm_response}

[Ground Truth]
{true_response}
"""

def process_data(data_d, free_answers_completed_ids, massive_dump_dir):
    if data_d[OUT_OBJ_ID] in free_answers_completed_ids:
        return False

    if not MODEL_RESPONSE_CLEAN_KEY in data_d:
        data_d[MODEL_RESPONSE_CLEAN_KEY] = clean_response(data_d[MODEL_RESPONSE_KEY])

    prompt = eval_free_answers_prompt(data_d[MODEL_RESPONSE_CLEAN_KEY], data_d[OUT_OBJ_ANSWER])
    api_response = api_call(prompt, DEFAULT_MODEL, OUTPUT_TOKEN_LIMIT)
    if not api_response:
        return False
    data_d[EVALUATED_FREE_ANSWER_RESPONSE_KEY] = api_response.strip()

    with open(f'{massive_dump_dir}/{data_d[OUT_OBJ_ID]}.json', 'w') as f:
        json.dump(data_d, f)

    return True



if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # args = parser.parse_args()

    # #TODO rm
    # file_name = 'template_data_10_pct_gpt-4o'
    # input_file_path = f'./responses_rebuttal/{file_name}.jsonl'
    # save_dir = f'./responses_rebuttal_evaluated'
    # massive_dump_dir = f'{save_dir}/{file_name}'

    question_ids_file_name = 'test_data.paraphrased.cleaned'
    prompt_type = FEW_SHOT_3_PROMPT_KEY #ZERO_SHOT_PROMPT_KEY
    ramification = WITHOUT_RAMIFICATIONS
    model = 'llama_8b' #'gpt-4o' #'llama_70b' 'llama_8b''llama_70b' #'llama_8b.finetuned_free' #
    save_dir = f'{PROJECT_PATH}/data/free_answers/{ramification}/{prompt_type}'
    massive_dump_dir = f'{save_dir}/{model}'
    os.makedirs(massive_dump_dir, exist_ok=True)


    free_answers_completed_ids = set([f.strip('.json') for f in os.listdir(massive_dump_dir) if f.endswith('.json')])
    print(len(free_answers_completed_ids))
    print('gathered ids')

    questions_ids = open_jsonl(f'{DATA_PATH}/{question_ids_file_name}.jsonl')
    questions_by_id = {d[OUT_OBJ_ID]: d for d in questions_ids}
    selected_ids = [d[OUT_OBJ_ID] for d in questions_ids if d[OUT_OBJ_ANSWER_TYPE] == FREE_ANSWER_TYPE]

    model_responses_dir = f'{PROJECT_PATH}/data/prompting_results/{ramification}/{prompt_type}'
    model_responses = open_jsonl(os.path.join(model_responses_dir, f'{model}.jsonl'))
    # model_responses = open_jsonl(input_file_path)
    model_responses = [d | questions_by_id[d[OUT_OBJ_ID]] for d in model_responses if d[OUT_OBJ_ID] in selected_ids]
    random.shuffle(model_responses)

    # for data_d in tqdm(model_responses):
    #     if data_d[OUT_OBJ_ID] not in free_answers_completed_ids:
    #         process_data(data_d, free_answers_completed_ids, massive_dump_dir)
    # Multithreading: Using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for data_d in model_responses:
            if data_d[OUT_OBJ_ID] not in free_answers_completed_ids:
                futures.append(executor.submit(process_data, data_d, free_answers_completed_ids, massive_dump_dir))

        # Iterate over the results to ensure all tasks complete
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            try:
                future.result()  # Get the result (or raise exceptions if any occurred)
            except Exception as e:
                print(f"Exception occurred: {e}")


    collected_data = [open_json(f'{massive_dump_dir}/{f}') for f in os.listdir(massive_dump_dir) if f.endswith('.json')]
    save_jsonl(collected_data, f'{save_dir}/{model}.jsonl')
    # save_jsonl(collected_data, f'{save_dir}/{file_name}.jsonl')
