import random
import os
from pathlib import Path
from pddl import parse_problem

DOMAINS = ['Blocksworld', 'Depots', 'DriverLog', 'GoldMiner', 'Visitall', 'NPuzzle', 'Satellite', 'Spanner', 'ZenoTravel', 'Grippers', 'Logistics', 'Miconic', 'Mystery']
DOMAINS = ['Mystery']    # Overwriting to generate just one domain

NO_OF_EXAMPLES = 100
TIME_LIMIT_FOR_SOLVER = 4*60    # In seconds

def generate_plans(domain, domain_file_path):
    # Creating the plan and saving the plan in relevant directory
    for i in range(NO_OF_EXAMPLES):
        instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
        plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
        os.system(f'./fast-downward.sif --overall-time-limit {TIME_LIMIT_FOR_SOLVER} --plan-file {plan_file_path} {domain_file_path} {instance_file_path} --search "astar(blind())"')

def generate_blocksworld_instances(domain):
    MIN_BLOCKS = 8
    MAX_BLOCKS = 12
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        no_of_boxes = random.randint(MIN_BLOCKS, MAX_BLOCKS)
        os.system(f'Generation/{domain}/blocksworld {no_of_boxes} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_blocksworld(domain):
    for i in range(NO_OF_EXAMPLES):
        try:
            # Checking if a plan exists for the instance or was it timed out
            plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
            with open(plan_file_path, 'r') as f:
                plans_pddl = f.readlines()

            # Creating ASP folder
            Path(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}')).mkdir(parents=True, exist_ok=True)
            instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
            instance = parse_problem(instance_file_path)

            # Getting objects
            objects = 'block('
            for ele in instance.objects:
                objects += str(ele) + '; '
            objects = objects[:-2] + ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), 'w') as f:
                f.write(objects)
            
            # Getting Initial Conditions
            initial = 'init('
            for ele in instance.init:
                ele = str(ele)[1:-1].split()
                if ele[0] == 'handempty':
                    initial += 'handempty;\n'
                elif ele[0] == 'ontable':
                    initial += f'ontable({ele[1]});\n'
                elif ele[0] == 'clear':
                    initial += f'clear({ele[1]});\n'
                elif ele[0] == 'on':
                    initial += f'on({ele[1]}, {ele[2]});\n'
            initial += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'init.lp'), 'w') as f:
                f.write(initial)

            # Getting Goal State
            goal = 'goal('
            for ele in str(instance.goal).split('(')[2:]:
                ele = ele[:-1].split()
                if ele[0] == 'at':
                    goal += f'at({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'on':
                    goal += f'on({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'in':
                    goal += f'in({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'lifting':
                    goal += f'lifting({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'available':
                    goal += f'available({ele[1]});\n'
                elif ele[0] == 'clear':
                    goal += f'clear({ele[1]});\n'
            goal += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'goal.lp'), 'w') as f:
                f.write(goal)

            # Getting Plans
            plans = ''
            for time_stamp, ele in enumerate(plans_pddl):
                ele = str(ele)[1:-2].split()
                if ele[0] == 'unstack':
                    plans += f'occurs(action_unstack({ele[1]},{ele[2]}),{time_stamp+1}).\n'
                elif ele[0] == 'stack':
                    plans += f'occurs(action_stack({ele[1]},{ele[2]}),{time_stamp+1}).\n'
                elif ele[0] == 'put-down':
                    plans += f'occurs(action_put_down({ele[1]}),{time_stamp+1}).\n'
                elif ele[0] == 'pick-up':
                    plans += f'occurs(action_pick_up({ele[1]}),{time_stamp+1}).\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'plan.lp'), 'w') as f:
                f.write(plans)
        except:
            print(f'No plan for instance {i+1}')
            pass


