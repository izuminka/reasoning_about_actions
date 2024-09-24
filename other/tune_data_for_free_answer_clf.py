import sys
sys.path.insert(0, '../../')
from questions_construction.questions import *
from common import *
import base64
import hashlib


ASP_ID ='asp_id'
ASP_DATA = 'asp_data'
ASP_DATA_TYPE = 'asp_data_type'
ASP_DATA_TYPE_FLUENTS = 'fluents'
ASP_DATA_TYPE_OBJ = 'objects'
ASP_DATA_TYPE_ACTIONS = 'actions'

MAX_SENT_LEN = 3000

def unique_id(data):
    hasher = hashlib.sha1(str(data).encode('ascii'))
    return base64.urlsafe_b64encode(hasher.digest())

def out_obj(asp):
    return {'asp': asp, }


def fluent_type_to_fluent_nl(fluent_type):
    if fluent_type == BASE_FLUENTS:
        return BASE_FLUENTS_NL
    elif fluent_type == DERIVED_FLUENTS:
        return DERIVED_FLUENTS_NL
    elif fluent_type == PERSISTENT_FLUENTS:
        return PERSISTENT_FLUENTS_NL
    elif fluent_type == STATIC_FLUENTS:
        return STATIC_FLUENTS_NL
    else:
        raise ValueError(f'Undefined fluent type {fluent_type}')


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

    def nl_variations_helper(self, asp_ls, to_nl_function, num_variations, max_len=MAX_SENT_LEN):
        nl_vatiations = set()
        while num_variations > 0:
            for asp in asp_ls:
                try:
                    nl = to_nl_function(asp)
                    if len(nl) < max_len:
                        nl_vatiations.add(nl)
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


    def corrupt_stuff_in_asp(self, fluents, stuff1, stuff2):
        fluents = deepcopy(fluents)
        if len(stuff1) == 1 and len(stuff2) == 1:
            return []
        corrupted_fluents_replaced = []
        num_fluents_to_corrupt = random.randint(1, len(fluents))
        for fluent in fluents[:num_fluents_to_corrupt]:
            for o1, o2 in zip(stuff1, stuff2):
                o1, o2 = str(o1), str(o2)
                if o1 in fluent:
                    corrupted_fluents_replaced.append(fluent.replace(o1, o2))
                    break
        result = corrupted_fluents_replaced + fluents[num_fluents_to_corrupt:]
        if result == fluents:
            return []
        return result

    def remove_numbers_in_objects(self, fluents):
        stuff1 = list(range(20, -1, -1))
        stuff2 = ['' for _ in range(len(stuff1))]
        return self.corrupt_stuff_in_asp(fluents, stuff1, stuff2)

    def corrupt_numbers(self, fluents):
        stuff1 = list(range(20, -1, -1))
        stuff2 = self.derange(deepcopy(stuff1))
        return self.corrupt_stuff_in_asp(fluents, stuff1, stuff2)

    def corrupt_objects(self, fluents):
        stuff1 = deepcopy(self.all_objects)
        stuff2 = self.derange(deepcopy(self.all_objects))
        return self.corrupt_stuff_in_asp(fluents, stuff1, stuff2)

    def corrupt_object_types(self, fluents):
        stuff1 = deepcopy(list(self.objects_by_type.keys()))
        stuff2 = self.derange(deepcopy(list(self.objects_by_type.keys())))
        return self.corrupt_stuff_in_asp(fluents, stuff1, stuff2)

    def all_nl_variations(self, data_dict, num_shuffles=10, num_variations=5):
        if data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_FLUENTS:
            perturbed_fluents = self.purturb_helper(data_dict, num_shuffles)
            nl_vatiations = self.nl_variations_helper(perturbed_fluents, partial(self.nl_fluents, is_sorted=False), num_variations)
            return list(nl_vatiations)
        elif data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_OBJ:
            perturbed_obj = self.purturb_helper(data_dict, num_shuffles)
            nl_vatiations = self.nl_variations_helper(perturbed_obj, partial(self.nl_objects, is_sorted=False), num_variations)
            return list(nl_vatiations)
        elif data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_ACTIONS:
            actions = [deepcopy(data_dict[ASP_DATA])]
            nl_vatiations = self.nl_variations_helper(actions, self.nl_actions, num_variations)
            return list(nl_vatiations)




    def general_asp_corrution(self, og_asp_obj_ls, function_corruption):
        result_set = []
        asp_obj_copy = deepcopy(og_asp_obj_ls)
        result_set.append(function_corruption(list(asp_obj_copy)))

        # Case1.2 flip the negations of some fluents and remove some fluents
        asp_obj_copy = deepcopy(og_asp_obj_ls)
        random.shuffle(asp_obj_copy)
        if int(len(asp_obj_copy) / 2) > 0:
            rand_i = random.randint(int(len(asp_obj_copy) / 2), len(asp_obj_copy))
            result_set.append(function_corruption(list(asp_obj_copy)[:rand_i]))
        # TODO: consider adding, + # of fluents

        final = set()
        for r in result_set:
            if r != og_asp_obj_ls:
                random.shuffle(r)
                final.add(tuple(r))
        return final

    def corrupt_actions(self, actions):
        not_present_actions = set(self.inexecutable_actions[1]).union(set(self.executable_actions[1])) - set(actions)
        if not not_present_actions:
            return []

        not_present_actions = list(not_present_actions)
        random.shuffle(not_present_actions)

        subbed_actions = deepcopy(actions)
        random_ids = random.sample(range(len(actions)), random.randint(1, min(len(not_present_actions), len(actions))))
        not_present_actions = not_present_actions[:len(random_ids)]
        if not not_present_actions:
            return []

        for i, sub in zip(random_ids, not_present_actions):
            subbed_actions[i] = sub
        return subbed_actions


    def corrupt_nl_variations(self, data_dict, num_corruptions=10, num_nl_variations=5):
        corrupted_set = set()
        if data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_FLUENTS:
            og_fluents = deepcopy(data_dict[ASP_DATA])
            slightly_corrupted_fluents = deepcopy(og_fluents)
            random.shuffle(slightly_corrupted_fluents)
            slightly_corrupted_fluents = self.corrupt_fluents(list(slightly_corrupted_fluents), 0.1)
            while num_corruptions > 0:
                # Case1.1 flip the negations of some fluents
                res = self.general_asp_corrution(og_fluents, self.corrupt_fluents)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                # Case2.1 corrupt_objects_in_fluents
                res = self.general_asp_corrution(og_fluents, self.corrupt_objects)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                # Case3.1 corrupt_object_types_in_fluents
                res = self.general_asp_corrution(slightly_corrupted_fluents, self.corrupt_object_types)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                # Case4.1 corrupt_numbers_in_fluents
                res = self.general_asp_corrution(slightly_corrupted_fluents, self.corrupt_numbers)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                # Case4.2 remove numbers in objects
                res = self.general_asp_corrution(slightly_corrupted_fluents, self.remove_numbers_in_objects)
                num_corruptions -= len(res)
                corrupted_set.update(res)
                to_nl_function = self.nl_fluents
        elif data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_OBJ:
            og_objects = deepcopy(data_dict[ASP_DATA])
            while num_corruptions > 0:

                res = self.general_asp_corrution(og_objects, self.remove_numbers_in_objects)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                res = self.general_asp_corrution(og_objects, self.corrupt_object_types)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                res = self.general_asp_corrution(og_objects, self.corrupt_numbers)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                # TODO add random new objects
                to_nl_function = partial(self.nl_objects, is_sorted=False)
        elif data_dict[ASP_DATA_TYPE] == ASP_DATA_TYPE_ACTIONS:
            og_actions = deepcopy(data_dict[ASP_DATA])
            while num_corruptions > 0:

                res = self.general_asp_corrution(og_actions, self.corrupt_actions)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                res = self.general_asp_corrution(og_actions, self.corrupt_numbers)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                res = self.general_asp_corrution(og_actions, self.remove_numbers_in_objects)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                res = self.general_asp_corrution(og_actions, self.corrupt_object_types)
                num_corruptions -= len(res)
                corrupted_set.update(res)

                # TODO add random new actions

                to_nl_function = self.nl_actions
        else:
            return []

        if () in corrupted_set:
            corrupted_set.remove(())
        nl_vatiations = self.nl_variations_helper(corrupted_set, to_nl_function, num_nl_variations)
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
                        if data_all_nl_variations:
                            data_corrupt_nl_variations = self.corrupt_nl_variations(data)
                            all.extend(self.create_pairs(data_all_nl_variations))
                            all.extend(self.create_pairs(data_all_nl_variations, data_corrupt_nl_variations))
        return all


