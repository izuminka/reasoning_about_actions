
import sys
sys.path.insert(0, '../../')
from questions_construction.questions import *

QUESTION_CLASSES = [FluentTrackingQuestions,
                    StateTrackingQuestions,
                    ActionExecutabilityQuestions,
                    EffectsQuestions,
                    NumericalReasoningQuestions,
                    CompositeQuestions] # ObjectTrackingQuestions, HallucinationQuestions
QUESTION_CATEGORIES = [q_class.QUESTION_CATEGORY for q_class in QUESTION_CLASSES]


def random_sub_keyword(is_random_sub):
    if is_random_sub:
        return WITH_RANDOM_SUB
    else:
        return WITHOUT_RANDOM_SUB

class AllQuestions:
    def __init__(self, jsonl_instance, domain_class, instance_id, question_multiplicity=QUESTION_MULTIPLICITY, plan_lengths=PLAN_LENGTHS):
        self.jsonl_instance = jsonl_instance
        self.domain_class = domain_class
        self.instance_id = instance_id
        self.question_multiplicity = question_multiplicity
        self.plan_lengths = plan_lengths
        self.all_questions = []
        self.q_types = [q_class(jsonl_instance, domain_class, instance_id) for q_class in QUESTION_CLASSES]

    def generate_all_questions(self):
        for q_type in self.q_types:
            self.all_questions += q_type.create_questions(self.question_multiplicity, self.plan_lengths)
        return self.all_questions

    def save_questions(self, save_dir=None):
        if save_dir is None:
            save_dir = QUESTIONS_PATH + f'/{self.domain_class.DOMAIN_NAME}'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_path = f'{save_dir}/{self.instance_id}.jsonl'
        save_jsonl(self.all_questions, save_path)


if __name__ == '__main__':
    save_dir_preix = f'{QUESTIONS_PATH}'
    upper_instance = 11
    # plan_lengths = [1, 10, 19]
    all_questions_tmp = []
    for domain_class in ALL_DOMAIN_CLASSES:
        domain = domain_class(is_random_sub=False, is_ramifications=False) # for questions, is_ramifications does not matter T/F, only for prompts
        for i in range(1, upper_instance):
            instance_name = f'Instance_{i}'
            jsonl_instance = open_jsonl(STATES_ACTIONS_PATH + f'/{domain.DOMAIN_NAME}/{instance_name}.jsonl')

            save_dir = os.path.join(save_dir_preix, WITHOUT_RANDOM_SUB, domain.DOMAIN_NAME)
            save_dir_rand = os.path.join(save_dir_preix, WITH_RANDOM_SUB, domain.DOMAIN_NAME)

            all_questions = AllQuestions(jsonl_instance, domain, instance_name)#, plan_lengths=plan_lengths)
            all_questions.generate_all_questions()
            all_questions.save_questions(save_dir)

            # #random sub questions
            # random_sub_all_questions = deepcopy(all_questions)
            # for d in random_sub_all_questions.all_questions:
            #     for k in [OUT_OBJ_ANSWER, OUT_OBJ_QUESTION, OUT_OBJ_INITIAL_STATE_NL]:
            #         d[k] = domain.to_random_substring(d[k])
            #     d['with_random_sub'] = True
            # random_sub_all_questions.save_questions(save_dir_rand)

            print(domain.DOMAIN_NAME, instance_name, 'done')


