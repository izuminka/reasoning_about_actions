MODELS=(
    # 'meta-llama/Llama-2-7b-chat-hf'
    # 'meta-llama/Llama-2-13b-chat-hf' 
    # 'meta-llama/Llama-2-70b-chat-hf'
    'mistralai/Mistral-7B-Instruct-v0.2'
    'google/gemma-7b-it'
    'google/gemma-2b-it'
    # 'allenai/OLMo-7B-Instruct'    # pip install ai2-olmo
)
DOMAINS=(
    'blocksworld'
    'depots'
    'driverlog'
    'goldminer'
    'grippers'
    'logistics'
    'miconic'
    'mystery'
    'npuzzle'
    'satellite'
    'spanner'
    'visitall'
    'zenotravel'
)
PROMPTS=(
    # 'zero_shot_data'
    'few_shot_1'
    'few_shot_3'
    'few_shot_5'
    # 'few_shot_5_cot'
)
RANDOM_SUBSTITUTIONS=(
    'with_random_sub'
    'without_random_sub'
)
RAMIFICATIONS=(
    'with_ramifications'
    'without_ramifications'
)

# INPUT_FILE='../../../data/data_for_evaluation'
INPUT_FILE='/scratch/dhanda/reasoning_about_actions/data/data_for_evaluation'
OUTPUT_FILE='../../../results'
HUGGINGFACE_CACHE_DIR='/scratch/dhanda/huggingface_cache'
HUGGINGFACE_TOKEN=$(cat huggingface.token.key)
INDEX=0


for model in "${MODELS[@]}"; do
    if [ "$model" == "mistralai/Mistral-7B-Instruct-v0.2" ]; then
        CONTEXT_LENGTH=32768
    elif [ "$model" == "google/gemma-7b-it" ] || [ "$model" == "google/gemma-2b-it" ]; then
        CONTEXT_LENGTH=8192
    else
        CONTEXT_LENGTH=4096
    fi
    for domain in "${DOMAINS[@]}"; do
        for prompt in "${PROMPTS[@]}"; do
            for substitutions in "${RANDOM_SUBSTITUTIONS[@]}"; do
                for ramifications in "${RAMIFICATIONS[@]}"; do
                    for instance in {1..10}; do
                        model_name=$(echo ${model} | cut -d'/' -f2)
                        sbatch_file_name="sbatch__${model_name}__subs_${substitutions}__ram_${ramifications}__${prompt}__${domain}_inst_${instance}.sh"
                        
                        echo '#!/bin/bash' > $sbatch_file_name
                        echo '#SBATCH -N 1' >> $sbatch_file_name
                        echo '#SBATCH -c 30' >> $sbatch_file_name
                        echo '#SBATCH --mem 100G' >> $sbatch_file_name
                        echo '#SBATCH -G a100:1' >> $sbatch_file_name
                        echo '#SBATCH -C a100_80' >> $sbatch_file_name
                        echo '#SBATCH -t 7-00:00:00' >> $sbatch_file_name
                        echo '#SBATCH -p general' >> $sbatch_file_name
                        echo '#SBATCH -q public' >> $sbatch_file_name
                        echo '#SBATCH --output=NONE' >> $sbatch_file_name
                        echo '#SBATCH --error=NONE' >> $sbatch_file_name
                        echo '#SBATCH --mail-type=NONE' >> $sbatch_file_name
                        echo '#SBATCH --export=NONE' >> $sbatch_file_name
                        echo 'module purge' >> $sbatch_file_name
                        echo 'module load mamba/latest' >> $sbatch_file_name
                        echo 'source activate reasoning_about_actions' >> $sbatch_file_name
                        echo "python huggingface_inference.py \
-m ${model} \
-f ${INPUT_FILE}/${substitutions}/${ramifications}/${prompt}/${domain}/Instance_${instance}.jsonl \
-o ${OUTPUT_FILE}/${model_name}/${substitutions}/${ramifications}/${prompt}/${domain}/Instance_${instance}.jsonl \
-c ${CONTEXT_LENGTH} \
-d ${HUGGINGFACE_CACHE_DIR} \
-t ${HUGGINGFACE_TOKEN} \
-i ${INDEX} \
" >> $sbatch_file_name
                        
                        sbatch $sbatch_file_name
                        echo "Successfully submitted ${model} ${domain} ${prompt}"
                        rm $sbatch_file_name
                    done
                done
            done
        done
    done
done
