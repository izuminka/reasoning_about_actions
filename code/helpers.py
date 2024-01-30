# INIT_REGEX = re.compile(r'(init\((.|\n)+\)\.)')
# GOAL_REGEX = re.compile(r'(goal\((.|\n)+\)\.)')

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


#
# def tmp_name():
#     return str(time.time()).replace('.', '_')
#
#
# def rm_tmp_file(file_name):
#     os.system(f"rm {file_name}")
#
#
# def execute_asp(paths, time_limit=ASP_EXECUTION_TIME_LIMIT):
#     if not os.path.isdir(TMP_ASP_EXEC_PATH):
#         os.makedirs(TMP_ASP_EXEC_PATH)
#     solution_save_path = os.path.join(TMP_ASP_EXEC_PATH, f'{tmp_name()}.lp.sol')
#     try:
#         # --outf=0 -V0 --out-atomf=%s. --quiet=1,2,2 | head -n1 | tr ' ' '\n'
#         os.system(f"clingo --outf=2 --opt-mode=OptN --time-limit={time_limit} {paths.join(' ')} > {solution_save_path}")
#         with open(solution_save_path) as f:
#             asp_json = json.load(f)
#         rm_tmp_file(solution_save_path)
#         return asp_json
#     except Exception as e:
#         print(e)
#         print(traceback.format_exc(), '\n')


