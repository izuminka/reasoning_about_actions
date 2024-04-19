from domains import *
from questions import *

QUESTION_CLASSES = [ObjectTrackingQuestions,
                    FluentTrackingQuestions,
                    StateTrackingQuestions,
                    ActionExecutabilityQuestions,
                    EffectsQuestions,
                    NumericalReasoningQuestions,
                    HallucinationQuestions,
                    CompositeQuestions]
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
    question_multiplicity = 1
    upper_instance = 11
    for is_random_sub in [False, True]:
        for domain_class in ALL_DOMAIN_CLASSES:
            domain = domain_class(is_random_sub=is_random_sub, is_ramifications=False) # for questions, is_ramifications does not matter T/F, only for prompts
            for i in range(1, upper_instance):
                instance_name = f'Instance_{i}'
                jsonl_instance = open_jsonl(STATES_ACTIONS_PATH + f'/{domain.DOMAIN_NAME}/{instance_name}.jsonl')

                save_dir = os.path.join(f'{QUESTIONS_PATH}_m{question_multiplicity}', random_sub_keyword(is_random_sub), domain.DOMAIN_NAME)
                # if os.path.exists(save_dir):
                #     continue

                all_questions = AllQuestions(jsonl_instance, domain, instance_name, question_multiplicity=question_multiplicity)
                all_questions.generate_all_questions()
                all_questions.save_questions(save_dir)
                print(domain.DOMAIN_NAME, is_random_sub, instance_name, 'done')