class ObjectTrackingPairs(AnswerPairGeneratorHelper):
    QUESTION_CATEGORY = 'object_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_1(self, plan_length):
        random_object_type = random.choice(list(self.objects_by_type.keys()))
        question = f"{self.nl_question_prefix(plan_length)} list all objects associated with type {random_object_type}. {NONE_STATEMENT}."
        answer = self.objects_by_type[random_object_type]
        # nl_answer = asp_to_nl(sorted(answer), lambda x: x)
        # return self.qa_data_object(question, nl_answer, FREE_ANSWER_TYPE, self.question_1.__name__, plan_length, None)
        if answer:
            return {ASP_ID: unique_id(answer),
                    ASP_DATA: answer,
                    ASP_DATA_TYPE: ASP_DATA_TYPE_OBJ} | self.qa_data_object(question, None, FREE_ANSWER_TYPE,
                                                                                question_name, plan_length, None, None)
        return None

    def question_2(self, plan_length):
        random_object_type = random.choice(list(self.objects_by_type.keys()))
        random_objects = random.sample(self.objects_by_type[random_object_type],
                                       random.randint(1, len(self.objects_by_type[random_object_type])))
        nl_random_objects = asp_to_nl(random_objects, lambda x: x)
        question = f"{self.nl_question_prefix(plan_length)} what is the object type for {nl_random_objects}. {NONE_STATEMENT}."
        if random_objects:
            return {ASP_ID: unique_id(random_objects),
                    ASP_DATA: random_objects,
                    ASP_DATA_TYPE: ASP_DATA_TYPE_OBJ} | self.qa_data_object(question, None, FREE_ANSWER_TYPE,
                                                                                question_name, plan_length, None, None)
        return None
        # return self.qa_data_object(question, random_object_type, FREE_ANSWER_TYPE, self.question_2.__name__,
        #                            plan_length, None)

    def question_iterators(self):
        return chain([self.question_1, self.question_2])