def generate_depots_instances(domain):
    MIN_DEPOTS = 3
    MAX_DEPOTS = 6

    MIN_DISTRIBUTORS = 3
    MAX_DISTRIBUTORS = 6
    
    MIN_TRUCKS = 3
    MAX_TRUCKS = 6
    
    MIN_HOISTS = 3
    MAX_HOISTS = 6
    
    MIN_CRATES = 3
    MAX_CRATES = 6
    
    MIN_PALLETS = 3
    MAX_PALLETS = 6
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        no_of_depots = random.randint(MIN_DEPOTS, MAX_DEPOTS)
        no_of_distributors = random.randint(MIN_DISTRIBUTORS, MAX_DISTRIBUTORS)
        no_of_trucks = random.randint(MIN_TRUCKS, MAX_TRUCKS)
        no_of_hoists = random.randint(MIN_HOISTS, MAX_HOISTS)
        no_of_crates = random.randint(MIN_CRATES, MAX_CRATES)
        no_of_pallets = random.randint(MIN_PALLETS, MAX_PALLETS)

        os.system(f'Generation/{domain}/depots -e {no_of_depots} -i {no_of_distributors} -t {no_of_trucks} -p {no_of_pallets} -h {no_of_hoists} -c {no_of_crates} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_depots(domain):
    for i in range(NO_OF_EXAMPLES):
        try:
            # Checking if a plan exists for the instance or was it timed out
            plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
            with open(plan_file_path, 'r') as f:
                plans_pddl = f.readlines()

            # Creating ASP folder
            Path(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}')).mkdir(parents=True, exist_ok=True)
            instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
            instance = parse_problem(instance_file_path)

            # Getting objects
            depots = 'depot('
            distributors = 'distributor('
            trucks = 'truck('
            pallets = 'pallet('
            crates = 'crate('
            hoists = 'hoist('
            for ele in instance.objects:
                ele = str(ele)
                if ele[:5] == 'depot':
                    depots += ele + '; '
                elif ele[:4] == 'dist':
                    distributors += ele + '; '
                elif ele[:5] == 'truck':
                    trucks += ele + '; '
                elif ele[:4] == 'pall':
                    pallets += ele + '; '
                elif ele[:4] == 'crat':
                    crates += ele + '; '
                elif ele[:4] == 'hois':
                    hoists += ele + '; '
            objects = depots[:-2] + ').\n' + distributors[:-2] + ').\n' + trucks[:-2] + ').\n' + pallets[:-2] + ').\n' + crates[:-2] + ').\n' + hoists[:-2] + ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), 'w') as f:
                f.write(objects)
            
            # Getting Initial Conditions
            initial = 'init('
            for ele in instance.init:
                ele = str(ele)[1:-1].split()
                if ele[0] == 'at':
                    initial += f'at({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'on':
                    initial += f'on({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'in':
                    initial += f'in({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'lifting':
                    initial += f'lifting({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'available':
                    initial += f'available({ele[1]});\n'
                elif ele[0] == 'clear':
                    initial += f'clear({ele[1]});\n'
            initial += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'init.lp'), 'w') as f:
                f.write(initial)

            # Getting Goal State
            goal = 'goal('
            for ele in str(instance.goal).split('(')[2:]:
                ele = ele[:-1].split()
                if ele[0] == 'at':
                    goal += f'at({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'on':
                    goal += f'on({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'in':
                    goal += f'in({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'lifting':
                    goal += f'lifting({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'available':
                    goal += f'available({ele[1]});\n'
                elif ele[0] == 'clear':
                    goal += f'clear({ele[1]});\n'
            goal += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'goal.lp'), 'w') as f:
                f.write(goal)

            # Getting Plans
            plans = ''
            for time_stamp, ele in enumerate(plans_pddl):
                ele = str(ele)[1:-2].split()
                if ele[0] == 'drive':
                    plans += f'occurs(action_drive({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'lift':
                    plans += f'occurs(action_lift({ele[1]},{ele[2]},{ele[3]},{ele[4]}),{time_stamp+1}).\n'
                elif ele[0] == 'drop':
                    plans += f'occurs(action_drop({ele[1]},{ele[2]},{ele[3]},{ele[4]}),{time_stamp+1}).\n'
                elif ele[0] == 'load':
                    plans += f'occurs(action_load({ele[1]},{ele[2]},{ele[3]},{ele[4]}),{time_stamp+1}).\n'
                elif ele[0] == 'unload':
                    plans += f'occurs(action_unload({ele[1]},{ele[2]},{ele[3]},{ele[4]}),{time_stamp+1}).\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'plan.lp'), 'w') as f:
                f.write(plans)
        except:
            pass


def generate_driverlog_instances(domain):
    MIN_JUNCTIONS = 2
    MAX_JUNCTIONS = 4

    MIN_DRIVERS = 2
    MAX_DRIVERS = 4

    MIN_PACKAGES = 2
    MAX_PACKAGES = 5

    MIN_DISTANCE = 1
    MAX_DISTANCE = 3

    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        seed = random.randint(1,1000)
        no_of_junctions = random.randint(MIN_JUNCTIONS, MAX_JUNCTIONS)
        no_of_drivers = random.randint(MIN_DRIVERS, MAX_DRIVERS)
        no_of_packages = random.randint(MIN_PACKAGES, MAX_PACKAGES)
        no_of_distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)

        os.system(f'Generation/{domain}/dlgen {seed} {no_of_junctions} {no_of_drivers} {no_of_packages} {no_of_distance} > temp2.pddl')
        with open('temp2.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_driverlog(domain):
    for i in range(NO_OF_EXAMPLES):
        try:
            # Checking if a plan exists for the instance or was it timed out
            plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
            with open(plan_file_path, 'r') as f:
                plans_pddl = f.readlines()

            # Creating ASP folder
            Path(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}')).mkdir(parents=True, exist_ok=True)
            instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
            instance = parse_problem(instance_file_path)

            # Getting objects
            driver = 'driver('
            truck = 'truck('
            obj = 'obj('
            location = 'location('
            for ele in instance.objects:
                ele = str(ele)
                if ele[:4] == 'truc':
                    truck += ele + '; '
                elif ele[:4] == 'driv':
                    driver += ele + '; '
                elif ele[:4] == 'pack':
                    obj += ele + '; '
                else:
                    location += ele + '; '
            objects = driver[:-2] + ').\n' + truck[:-2] + ').\n' + obj[:-2] + ').\n' + location[:-2] + ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), 'w') as f:
                f.write(objects)
            
            # Getting Initial Conditions
            initial = 'init('
            for ele in instance.init:
                ele = str(ele)[1:-1].split()
                if ele[0] == 'at':
                    initial += f'at({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'in':
                    initial += f'in({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'driving':
                    initial += f'driving({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'link':
                    initial += f'link({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'path':
                    initial += f'path({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'empty':
                    initial += f'empty({ele[1]});\n'
            initial += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'init.lp'), 'w') as f:
                f.write(initial)

            # Getting Goal State
            goal = 'goal('
            for ele in str(instance.goal).split('(')[2:]:
                ele = ele[:-2].split()
                if ele[0] == 'at':
                    goal += f'at({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'in':
                    goal += f'in({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'driving':
                    goal += f'driving({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'link':
                    goal += f'link({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'path':
                    goal += f'path({ele[1]}, {ele[2]});\n'
                elif ele[0] == 'empty':
                    goal += f'empty({ele[1]});\n'
            goal += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'goal.lp'), 'w') as f:
                f.write(goal)

            # Getting Plans
            plans = ''
            for time_stamp, ele in enumerate(plans_pddl):
                ele = str(ele)[1:-2].split()
                if ele[0] == 'load-truck':
                    plans += f'occurs(action_load_truck({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'unload-truck':
                    plans += f'occurs(action_unload_truck({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'board-truck':
                    plans += f'occurs(action_board_truck({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'disembark-truck':
                    plans += f'occurs(action_disembark_truck({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'drive-truck':
                    plans += f'occurs(action_drive_truck({ele[1]},{ele[2]},{ele[3]},{ele[4]}),{time_stamp+1}).\n'
                elif ele[0] == 'walk':
                    plans += f'occurs(action_walk({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'plan.lp'), 'w') as f:
                f.write(plans)
        except Exception as e:
            pass


