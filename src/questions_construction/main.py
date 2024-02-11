from domains import *
from questions import *


class AllQuestions:
    def __init__(self, jsonl_instance, domain_class, instance_id):
        self.jsonl_instance = jsonl_instance
        self.domain_class = domain_class
        self.question_multiplicity = QUESTION_MULTIPLICITY
        self.plan_lengths = PLAN_LENGTHS
        self.all_questions = []
        self.q_types = [ObjectTrackingQuestions(jsonl_instance, domain_class, instance_id),
                        FluentTrackingQuestions(jsonl_instance, domain_class, instance_id),
                        StateTrackingQuestions(jsonl_instance, domain_class, instance_id),
                        ActionExecutabilityQuestions(jsonl_instance, domain_class, instance_id),
                        EffectsQuestions(jsonl_instance, domain_class, instance_id),
                        NumericalReasoningQuestions(jsonl_instance, domain_class, instance_id),
                        # HallucinationQuestions(jsonl_instance, domain_class, instance_id),
                        # LoopingQuestions(jsonl_instance, domain_class, instance_id),
                        ]


    def generate_all_questions(self):
        for q_type in self.q_types:
            self.all_questions += q_type.create_questions(self.question_multiplicity, self.plan_lengths)
        return self.all_questions



if __name__ == '__main__':

    multiplicity = 2

    domain_name = 'blocksworld'
    domain_class = Blocksworld()


    all_questions = []
    for domain_class in domain_list:
        for instance_jsonl in instance_list:
            domain_instance = domain_class(instance_jsonl)
            all_questions += domain_instance.create_questions()
    # TODO add batching
    with open('questions.jsonl', 'w') as f:
        for question in all_questions:
            f.write(json.dumps(question) + '\n')