class FluentTrackingPairs(AnswerPairGeneratorHelper):
    QUESTION_CATEGORY = 'fluent_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_3_helper(self, plan_length, fluent_type, is_pos_fluent_question, question_name):
        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type=fluent_type)
        if not pos_fluents and not neg_fluents:
            return None

        question = (f"{self.nl_question_prefix(plan_length)}, what are the {fluent_type_to_fluent_nl(fluent_type)} for {obj}? "
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
            for is_pos_fluent_question in POS_NEG_FLUENTS_KEY_LIST:
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
        if is_pos_fluent_question == True:
            fluent_type_nl = POSITIVE_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length]
        elif is_pos_fluent_question == False:
            fluent_type_nl = NEGATIVE_FLUENTS_NL
            fluents = self.neg_fluents_given_plan[plan_length]
        else:
            fluent_type_nl = FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length] + self.neg_fluents_given_plan[plan_length]
        nl_fluents = self.nl_fluents(fluents)
        if fluents:
            return {ASP_ID: unique_id(fluents),
                    ASP_DATA: fluents,
                    ASP_DATA_TYPE: ASP_DATA_TYPE_FLUENTS} | self.qa_data_object(None, nl_fluents, FREE_ANSWER_TYPE, question_name, plan_length, None,
                                   is_pos_fluent_question)
        return None


    def questions_iter_2(self):
        counter = 0
        for is_pos_fluent_question in POS_NEG_FLUENTS_KEY_LIST:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          is_pos_fluent_question=is_pos_fluent_question,
                          question_name=question_name(counter, 'iter_2'))

    def question_iterators(self):
        return chain(self.questions_iter_2())