def generate_goldminer_instances(domain):
    MIN_ROWS = 2
    MAX_ROWS = 6

    MIN_COLS = 2
    MAX_COLS = 6
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        seed = random.randint(1, 1000)
        no_of_rows = random.randint(MIN_ROWS, MAX_ROWS)
        no_of_cols = random.randint(MIN_COLS, MAX_COLS)
        os.system(f'Generation/{domain}/gold-miner-generator -r {no_of_rows} -c {no_of_cols} -s {seed} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_goldminer(domain):
    for i in range(NO_OF_EXAMPLES):
        try:
            # Checking if a plan exists for the instance or was it timed out
            plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
            with open(plan_file_path, 'r') as f:
                plans_pddl = f.readlines()

            # Creating ASP folder
            Path(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}')).mkdir(parents=True, exist_ok=True)
            instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
            instance = parse_problem(instance_file_path)

            # Getting objects
            loc = 'loc('
            for ele in instance.objects:
                ele = str(ele)
                loc += ele + '; '
            objects = loc[:-2] + ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), 'w') as f:
                f.write(objects)
            
            # Getting Initial Conditions
            initial = 'init('
            for ele in instance.init:
                ele = str(ele)[1:-1].split()
                if ele[0] == 'robot-at':
                    initial += f'robot_at({ele[1]});\n'
                elif ele[0] == 'bomb-at':
                    initial += f'bomb_at({ele[1]});\n'
                elif ele[0] == 'laser-at':
                    initial += f'laser_at({ele[1]});\n'
                elif ele[0] == 'soft-rock-at':
                    initial += f'soft_rock_at({ele[1]});\n'
                elif ele[0] == 'hard-rock-at':
                    initial += f'hard_rock_at({ele[1]});\n'
                elif ele[0] == 'gold-at':
                    initial += f'gold_at({ele[1]});\n'
                elif ele[0] == 'arm-empty':
                    initial += f'arm_empty;\n'
                elif ele[0] == 'holds-bomb':
                    initial += f'holds_bomb;\n'
                elif ele[0] == 'holds-laser':
                    initial += f'holds_laser;\n'
                elif ele[0] == 'holds-gold':
                    initial += f'holds_gold;\n'
                elif ele[0] == 'clear':
                    initial += f'clear({ele[1]});\n'
                elif ele[0] == 'connected':
                    initial += f'connected({ele[1]}, {ele[2]});\n'
            initial += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'init.lp'), 'w') as f:
                f.write(initial)

            # Getting Goal State
            goal = 'goal('
            for ele in str(instance.goal).split('(')[1:]:
                ele = ele[:-1].split()
                if ele[0] == 'robot-at':
                    goal += f'robot_at({ele[1]});\n'
                elif ele[0] == 'bomb-at':
                    goal += f'bomb_at({ele[1]});\n'
                elif ele[0] == 'laser-at':
                    goal += f'laser_at({ele[1]});\n'
                elif ele[0] == 'soft-rock-at':
                    goal += f'soft_rock_at({ele[1]});\n'
                elif ele[0] == 'hard-rock-at':
                    goal += f'hard_rock_at({ele[1]});\n'
                elif ele[0] == 'gold-at':
                    goal += f'gold_at({ele[1]});\n'
                elif ele[0] == 'arm-empty':
                    goal += f'arm_empty;\n'
                elif ele[0] == 'holds-bomb':
                    goal += f'holds_bomb;\n'
                elif ele[0] == 'holds-laser':
                    goal += f'holds_laser;\n'
                elif ele[0] == 'holds-gold':
                    goal += f'holds_gold;\n'
                elif ele[0] == 'clear':
                    goal += f'clear({ele[1]});\n'
                elif ele[0] == 'connected':
                    goal += f'connected({ele[1]}, {ele[2]});\n'
            goal += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'goal.lp'), 'w') as f:
                f.write(goal)

            # Getting Plans
            plans = ''
            for time_stamp, ele in enumerate(plans_pddl):
                ele = str(ele)[1:-2].split()
                if ele[0] == 'move':
                    plans += f'occurs(action_move({ele[1]},{ele[2]}),{time_stamp+1}).\n'
                elif ele[0] == 'pickup-laser':
                    plans += f'occurs(action_pickup_laser({ele[1]}),{time_stamp+1}).\n'
                elif ele[0] == 'pickup-bomb':
                    plans += f'occurs(action_pick_up_bomb({ele[1]}),{time_stamp+1}).\n'
                elif ele[0] == 'putdown-laser':
                    plans += f'occurs(action_put_down_laser({ele[1]}),{time_stamp+1}).\n'
                elif ele[0] == 'detonate-bomb':
                    plans += f'occurs(action_detonate_bomb({ele[1]}, {ele[2]}),{time_stamp+1}).\n'
                elif ele[0] == 'fire-laser':
                    plans += f'occurs(action_fire_laser({ele[1]}, {ele[2]}),{time_stamp+1}).\n'
                elif ele[0] == 'pick-gold':
                    plans += f'occurs(action_pick_gold({ele[1]}),{time_stamp+1}).\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'plan.lp'), 'w') as f:
                f.write(plans)
        except Exception as e:
            pass


