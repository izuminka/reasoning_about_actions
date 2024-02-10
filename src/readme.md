Data Computation

`/inital_state_generation`
 - PDDL instances are created, plan is computed and validated. 
 - Instances are automatically converted to ASP

`states_actions_generation.py`
- Given ASP domain, instance and plan `jsonl` file is computed with states and actions branching (depth 1) from the given plan

`/question_construction`
- Given computed `jsonl` and domain name questions are generated