class EffectsPairs(AnswerPairGeneratorHelper):
    QUESTION_CATEGORY = 'effects'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def prefix(self, plan_length):
        if plan_length == 0:
            return f"{INITIAL_CONDITION_PREFIX},"
        else:
            return f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. In this state,"

    def questions_iter_2_helper(self, plan_length, is_pos_fluent_question, question_name):
        action = self.given_plan_sequence[plan_length]
        if is_pos_fluent_question == POS_NEG_FLUENTS_KEY_LIST:
            fluents_type_nl = FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length + 1] + self.neg_fluents_given_plan[plan_length + 1]
        elif is_pos_fluent_question == POS_FLUENTS_QUESTION:
            fluents_type_nl = POSITIVE_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length + 1]
        else:
            fluents_type_nl = NEGATIVE_FLUENTS_NL
            fluents = self.neg_fluents_given_plan[plan_length + 1]

        if fluents:
            return {ASP_ID: unique_id(fluents),
                    ASP_DATA: fluents,
                    ASP_DATA_TYPE: ASP_DATA_TYPE_FLUENTS} | self.qa_data_object(None, '', FREE_ANSWER_TYPE, question_name, plan_length, None)
        return None

    def questions_iter_2(self):
        counter = 0
        for is_pos_fluent_question in POS_NEG_FLUENTS_KEY_LIST:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          is_pos_fluent_question=is_pos_fluent_question,
                          question_name=question_name(counter, 'iter_2'))

    def question_iterators(self):
        return chain(self.questions_iter_2())