def generate_visitall_instances(domain):
    MIN_SIZE_GRID = 1
    MAX_SIZE_GRID = 1

    MIN_WIDTH_GRID = 1
    MAX_WIDTH_GRID = 10

    MIN_HEIGHT_GRID = 1
    MAX_HEIGHT_GRID = 10

    MIN_RATIO_CELLS = 1
    MAX_RATIO_CELLS = 10

    MIN_UNAVAIL_LOC = 1
    MAX_UNAVAIL_LOC = 10
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        size_of_square_grid = random.randint(MIN_SIZE_GRID, MAX_SIZE_GRID)
        width_rectangular_grid = random.randint(MIN_WIDTH_GRID, MAX_WIDTH_GRID)
        height_rectangular_grid = random.randint(MIN_HEIGHT_GRID, MAX_HEIGHT_GRID)
        ratio_cells_in_goal = random.randint(MIN_RATIO_CELLS, MAX_RATIO_CELLS)
        no_unavailable_loc = random.randint(MIN_UNAVAIL_LOC, MAX_UNAVAIL_LOC)
        os.system(f'Generation/{domain}/grid -n {size_of_square_grid} -x {width_rectangular_grid} -y {height_rectangular_grid} -r {ratio_cells_in_goal} -u {no_unavailable_loc} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_visitall(domain):
    pass


def generate_npuzzle_instances(domain):
    MIN_ROWS = 5    # No of cols = No of rows
    MAX_ROWS = 10
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        no_of_rows = random.randint(MIN_ROWS, MAX_ROWS)
        seed = random.randint(1,1000)
        os.system(f'Generation/{domain}/n-puzzle-generator -n {no_of_rows} -s {seed} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_npuzzle(domain):
    pass


def generate_satellite_instances(domain):
    MIN_SATELLITE = 1
    MAX_SATELLITE = 10

    MIN_INSTRUMENT = 1
    MAX_INSTRUMENT = 10

    MIN_MODES = 1
    MAX_MODES = 10

    MIN_TIME = 1
    MAX_TIME = 10

    MIN_OBSERVATION = 1
    MAX_OBSERVATION = 10
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        seed = random.randint(1,100)
        no_of_satellite = random.randint(MIN_SATELLITE, MAX_SATELLITE)
        no_of_instrument = random.randint(MIN_INSTRUMENT, MAX_INSTRUMENT)
        no_of_modes = random.randint(MIN_MODES, MAX_MODES)
        time = random.randint(MIN_TIME, MAX_TIME)
        no_of_observation = random.randint(MIN_OBSERVATION, MAX_OBSERVATION)
        os.system(f'Generation/{domain}/satgen {seed} {no_of_satellite} {no_of_instrument} {no_of_modes} {time} {no_of_observation} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_satellite(domain):
    pass


def generate_spanner_instances(domain):
    MIN_SPANNER = 5
    MAX_SPANNER = 15

    MIN_NUT = 1
    MAX_NUT = 10

    MIN_LOCATION = 1
    MAX_LOCATION = 1
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        no_of_spanners = random.randint(MIN_SPANNER, MAX_SPANNER)
        no_of_nuts = random.randint(MIN_NUT, MAX_NUT)
        no_of_locations = random.randint(MIN_LOCATION, MAX_LOCATION)
        seed = random.randint(1,100)
        os.system(f'python3 Generation/{domain}/spanner-generator.py {no_of_spanners} {no_of_nuts} {no_of_locations} --seed {seed} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_spanner(domain):
    pass


def generate_zenotravel_instances(domain):
    MIN_CITIES = 5
    MAX_CITIES = 15
    
    MIN_PLANES = 1
    MAX_PLANES = 10

    MIN_PEOPLE = 1
    MAX_PEOPLE = 10

    MIN_DISTANCE = 1
    MAX_DISTANCE = 100

    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        seed = random.randint(1,100)
        no_of_cities = random.randint(MIN_CITIES, MAX_CITIES)
        no_of_planes = random.randint(MIN_PLANES, MAX_PLANES)
        no_of_people = random.randint(MIN_PEOPLE, MAX_PEOPLE)
        distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)
        os.system(f'Generation/{domain}/ztravel {seed} {no_of_cities} {no_of_planes} {no_of_people} {distance} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_zenotravel(domain):
    pass


def generate_grippers_instances(domain):
    MIN_ROBOTS = 2
    MAX_ROBOTS = 4

    MIN_ROOMS = 3
    MAX_ROOMS = 5

    MIN_BALLS = 6
    MAX_BALLS = 8
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        no_of_robots = random.randint(MIN_ROBOTS, MAX_ROBOTS)
        no_of_rooms = random.randint(MIN_ROOMS, MAX_ROOMS)
        no_of_balls = random.randint(MIN_BALLS, MAX_BALLS)
        os.system(f'Generation/{domain}/grippers -n {no_of_robots} -r {no_of_rooms} -o {no_of_balls} > temp3.pddl')
        with open('temp3.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_grippers(domain):
    for i in range(NO_OF_EXAMPLES):
        try:
            # Checking if a plan exists for the instance or was it timed out
            plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
            with open(plan_file_path, 'r') as f:
                plans_pddl = f.readlines()

            # Creating ASP folder
            Path(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}')).mkdir(parents=True, exist_ok=True)
            instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
            instance = parse_problem(instance_file_path)

            # Getting objects
            robot = 'robot('
            gripper = 'gripper('
            room = 'room('
            object_str = 'object('
            for ele in instance.objects:
                ele = str(ele)
                if ele[:4] == 'robo':
                    robot += ele + '; '
                elif ele[:4] == 'lgri' or ele[:4] == 'rgri':
                    gripper += ele + '; '
                elif ele[:4] == 'room':
                    room += ele + '; '
                elif ele[:4] == 'ball':
                    object_str += ele + '; '
            objects = robot[:-2] + ').\n' + gripper[:-2] + ').\n' + room[:-2] + ').\n' + object_str[:-2] + ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), 'w') as f:
                f.write(objects)
            
            # Getting Initial Conditions
            initial = 'init('
            for ele in instance.init:
                ele = str(ele)[1:-1].split()
                if ele[0] == 'at-robby':
                    initial += f'at_robby({ele[1]},{ele[2]});\n'
                elif ele[0] == 'at':
                    initial += f'at({ele[1]},{ele[2]});\n'
                elif ele[0] == 'free':
                    initial += f'free({ele[1]},{ele[2]});\n'
                elif ele[0] == 'carry':
                    initial += f'carry({ele[1]},{ele[2]},{ele[3]});\n'
            initial += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'init.lp'), 'w') as f:
                f.write(initial)

            # Getting Goal State
            goal = 'goal('
            for ele in str(instance.goal).split('(')[2:]:
                ele = ele[:-2].split()
                if ele[0] == 'at-robby':
                    goal += f'at_robby({ele[1]},{ele[2]});\n'
                elif ele[0] == 'at':
                    goal += f'at({ele[1]},{ele[2]});\n'
                elif ele[0] == 'free':
                    goal += f'free({ele[1]},{ele[2]});\n'
                elif ele[0] == 'carry':
                    goal += f'carry({ele[1]},{ele[2]},{ele[3]});\n'
            goal += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'goal.lp'), 'w') as f:
                f.write(goal)

            # Getting Plans
            plans = ''
            for time_stamp, ele in enumerate(plans_pddl):
                ele = str(ele)[1:-2].split()
                if ele[0] == 'move':
                    plans += f'occurs(action_move({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'pick':
                    plans += f'occurs(action_pick({ele[1]},{ele[2]},{ele[3]},{ele[4]}),{time_stamp+1}).\n'
                elif ele[0] == 'drop':
                    plans += f'occurs(action_drop({ele[1]},{ele[2]},{ele[3]},{ele[4]}),{time_stamp+1}).\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'plan.lp'), 'w') as f:
                f.write(plans)
        except Exception as e:
            pass


