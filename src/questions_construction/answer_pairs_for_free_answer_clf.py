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

MAX_SENT_LEN = 2000

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

    def variations_helper(self, fluents_ls, num_variations, max_len=MAX_SENT_LEN):
        nl_vatiations = set()
        for fluents in fluents_ls:
            while num_variations > 0:
                try:
                    nl_flunets = self.nl_fluents(fluents)
                    if len(nl_flunets) < max_len:
                        nl_vatiations.add(nl_flunets)
                except Exception as e:
                    print(e)
                num_variations -= 1
        return list(nl_vatiations)

    def derange(self, ls):
        # sattolo_cycle
        result = deepcopy(ls)
        for i in range(len(ls) - 1, 0, -1):
            # Pick a random index from 0 to i-1 (not picking i itself)
            j = random.randint(0, i - 1)
            result[i], result[j] = result[j], result[i]
        return result


    def corrupt_stuff_in_fluents(self, fluents, stuff1, stuff2):
        fluents = deepcopy(fluents)
        if len(stuff1) == 1 and len(stuff2) == 1:
            return []
        corrupted_fluents_replaced = []
        num_fluents_to_corrupt = random.randint(1, len(fluents))
        for fluent in fluents[:num_fluents_to_corrupt]:
            for o1, o2 in zip(stuff1, stuff2):
                if o1 in fluent:
                    corrupted_fluents_replaced.append(fluent.replace(o1, o2))
                    break
        return corrupted_fluents_replaced + fluents[num_fluents_to_corrupt:]

    def corrupt_objects_in_fluents(self, fluents):
        stuff1 = deepcopy(self.all_objects)
        stuff2 = self.derange(deepcopy(self.all_objects))
        return self.corrupt_stuff_in_fluents(fluents, stuff1, stuff2)

    def corrupt_object_types_in_fluents(self, fluents):
        stuff1 = deepcopy(list(self.objects_by_type.keys()))
        stuff2 = self.derange(deepcopy(list(self.objects_by_type.keys())))
        return self.corrupt_stuff_in_fluents(fluents, stuff1, stuff2)

    def all_nl_variations(self, data_dict, num_shuffles=100, num_variations=50):
        if data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_FLUENTS:
            perturbed_fluents = self.purturb_helper(data_dict, num_shuffles)
            nl_vatiations = self.variations_helper(perturbed_fluents, num_variations)
            return list(nl_vatiations)


    def corrupt_nl_variations(self, data_dict, num_corruptions=100, num_nl_variations=50):
        if data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_FLUENTS:
            og_fluents = deepcopy(data_dict[ASP_DATA])

            corrupted_fluents_set = set()
            while num_corruptions > 0:
                # Case1.1 flip the negations of some fluents
                fluents = deepcopy(og_fluents)
                random.shuffle(fluents)
                corrupted_fluents_set.add(tuple(self.corrupt_fluents(list(fluents))))
                num_corruptions -= 1

                # Case1.2 flip the negations of some fluents and remove some fluents
                fluents = deepcopy(og_fluents)
                random.shuffle(fluents)
                if int(len(fluents)/2) > 0:
                    rand_i = random.randint(int(len(fluents)/2), len(fluents))
                    corrupted_fluents_set.add(tuple(self.corrupt_fluents(list(fluents)[:rand_i])))
                    num_corruptions -= 1
                # TODO: consider adding, + # of fluents

                # Case2.1 swap the numbers in the fluents
                fluents = deepcopy(og_fluents)
                random.shuffle(fluents)
                corrupted_fluents_set.add(tuple(self.corrupt_objects_in_fluents(fluents)))
                num_corruptions -= 1

                # Case2.2 swap the numbers in the fluents
                fluents = deepcopy(og_fluents)
                random.shuffle(fluents)
                if int(len(fluents)/2) > 0:
                    rand_i = random.randint(int(len(fluents)/2), len(fluents))
                    corrupted_fluents_set.add(tuple(self.corrupt_objects_in_fluents(fluents)[:rand_i]))
                    num_corruptions -= 1

                # Case3.1 swap the numbers in the fluents
                fluents = deepcopy(og_fluents)
                random.shuffle(fluents)
                fluents = self.corrupt_fluents(list(fluents), 0.1)
                currupted = self.corrupt_object_types_in_fluents(fluents)
                corrupted_fluents_set.add(tuple(currupted))
                num_corruptions -= 1

                # Case3.2 swap the numbers in the fluents
                fluents = deepcopy(og_fluents)
                random.shuffle(fluents)
                fluents = self.corrupt_fluents(list(fluents), 0.1)
                if int(len(fluents)/2) > 0:
                    rand_i = random.randint(int(len(fluents)/2), len(fluents))
                    corrupted = self.corrupt_object_types_in_fluents(fluents)[:rand_i]
                    corrupted_fluents_set.add(tuple(corrupted))
                    num_corruptions -= 1

            if () in corrupted_fluents_set:
                corrupted_fluents_set.remove(())
            nl_vatiations = self.variations_helper(corrupted_fluents_set, num_nl_variations)
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
    upper_instance = 11
    is_random_sub = False
    save_dir = './pairs_new3'
    os.makedirs(save_dir, exist_ok=True)
    for domain_class in ALL_DOMAIN_CLASSES:
        domain = domain_class(is_random_sub=is_random_sub, is_ramifications=False) # for questions, is_ramifications does not matter T/F, only for prompts
        pairs_over_instances = set()
        for i in range(1, upper_instance):
            instance_name = f'Instance_{i}'
            jsonl_instance = open_jsonl(STATES_ACTIONS_PATH + f'/{domain.DOMAIN_NAME}/{instance_name}.jsonl')

            for pair_class in [StateTrackingPairs, FluentTrackingPairs]:
                all_questions = pair_class(jsonl_instance, domain, instance_name)
                for p in all_questions.pairs_pipeline():
                    pairs_over_instances.add(p)

        pairs_all = [{'s1': s1, 's2': s2, 'label': label} for s1, s2, label in pairs_over_instances]
        save_jsonl(pairs_all, f'{save_dir}/{domain.DOMAIN_NAME}.jsonl')
        print(domain.DOMAIN_NAME, f'is_random_sub: {is_random_sub}', 'saved')