class ActionExecutabilityPairs(AnswerPairGeneratorHelper):
    QUESTION_CATEGORY = 'action_executability'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_1_helper(self, plan_length, is_answer_true, question_name):
        sequence_of_actions, _random_corrupt_action_i = self.sequence_of_actions(plan_length, is_answer_true)
        nl_sequence_of_actions = asp_to_nl(sequence_of_actions, self.domain_class.action_to_natural_language)
        question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {nl_sequence_of_actions}. Is it possible to execute it, {TRUE_OR_FALSE}?"
        # return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length, None)
        if sequence_of_actions:
            return {ASP_ID: unique_id(sequence_of_actions),
                    ASP_DATA: sequence_of_actions,
                    ASP_DATA_TYPE: ASP_DATA_TYPE_ACTIONS} | self.qa_data_object(None, '', FREE_ANSWER_TYPE,
                                                                                question_name, plan_length, None)
        else:
            return None

    def questions_iter_3_helper(self, plan_length, is_answer_none, question_name):
        if is_answer_none:
            # question = (
            #     f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. "
            #     f"What is the first inexecutable action in the sequence? "
            #     f"{NONE_STATEMENT}.")
            # return self.qa_data_object(question, NONE_ANSWER, FREE_ANSWER_TYPE, question_name, plan_length, None)
            return None
        else:
            sequence_of_actions, random_corrupt_action_i = self.corrupt_action_sequence(plan_length)
            inexecutable_action = sequence_of_actions[random_corrupt_action_i]
            question = (
                f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions(sequence_of_actions)} to reach the current state. "
                f"What is the first inexecutable action in the sequence? "
                f"{NONE_STATEMENT}.")
            # return self.qa_data_object(question, self.domain_class.action_to_natural_language(inexecutable_action),
            #                            FREE_ANSWER_TYPE, question_name, plan_length, None)
            if inexecutable_action:
                return {ASP_ID: unique_id(sequence_of_actions),
                        ASP_DATA: sequence_of_actions,
                        ASP_DATA_TYPE: ASP_DATA_TYPE_ACTIONS} | self.qa_data_object(None, '', FREE_ANSWER_TYPE,
                                                                                    question_name, plan_length, None)
            return None

    def questions_iter_3(self):
        counter = 0
        for is_answer_none in [False]:
            counter += 1
            yield partial(self.questions_iter_3_helper,
                          is_answer_none=is_answer_none,
                          question_name=question_name(counter, 'iter_3'))

    def question_4(self, plan_length):
        question = (f"{self.nl_question_prefix(plan_length)} list all executable actions. "
                    f"{NONE_STATEMENT}.")
        # return self.qa_data_object(question, self.nl_actions(self.executable_actions[plan_length]), FREE_ANSWER_TYPE,
        #                            self.question_4.__name__, plan_length, None)
        if self.executable_actions[plan_length]:
            return {ASP_ID: unique_id(self.executable_actions[plan_length]),
                    ASP_DATA: self.executable_actions[plan_length],
                    ASP_DATA_TYPE: ASP_DATA_TYPE_ACTIONS} | self.qa_data_object(None, '', FREE_ANSWER_TYPE,
                                                                                question_name, plan_length, None)
        return None

    def question_5(self, plan_length):
        question = (f"{self.nl_question_prefix(plan_length)} list all inexecutable actions. "
                    f"{NONE_STATEMENT}.")
        # return self.qa_data_object(question, self.nl_actions(self.inexecutable_actions[plan_length]), FREE_ANSWER_TYPE,
        #                            self.question_5.__name__, plan_length, None)
        if self.inexecutable_actions[plan_length]:
            return {ASP_ID: unique_id(self.inexecutable_actions[plan_length]),
                    ASP_DATA: self.inexecutable_actions[plan_length],
                    ASP_DATA_TYPE: ASP_DATA_TYPE_ACTIONS} | self.qa_data_object(None, '', FREE_ANSWER_TYPE,
                                                                                question_name, plan_length, None)
        return None

    def question_iterators(self):
        return chain(self.questions_iter_3(),
                     [self.question_4, self.question_5])



if __name__ == '__main__':
    upper_instance = 11
    is_random_sub = False
    save_dir = './pairs_new4'
    os.makedirs(save_dir, exist_ok=True)
    for domain_class in ALL_DOMAIN_CLASSES:
        domain = domain_class(is_random_sub=is_random_sub, is_ramifications=False) # for questions, is_ramifications does not matter T/F, only for prompts
        pairs_over_instances = set()
        for i in range(1, upper_instance):
            instance_name = f'Instance_{i}'
            jsonl_instance = open_jsonl(STATES_ACTIONS_PATH + f'/{domain.DOMAIN_NAME}/{instance_name}.jsonl')

            # not working: HallucinationPairs
            for pair_class in [ActionExecutabilityPairs, StateTrackingPairs, FluentTrackingPairs, EffectsPairs, ObjectTrackingPairs]:
                all_questions = pair_class(jsonl_instance, domain, instance_name)
                for p in all_questions.pairs_pipeline():
                    pairs_over_instances.add(p)

        pairs_all = [{'s1': s1, 's2': s2, 'label': label} for s1, s2, label in pairs_over_instances]
        save_jsonl(pairs_all, f'{save_dir}/{domain.DOMAIN_NAME}.actions.jsonl')
        print(domain.DOMAIN_NAME, f'is_random_sub: {is_random_sub}', 'saved')