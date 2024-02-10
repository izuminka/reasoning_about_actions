import os
import seaborn as sns
import matplotlib.pyplot as plt
import random
from pathlib import Path

DOMAINS = ['Blocksworld', 'Depots', 'DriverLog', 'GoldMiner', 'Visitall', 'NPuzzle', 'Satellite', 'Spanner', 'ZenoTravel', 'Grippers', 'Logistics', 'Miconic', 'Mystery']
DOMAINS = ['Mystery']
SELECTED_LENGTH = 20
NO_OF_INSTANCES = 10
START_IDX = 1    # Index that is used for saving the instances

def add_dict(object_path, count_dict):
    with open(object_path, 'r') as f:
        objects = f.read()
    object_length = len(objects.split(';'))

    if object_length in count_dict:
        count_dict[object_length] += 1
    else:
        count_dict[object_length] = 1
    return count_dict

def main():
    for domain in DOMAINS:
        # Getting plan lengths
        plan_lengths = []
        for folder_name in os.listdir(os.path.join('Domains', domain, 'ASP')):
            plan_file_path = os.path.join('Domains', domain, 'ASP', folder_name, 'plan.lp')
            with open(plan_file_path, 'r') as f:
                plan_lengths.append(len(f.readlines()))
        print(domain)
        print(plan_lengths)
        print()
        
        
        d = {}
        for plan_length in plan_lengths:
            if plan_length in d:
                d[plan_length] += 1
            else:
                d[plan_length] = 1
        

        X = [ele for ele in range(min(plan_lengths), max(plan_lengths)+1)]
        Y = [d[ele] if ele in d else 0 for ele in X]

        # Generating a bar graph for the list
        ax = sns.barplot(x=X, y=Y)
        ax.bar_label(ax.containers[0])
        ax.tick_params(axis='x', rotation=90)
        plt.xlabel('Plan Length')
        plt.ylabel('Number of instances')
        plt.title(f'Domain {domain} - Total Instances: {len(plan_lengths)}')
        plt.savefig(os.path.join('Domains', domain, 'plan_lengths.jpg'))
        # plt.show()

def plot_objects(domain):    # Blocksworld, GoldMiner
    # Creating dictionary containing the objects of the selected length
    objects_count = {}
    selected_instances = []
    for folder_name in os.listdir(os.path.join('Domains', domain, 'ASP')):
        with open(os.path.join('Domains', domain, 'ASP', folder_name, 'plan.lp'), 'r') as f:
            plan_length = len(f.readlines())
            if plan_length >= SELECTED_LENGTH:
                selected_instances.append(folder_name.split('_')[1])
                print(f'{folder_name} has a plan of length {plan_length}')
                objects_count = add_dict(os.path.join('Domains', domain, 'ASP', folder_name, 'objects.lp'), objects_count)
    print(objects_count)
    
    # Plotting the bar plot
    X = [ele for ele in range(min(objects_count.keys()), max(objects_count.keys())+1)]
    Y = [objects_count[ele] if ele in objects_count else 0 for ele in X]
    ax = sns.barplot(x=X, y=Y)
    ax.bar_label(ax.containers[0])
    ax.tick_params(axis='x', rotation=90)
    plt.xlabel('Number of objects')
    plt.ylabel('Number of instances')
    plt.title(f'Domain {domain} - Total Instances: {sum(Y)}')
    plt.savefig(os.path.join('Domains', domain, f'objects_plan_{SELECTED_LENGTH}.jpg'))

    # Saving random instances to Initial Conditions
    if NO_OF_INSTANCES-START_IDX+1 < len(selected_instances):
        selected_instances = random.sample(selected_instances, NO_OF_INSTANCES-START_IDX+1)
    print('\nSelected Instances:\n', selected_instances)
    for index, selected_instance in enumerate(selected_instances):
        # Saving ASP
        temp_path = os.path.join('Temp', 'ASP', f'Instance_{START_IDX+index}')
        Path(temp_path).mkdir(parents=True, exist_ok=True)
        asp_path = os.path.join('Domains', domain, 'ASP', f'Instance_{selected_instance}', '*')
        os.system(f'cp {asp_path} {temp_path}')
        # Saving PDDL
        temp_path = os.path.join('Temp', 'PDDL', f'Instance_{START_IDX+index}')
        Path(temp_path).mkdir(parents=True, exist_ok=True)
        instance_path = os.path.join('Domains', domain, 'Instances', f'instance_{selected_instance}.pddl')
        os.system(f'cp {instance_path} {temp_path}')
        plan_path = os.path.join('Domains', domain, 'Plans', f'plan_{selected_instance}.pddl')
        os.system(f'cp {plan_path} {temp_path}')

def final_domain_check(domain):
    # Checking if any instance is repeated
    instances = []
    for i in range(NO_OF_INSTANCES):
        with open(os.path.join('Initial_Conditions', domain, 'PDDL', f'Instance_{i+1}', 'instance.pddl'), 'r') as f:
            instance = f.read().strip()
            if instance in instances:
                print(f'Instance {i+1} is repeated.')
            else:
                instances.append(instance)
    
    # Checking if the plans are valid
    domain_file_path = os.path.join('Domains', domain, 'domain.pddl')
    for i in range(NO_OF_INSTANCES):
        instance_file_path = os.path.join('Initial_Conditions', domain, 'PDDL', f'Instance_{i+1}', 'instance.pddl')
        plan_file_path = os.path.join('Initial_Conditions', domain, 'PDDL', f'Instance_{i+1}', 'plan.pddl')
        os.system(f'VAL/build/linux64/Release/bin/Validate -v {domain_file_path} {instance_file_path} {plan_file_path} > tmp.pddl')

        with open('tmp.pddl', 'r') as f:
            if 'Plan Valid' in f.read():
                print(f'Instance_{i+1} is validated')
            else:
                print(f'Instance_{i+1} failed during validation :(')
    
    # Saving a plot for number of objects
    objects_count = {}
    for i in range(NO_OF_INSTANCES):
        objects_count = add_dict(os.path.join('Initial_Conditions', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), objects_count)
    print(objects_count)
    
    # Plotting the bar plot
    X = [ele for ele in range(min(objects_count.keys()), max(objects_count.keys())+1)]
    Y = [objects_count[ele] if ele in objects_count else 0 for ele in X]
    ax = sns.barplot(x=X, y=Y)
    ax.bar_label(ax.containers[0])
    ax.tick_params(axis='x', rotation=90)
    plt.xlabel('Number of objects')
    plt.ylabel('Number of instances')
    plt.title(f'Domain {domain} - Total Instances: {sum(Y)}')
    plt.savefig(os.path.join('Initial_Conditions', domain, f'objects_plan_{SELECTED_LENGTH}.jpg'))

if __name__ == '__main__':
    # main()
    plot_objects(DOMAINS[0])    # For one specific domain ; Also saves the instances in Initial Condition
    # final_domain_check(DOMAINS[0])    # For one specific domain