def generate_logistics_instances(domain):
    MIN_AIRPLANES = 1
    MAX_AIRPLANES = 3

    MIN_CITIES = 1
    MAX_CITIES = 3

    MIN_CITY_SIZE = 2
    MAX_CITY_SIZE = 5

    MIN_PACKAGES = 4
    MAX_PACKAGES = max(6, MAX_CITIES)

    # MIN_TRUCKS = 1    # Commnted as the min would be no_of_cities
    MAX_TRUCKS = 4
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        no_of_airplanes = random.randint(MIN_AIRPLANES, MAX_AIRPLANES)
        no_of_cities = random.randint(MIN_CITIES, MAX_CITIES)
        no_of_city_size = random.randint(MIN_CITY_SIZE, MAX_CITY_SIZE)
        no_of_packages = random.randint(MIN_PACKAGES, MAX_PACKAGES)
        no_of_trucks = random.randint(no_of_cities, MAX_TRUCKS)
        os.system(f'Generation/{domain}/logistics -a {no_of_airplanes} -c {no_of_cities} -s {no_of_city_size} -p {no_of_packages} -t {no_of_trucks} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_logistics(domain):
    for i in range(NO_OF_EXAMPLES):
        try:
            # Checking if a plan exists for the instance or was it timed out
            plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
            with open(plan_file_path, 'r') as f:
                plans_pddl = f.readlines()

            # Creating ASP folder
            Path(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}')).mkdir(parents=True, exist_ok=True)
            instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
            instance = parse_problem(instance_file_path)

            # Getting objects
            airplane = 'airplane('
            truck = 'truck('
            city = 'city('
            airport = 'airport('
            package = 'package('
            for ele in instance.objects:
                ele = str(ele)
                if ele[:1] == 'a':
                    airplane += ele + '; '
                elif ele[:1] == 't':
                    truck += ele + '; '
                elif ele[:1] == 'c':
                    city += ele + '; '
                elif ele[:1] == 'l':
                    airport += ele + '; '
                elif ele[:1] == 'p':
                    package += ele + '; '
            objects = airplane[:-2] + ').\n' + truck[:-2] + ').\n' + city[:-2] + ').\n' + airport[:-2] + ').\n' + package[:-2] + ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), 'w') as f:
                f.write(objects)
            
            # Getting Initial Conditions
            initial = 'init('
            for ele in instance.init:
                ele = str(ele)[1:-1].split()
                if ele[0] == 'in-city':
                    initial += f'in_city({ele[1]},{ele[2]});\n'
                elif ele[0] == 'at':
                    initial += f'at({ele[1]},{ele[2]});\n'
                elif ele[0] == 'in':
                    initial += f'in({ele[1]},{ele[2]});\n'
            initial += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'init.lp'), 'w') as f:
                f.write(initial)

            # Getting Goal State
            goal = 'goal('
            for ele in str(instance.goal).split('(')[2:]:
                ele = ele[:-2].split()
                if ele[0] == 'in-city':
                    goal += f'in_city({ele[1]},{ele[2]});\n'
                elif ele[0] == 'at':
                    goal += f'at({ele[1]},{ele[2]});\n'
                elif ele[0] == 'in':
                    goal += f'in({ele[1]},{ele[2]});\n'
            goal += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'goal.lp'), 'w') as f:
                f.write(goal)

            # Getting Plans
            plans = ''
            for time_stamp, ele in enumerate(plans_pddl):
                ele = str(ele)[1:-2].split()
                if ele[0] == 'load-truck':
                    plans += f'occurs(action_load_truck({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'load-airplane':
                    plans += f'occurs(action_load_airplane({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'unload-truck':
                    plans += f'occurs(action_unload_truck({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'unload-airplane':
                    plans += f'occurs(action_unload_airplane({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
                elif ele[0] == 'drive-truck':
                    plans += f'occurs(action_drive_truck({ele[1]},{ele[2]},{ele[3]},{ele[4]}),{time_stamp+1}).\n'
                elif ele[0] == 'fly-airplane':
                    plans += f'occurs(action_fly_airplane({ele[1]},{ele[2]},{ele[3]}),{time_stamp+1}).\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'plan.lp'), 'w') as f:
                f.write(plans)
        except Exception as e:
            pass


