
# ActionReasoningBench

Data and models are available at [gdrive](https://drive.google.com/drive/folders/1v8yhRmd2IhLLNpiJhoh4fyiaKEcaI9_B?usp=sharing)

## Directory Structure 
- **init_goal_state_generation/**: PDDL instances are created, plan is computed and validated. Instances are automatically converted to ASP
- **states_actions_generation/**: Given ASP domain, instance and plan `jsonl` file is computed with states and actions branching from the given plan
- **questions_construction/**: Contains ASP -> NL conversions for each domain and question generation scripts.
- **evaluation/**: Contains scripts for creates prompts, evaluates models on prompting and fine-tuning
- **analysis/**: Contains scripts and tools for analyzing the evaluated models
- **tests/**: Includes unit tests and other testing scripts to ensure the functionality and integrity of the pipeline.
- **other/**: Contains miscellaneous scripts and resources that do not fit into the other specific categories.

## Files
- **common.py**: Contains common functions and utilities used across different modules in the pipeline.
- **requirements.txt**: Lists the dependencies required to run the project.

## Getting Started

To get started with this project, follow the steps below:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/izuminka/reasoning_about_actions
   cd reasoning_about_actions
   ```
2. **Install the dependencies**:
   ```bash
   conda create --name action_reasoning python=3.9
   conda activate action_reasoning
   pip install -r requirements.txt
   ```
3. **Download Data/Models**:
   
   Data and models are available at [gdrive](https://drive.google.com/drive/folders/1v8yhRmd2IhLLNpiJhoh4fyiaKEcaI9_B?usp=sharing)
