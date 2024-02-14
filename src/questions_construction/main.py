from domains import *
from questions import *

QUESTION_CLASSES = [ObjectTrackingQuestions,
                    FluentTrackingQuestions,
                    StateTrackingQuestions,
                    ActionExecutabilityQuestions,
                    EffectsQuestions,
                    NumericalReasoningQuestions,
                    HallucinationQuestions]
QUESTION_CATEGORIES = [q_class.question_category() for q_class in QUESTION_CLASSES]


class AllQuestions:
    def __init__(self, jsonl_instance, domain_class, instance_id, question_multiplicity=QUESTION_MULTIPLICITY, plan_lengths=PLAN_LENGTHS):
        self.jsonl_instance = jsonl_instance
        self.domain_class = domain_class
        self.instance_id = instance_id
        self.question_multiplicity = question_multiplicity
        self.plan_lengths = plan_lengths
        self.all_questions = []
        self.q_types = [
            ObjectTrackingQuestions(jsonl_instance, domain_class, instance_id),
            FluentTrackingQuestions(jsonl_instance, domain_class, instance_id),
            StateTrackingQuestions(jsonl_instance, domain_class, instance_id),
            ActionExecutabilityQuestions(jsonl_instance, domain_class, instance_id),
            EffectsQuestions(jsonl_instance, domain_class, instance_id),
            NumericalReasoningQuestions(jsonl_instance, domain_class, instance_id),
            HallucinationQuestions(jsonl_instance, domain_class, instance_id)
        ]

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
    # domain = Zenotravel()
    # i = 1
    # instance_name = f'Instance_{i}'
    # jsonl_instance = open_jsonl(STATES_ACTIONS_PATH + f'/{domain.DOMAIN_NAME}/{instance_name}.jsonl')
    # all_questions = AllQuestions(jsonl_instance, domain, instance_name)
    # all_questions.generate_all_questions()
    # all_questions.save_questions()

    # for domain_class in ALL_DOMAIN_CLASSES:
    #     domain = domain_class()
    #     print(domain.DOMAIN_NAME)
    #     i = 1
    #     instance_name = f'Instance_{i}'
    #     jsonl_instance = open_jsonl(STATES_ACTIONS_PATH + f'/{domain.DOMAIN_NAME}/{instance_name}.jsonl')
    #     all_questions = AllQuestions(jsonl_instance, domain, instance_name)
    #     all_questions.generate_all_questions()
    #     all_questions.save_questions()

    for domain_class in ALL_DOMAIN_CLASSES:
        domain = domain_class()
        print(domain.DOMAIN_NAME)
        for i in range(1, 11):
            print(i)
            instance_name = f'Instance_{i}'
            jsonl_instance = open_jsonl(STATES_ACTIONS_PATH + f'/{domain.DOMAIN_NAME}/{instance_name}.jsonl')
            all_questions = AllQuestions(jsonl_instance, domain, instance_name)#, question_multiplicity=multiplicity, plan_lengths=plan_lengths)
            all_questions.generate_all_questions()
            all_questions.save_questions()