def generate_miconic_instances(domain):
    MIN_FLOORS = 5
    MAX_FLOORS = 10

    MIN_PASSENGERS = 5
    MAX_PASSENGERS = 10
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        no_of_floors = random.randint(MIN_FLOORS, MAX_FLOORS)
        no_of_passengers = random.randint(MIN_PASSENGERS, MAX_PASSENGERS)
        os.system(f'Generation/{domain}/miconic -f {no_of_floors} -p {no_of_passengers} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_miconic(domain):
    for i in range(NO_OF_EXAMPLES):
        try:
            # Checking if a plan exists for the instance or was it timed out
            plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
            with open(plan_file_path, 'r') as f:
                plans_pddl = f.readlines()

            # Creating ASP folder
            Path(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}')).mkdir(parents=True, exist_ok=True)
            instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
            instance = parse_problem(instance_file_path)

            # Getting objects
            passenger = 'passenger('
            floor = 'floor('
            for ele in instance.objects:
                ele = str(ele)
                if ele[:1] == 'p':
                    passenger += ele + '; '
                elif ele[:1] == 'f':
                    floor += ele + '; '
            objects = passenger[:-2] + ').\n' + floor[:-2] + ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), 'w') as f:
                f.write(objects)
            
            # Getting Initial Conditions
            initial = 'init('
            for ele in instance.init:
                ele = str(ele)[1:-1].split()
                if ele[0] == 'origin':
                    initial += f'origin({ele[1]},{ele[2]});\n'
                elif ele[0] == 'destin':
                    initial += f'destin({ele[1]},{ele[2]});\n'
                elif ele[0] == 'above':
                    initial += f'above({ele[1]},{ele[2]});\n'
                elif ele[0] == 'boarded':
                    initial += f'boarded({ele[1]});\n'
                elif ele[0] == 'not-boarded':
                    initial += f'not_boarded({ele[1]});\n'
                elif ele[0] == 'served':
                    initial += f'served({ele[1]});\n'
                elif ele[0] == 'not-served':
                    initial += f'not_served({ele[1]});\n'
                elif ele[0] == 'lift-at':
                    initial += f'lift_at({ele[1]});\n'
            initial += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'init.lp'), 'w') as f:
                f.write(initial)

            # Getting Goal State
            goal = 'goal('
            for ele in str(instance.goal).split('(')[2:]:
                ele = ele[:-2].split()
                if ele[0] == 'origin':
                    goal += f'origin({ele[1]},{ele[2]});\n'
                elif ele[0] == 'destin':
                    goal += f'destin({ele[1]},{ele[2]});\n'
                elif ele[0] == 'above':
                    goal += f'above({ele[1]},{ele[2]});\n'
                elif ele[0] == 'boarded':
                    goal += f'boarded({ele[1]});\n'
                elif ele[0] == 'not-boarded':
                    goal += f'not_boarded({ele[1]});\n'
                elif ele[0] == 'served':
                    goal += f'served({ele[1]});\n'
                elif ele[0] == 'not-served':
                    goal += f'not_served({ele[1]});\n'
                elif ele[0] == 'lift-at':
                    goal += f'lift_at({ele[1]});\n'
            goal += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'goal.lp'), 'w') as f:
                f.write(goal)

            # Getting Plans
            plans = ''
            for time_stamp, ele in enumerate(plans_pddl):
                ele = str(ele)[1:-2].split()
                if ele[0] == 'board':
                    plans += f'occurs(action_board({ele[1]},{ele[2]}),{time_stamp+1}).\n'
                elif ele[0] == 'depart':
                    plans += f'occurs(action_depart({ele[1]},{ele[2]}),{time_stamp+1}).\n'
                elif ele[0] == 'up':
                    plans += f'occurs(action_up({ele[1]},{ele[2]}),{time_stamp+1}).\n'
                elif ele[0] == 'down':
                    plans += f'occurs(action_down({ele[1]},{ele[2]}),{time_stamp+1}).\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'plan.lp'), 'w') as f:
                f.write(plans)
        except Exception as e:
            pass


