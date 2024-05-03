import sys
sys.path.insert(0, '../../')
from src.questions_construction.questions import *
from src.common import *
import base64
import hashlib
import zipfile

import json

# answer = self.nl_fluents(fluents)
# answer = self.objects_by_type[random_object_type]
# answer = 'None'
# answer = random.sample(self.all_objects, random.randint(2, len(self.all_objects)))[0]
# answer = nl_hallucinated_action
# self.domain_class.action_to_natural_language(inexecutable_action)

ASP_ID ='asp_id'
ASP_DATA = 'asp_data'
ASP_DATA_TYPE = 'asp_data_type'

ASP_DATA_TYPE_FLUENTS = 'fluents'
def unique_id(data):
    hasher = hashlib.sha1(str(data).encode('ascii'))
    return base64.urlsafe_b64encode(hasher.digest())

def out_obj(asp):
    return {'asp': asp, }


class AnswerPairGeneratorHelper(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)


    def purturb_helper(self, data_dict, num_shuffles):
        perturbed_fluents = set()
        for i in range(num_shuffles):
            tmp = deepcopy(data_dict[ASP_DATA])
            random.shuffle(tmp)
            perturbed_fluents.add(tuple(tmp))
        return list(perturbed_fluents)

    def variations_helper(self, fluents, num_variations):
        nl_vatiations = set()
        for fluent in fluents:
            while num_variations > 0:
                nl_vatiations.add(self.nl_fluents(fluent))
                num_variations -= 1
        return list(nl_vatiations)


    def all_nl_variations(self, data_dict, num_shuffles=100, num_variations=100):
        if data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_FLUENTS:
            perturbed_fluents = self.purturb_helper(data_dict, num_shuffles)
            nl_vatiations = self.variations_helper(perturbed_fluents, num_variations)
            return list(nl_vatiations)

    def corrupt_nl_variations(self, data_dict, num_shuffles=10, num_corruptions=100, num_nl_variations=10):
        if data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_FLUENTS:
            perturbed_fluents = self.purturb_helper(data_dict, num_shuffles)

            corrupted_fluents = set()
            for fluents in perturbed_fluents:
                while num_corruptions > 0:
                    corrupted_fluents.add(tuple(self.corrupt_fluents(list(fluents))))
                    num_corruptions -= 1
                    if int(len(fluents)/2) > 0:
                        rand_i = random.randint(int(len(fluents)/2), len(fluents))
                        corrupted_fluents.add(tuple(self.corrupt_fluents(list(fluents)[:rand_i])))
                        num_corruptions -= 1
                    # TODO: consider adding, + # of fluents

            nl_vatiations = self.variations_helper(corrupted_fluents, num_nl_variations)
            return list(nl_vatiations)
    def create_pairs(self, good, bad=None):
        if not bad:
            pairs = []
            for i in range(len(good)):
                for j in range(i, len(good)):
                    pairs.append((good[i], good[j], 'True'))
        else:
            pairs = []
            for i in range(len(good)):
                for j in range(len(bad)):
                    pairs.append((good[i], bad[j], 'False'))
        return pairs


    def pairs_pipeline(self, plan_lengths=range(1,20), num_tries = 10):
        all = []
        for plan_length in plan_lengths:
            for question_constructor in self.question_iterators():
                while num_tries > 0:
                    num_tries -= 1
                    data = question_constructor(plan_length)
                    if data:
                        data_all_nl_variations = self.all_nl_variations(data)
                        data_corrupt_nl_variations = self.corrupt_nl_variations(data)
                        all.extend(self.create_pairs(data_all_nl_variations))
                        all.extend(self.create_pairs(data_all_nl_variations, data_corrupt_nl_variations))
        return all

class FluentTrackingPairs(AnswerPairGeneratorHelper):
    QUESTION_CATEGORY = 'fluent_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_3_helper(self, plan_length, fluent_type, is_pos_fluent_question, question_name):
        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type=fluent_type)
        if not pos_fluents and not neg_fluents:
            return None

        question = (f"{self.nl_question_prefix(plan_length)}. "
                    f"What are the {fluent_type_to_fluent_nl(fluent_type)} for {obj}? "
                    f"{NONE_STATEMENT}")
        fluents = self.fluent_helper(pos_fluents, neg_fluents, True, is_pos_fluent_question)
        if fluents:
            return {ASP_ID: unique_id(fluents),
                    ASP_DATA: fluents,
                    ASP_DATA_TYPE: ASP_DATA_TYPE_FLUENTS} | self.qa_data_object(question, None, FREE_ANSWER_TYPE, question_name, plan_length, fluent_type, is_pos_fluent_question)
        return None

    def questions_iter_3(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_pos_fluent_question in [True, False, None]:
                counter += 1
                yield partial(self.questions_iter_3_helper,
                              fluent_type=fluent_type,
                              is_pos_fluent_question=is_pos_fluent_question,
                              question_name=question_name(counter, 'iter_3'))

    def question_iterators(self):
        return chain(self.questions_iter_3())

class StateTrackingPairs(AnswerPairGeneratorHelper):
    QUESTION_CATEGORY = 'state_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_2_helper(self, plan_length, is_pos_fluent_question, question_name):
        if is_pos_fluent_question:
            fluent_type_nl = POSITIVE_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length]
        else:
            fluent_type_nl = NEGATIVE_FLUENTS_NL
            fluents = self.neg_fluents_given_plan[plan_length]
        nl_fluents = self.nl_fluents(fluents)
        if fluents:
            return {ASP_ID: unique_id(fluents),
                    ASP_DATA: fluents,
                    ASP_DATA_TYPE: ASP_DATA_TYPE_FLUENTS} | self.qa_data_object(None, nl_fluents, FREE_ANSWER_TYPE, question_name, plan_length, None,
                                   is_pos_fluent_question)
        return None

    def questions_iter_2(self):
        counter = 0
        for is_pos_fluent_question in [True, False, None]:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          is_pos_fluent_question=is_pos_fluent_question,
                          question_name=question_name(counter, 'iter_2'))

    def question_iterators(self):
        return chain(self.questions_iter_2())


if __name__ == '__main__':
    question_multiplicity = 1
    upper_instance = 11
    is_random_sub = False
    for domain_class in ALL_DOMAIN_CLASSES:
        pairs_all = []
        domain = domain_class(is_random_sub=is_random_sub, is_ramifications=False) # for questions, is_ramifications does not matter T/F, only for prompts
        for i in range(1, upper_instance):
            instance_name = f'Instance_{i}'

            jsonl_instance = open_jsonl(STATES_ACTIONS_PATH + f'/{domain.DOMAIN_NAME}/{instance_name}.jsonl')
            save_dir = '.'
            # save_dir = os.path.join(f'{QUESTIONS_PATH}_m{question_multiplicity}', random_sub_keyword(is_random_sub), domain.DOMAIN_NAME)
            # if os.path.exists(save_dir):
            #     continue

            for pair_class in [StateTrackingPairs, FluentTrackingPairs]:
                pairs = set()
                all_questions = pair_class(jsonl_instance, domain, instance_name)
                for p in all_questions.pairs_pipeline():
                    pairs.add(p)
                pairs_all.extend(list(pairs))
                print(domain.DOMAIN_NAME, is_random_sub, instance_name, 'done')
            save_jsonl(list(pairs_all), f'./pairs/{domain.DOMAIN_NAME}.jsonl')

    # print('saving')
    # save_jsonl(list(pairs_all), f'pairs_all.jsonl')
    # print('saved')
