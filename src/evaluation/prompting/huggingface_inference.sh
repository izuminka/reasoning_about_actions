MODELS=('meta-llama/Llama-2-7b-chat-hf' 'meta-llama/Llama-2-13b-chat-hf' 
        'meta-llama/Llama-2-70b-chat-hf' 'mistralai/Mistral-7B-Instruct-v0.2'
        'google/gemma-7b-it' 'google/gemma-2b-it')
DOMAINS=('blocksworld' 'depots' 'driverlog' 'goldminer' 'grippers' 'logistics'
        'miconic' 'mystery' 'npuzzle' 'satellite' 'spanner' 'visitall' 'zenotravel')
PROMPTS=('zero_shot_data' 'few_shot_4' 'few_shot_4_cot')

INPUT_FILE='../../../data/data_files_ramifications'
OUTPUT_FILE='../../../results_ramifications'
PYTHON_CMD='python huggingface_inference.py'
INDEX=0
CONTEXT_LENGTH=4096


for model in "${MODELS[@]}"; do
    for domain in "${DOMAINS[@]}"; do
        for prompt in "${PROMPTS[@]}"; do
            model_name=$(echo ${model} | cut -d'/' -f2)
            sbatch_file_name="sbatch_${model_name}_${domain}_${prompt}.sh"
            echo '#!/bin/bash' > $sbatch_file_name
            echo '#SBATCH -N 1' >> $sbatch_file_name
            echo '#SBATCH -c 30' >> $sbatch_file_name
            echo '#SBATCH --mem 300G' >> $sbatch_file_name
            echo '#SBATCH -G a100:3' >> $sbatch_file_name
            echo '#SBATCH -C a100_80' >> $sbatch_file_name
            echo '#SBATCH -t 7-00:00:00' >> $sbatch_file_name
            echo '#SBATCH -p general' >> $sbatch_file_name
            echo '#SBATCH -q public' >> $sbatch_file_name
            echo '#SBATCH --mail-type=NONE' >> $sbatch_file_name
            echo '#SBATCH --export=NONE' >> $sbatch_file_name
            echo 'module purge' >> $sbatch_file_name
            echo 'module load mamba/latest' >> $sbatch_file_name
            echo 'source activate reasoning_about_actions' >> $sbatch_file_name
            echo "$PYTHON_CMD -m ${model} -i ${INDEX} -c ${CONTEXT_LENGTH} \
-f ${INPUT_FILE}/${prompt}/${domain}.jsonl \
-o ${OUTPUT_FILE}/${model_name}/${prompt}/${domain}.jsonl" >> $sbatch_file_name
            sbatch $sbatch_file_name
            echo "Successfully submitted ${model} ${domain} ${prompt}"
            rm $sbatch_file_name
        done
    done
done