def generate_mystery_instances(domain):
    MIN_LOCATIONS = 2
    MAX_LOCATIONS = 6

    MIN_FUEL = 2
    MAX_FUEL = 4

    MIN_SPACE = 2
    MAX_SPACE = 4

    MIN_VEHICLES = 2
    MAX_VEHICLES = 5

    MIN_CARGO = 7
    MAX_CARGO = 12
    
    # Set to check for duplicate instances
    instances = set()

    while len(instances) < NO_OF_EXAMPLES:
        no_of_locations = random.randint(MIN_LOCATIONS, MAX_LOCATIONS)
        no_of_fuel = random.randint(MIN_FUEL, MAX_FUEL)
        no_of_space = random.randint(MIN_SPACE, MAX_SPACE)
        no_of_vehicles = random.randint(MIN_VEHICLES, MAX_VEHICLES)
        no_of_cargo = random.randint(MIN_CARGO, MAX_CARGO)
        seed = random.randint(1,1000)
        os.system(f'Generation/{domain}/mystery -l {no_of_locations} -f {no_of_fuel} -s {no_of_space} -v {no_of_vehicles} -c {no_of_cargo} -r {seed} > temp.pddl')
        with open('temp.pddl', 'r') as f:
            instance = f.read()
        if instance not in instances:
            instances.add(instance)
            with open(f'Domains/{domain}/Instances/instance_{len(instances)}.pddl', 'w') as f:
                f.write(instance)

