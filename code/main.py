# Input 
# domain
# init/final conditions
# Sequence of actions


# Iteratively start from init, 
# 1. take all actions, output the state
    # mark feasable vs infeasable actions
# 2. generate questions about the state

# Generate questions about the state
# Question about the state of the world
# Next feasible and infeasable actions 

def assemble_asp(domain_path, instance_path, asp_general_path):
    asp_script = ''

    with open(asp_general_path) as f:
        general_asp = f.read()
    asp_script += '% GENERAL -------------------- \n\n'
    asp_script += general_asp + '\n\n'

    with open(domain_path) as f:
        domain = f.read()
    asp_script += '% DOMAIN  --------------------\n\n'
    asp_script += domain + '\n\n'

    with open(instance_path) as f:
        instance = f.read()
    asp_script += '% OBJECTS & INIT/GOAL --------------------\n\n'
    asp_script += instance

    return asp_script

