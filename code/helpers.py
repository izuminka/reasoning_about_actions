# @staticmethod
# def extract_instance_state(instance_str, state_type):
#     if state_type == "init":
#         match = DataGenerator.INIT_REGEX.search(instance_str)
#         if not match:
#             raise Exception("No init state found in instance file.")
#     elif state_type == "goal":
#         match = DataGenerator.GOAL_REGEX.search(instance_str)
#         if not match:
#             raise Exception("No goal state found in instance file.")
#     else:
#         raise Exception("Unknown state type.")
#     return match.group(0)
#
#
# def __init__(self, asp_domain_path, asp_instance_path):
#     self.domain_path = asp_domain_path
#     self.asp_domain = self.open_asp(self.domain_path)
#
#     self.asp_instance_path = asp_instance_path
#     self.asp_instance = self.open_asp(self.asp_instance_path)
#
#     init_state_string = self.extract_instance_state(self.asp_instance, state_type="init")
#     goal_state_string = self.extract_instance_state(self.asp_instance, state_type="goal")
#
#     self.initial_state = self.string_state_to_set(init_state_string, prefix='init(')
#     self.goal_state = self.string_state_to_set(goal_state_string, prefix='goal(')
#     self.objects_str = self.asp_instance.replace(init_state_string, "").replace(goal_state_string, "")