def convert_mystery(domain):
    for i in range(NO_OF_EXAMPLES):
        try:
            # Checking if a plan exists for the instance or was it timed out
            plan_file_path = os.path.join('Domains', domain, 'Plans', f'plan_{i+1}.pddl')
            with open(plan_file_path, 'r') as f:
                plans_pddl = f.readlines()

            # Creating ASP folder
            Path(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}')).mkdir(parents=True, exist_ok=True)
            instance_file_path = os.path.join('Domains', domain, 'Instances', f'instance_{i+1}.pddl')
            instance = parse_problem(instance_file_path)

            # Getting objects
            fuel = 'fuel('
            space = 'space('
            location = 'location('
            vehicle = 'vehicle('
            cargo = 'cargo('
            for ele in instance.objects:
                ele = str(ele)
                if ele[:1] == 'f':
                    fuel += ele + '; '
                elif ele[:1] == 's':
                    space += ele + '; '
                elif ele[:1] == 'l':
                    location += ele + '; '
                elif ele[:1] == 'v':
                    vehicle += ele + '; '
                elif ele[:1] == 'c':
                    cargo += ele + '; '
            objects = fuel[:-2] + ').\n' + space[:-2] + ').\n' + location[:-2] + ').\n' + vehicle[:-2] + ').\n' + cargo[:-2] + ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'objects.lp'), 'w') as f:
                f.write(objects)
            
            # Getting Initial Conditions
            initial = 'init('
            for ele in instance.init:
                ele = str(ele)[1:-1].split()
                if ele[0] == 'at':
                    initial += f'at({ele[1]},{ele[2]});\n'
                elif ele[0] == 'conn':
                    initial += f'conn({ele[1]},{ele[2]});\n'
                elif ele[0] == 'has-fuel':
                    initial += f'has_fuel({ele[1]},{ele[2]});\n'
                elif ele[0] == 'fuel-neighbor':
                    initial += f'fuel_neighbor({ele[1]},{ele[2]});\n'
                elif ele[0] == 'in':
                    initial += f'in({ele[1]},{ele[2]});\n'
                elif ele[0] == 'has-space':
                    initial += f'has_space({ele[1]},{ele[2]});\n'
                elif ele[0] == 'space-neighbor':
                    initial += f'space_neighbor({ele[1]},{ele[2]});\n'
            initial += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'init.lp'), 'w') as f:
                f.write(initial)

            # Getting Goal State
            goal = 'goal('
            for ele in str(instance.goal).split('(')[2:]:
                ele = ele[:-2].split()
                if ele[0] == 'at':
                    initial += f'at({ele[1]},{ele[2]});\n'
                elif ele[0] == 'conn':
                    initial += f'conn({ele[1]},{ele[2]});\n'
                elif ele[0] == 'has-fuel':
                    initial += f'has_fuel({ele[1]},{ele[2]});\n'
                elif ele[0] == 'fuel-neighbor':
                    initial += f'fuel_neighbor({ele[1]},{ele[2]});\n'
                elif ele[0] == 'in':
                    initial += f'in({ele[1]},{ele[2]});\n'
                elif ele[0] == 'has-space':
                    initial += f'has_space({ele[1]},{ele[2]});\n'
                elif ele[0] == 'space-neighbor':
                    initial += f'space_neighbor({ele[1]},{ele[2]});\n'
            goal += ').\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'goal.lp'), 'w') as f:
                f.write(goal)

            # Getting Plans
            plans = ''
            for time_stamp, ele in enumerate(plans_pddl):
                ele = str(ele)[1:-2].split()
                if ele[0] == 'move':
                    plans += f'occurs(action_move({ele[1]},{ele[2]},{ele[3]},{ele[4]},{ele[5]}),{time_stamp+1}).\n'
                elif ele[0] == 'load':
                    plans += f'occurs(action_load({ele[1]},{ele[2]},{ele[3]},{ele[4]},{ele[5]}),{time_stamp+1}).\n'
                elif ele[0] == 'unload':
                    plans += f'occurs(action_unload({ele[1]},{ele[2]},{ele[3]},{ele[4]},{ele[5]}),{time_stamp+1}).\n'
            with open(os.path.join('Domains', domain, 'ASP', f'Instance_{i+1}', 'plan.lp'), 'w') as f:
                f.write(plans)
        except Exception as e:
            pass


def main():
    for domain in DOMAINS:
        domain_file_path = os.path.join('Domains', domain, 'domain.pddl')

        # Creating relevant directories
        Path(os.path.join('Domains', domain, 'Instances')).mkdir(parents=True, exist_ok=True)
        Path(os.path.join('Domains', domain, 'Plans')).mkdir(parents=True, exist_ok=True)

        if domain == 'Blocksworld':
            # generate_blocksworld_instances(domain)
            # generate_plans(domain, domain_file_path)
            convert_blocksworld(domain)
        elif domain == 'Depots':
            # generate_depots_instances(domain)
            # generate_plans(domain, domain_file_path)
            convert_depots(domain)
        elif domain == 'DriverLog':
            generate_driverlog_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_driverlog(domain)
        elif domain == 'GoldMiner':
            # generate_goldminer_instances(domain)
            # generate_plans(domain, domain_file_path)
            convert_goldminer(domain)
        elif domain == 'Visitall':
            generate_visitall_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_visitall(domain)
        elif domain == 'NPuzzle':
            generate_npuzzle_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_npuzzle(domain)
        elif domain == 'Satellite':
            generate_satellite_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_satellite(domain)
        elif domain == 'Spanner':
            generate_spanner_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_spanner(domain)
        elif domain == 'ZenoTravel':
            generate_zenotravel_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_zenotravel(domain)
        elif domain == 'Grippers':
            generate_grippers_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_grippers(domain)
        elif domain == 'Logistics':
            generate_logistics_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_logistics(domain)
        elif domain == 'Miconic':
            generate_miconic_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_miconic(domain)
        elif domain == 'Mystery':
            generate_mystery_instances(domain)
            generate_plans(domain, domain_file_path)
            convert_mystery(domain)


if __name__ == '__main__':
    main()