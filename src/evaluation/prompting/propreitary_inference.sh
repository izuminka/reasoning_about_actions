MODELS=(
    'gemini'
    'gpt4'
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
    'zero_shot_data'
    'few_shot_4'
    'few_shot_4_cot'
)

INPUT_FILE='../../../data/data_files'
OUTPUT_FILE='../../../results'
INDEX=0
TEMPERATURE=0.0

GEMINI_API_KEY=$(cat gemini.api.key)
OPEN_AI_KEY=$(cat openai.api.key)

for model in "${MODELS[@]}"; do
    for domain in "${DOMAINS[@]}"; do
        for prompt in "${PROMPTS[@]}"; do
            echo $GEMINI_API_KEY
            model_name=$model | tr '[:upper:]' '[:lower:]'
            echo $model_name
            exit
            sbatch_file_name="sbatch_${model_name}_${domain}_${prompt}.sh"
            # Conditionally setting the API key
            if [ "$model" == "gemini" ]; then
                API_KEY=$GEMINI_API_KEY
            elif [ "$model" == "gpt4" ]; then
                API_KEY=$OPEN_AI_KEY
            fi
            
            echo '#!/bin/bash' > $sbatch_file_name
            echo '#SBATCH -N 1' >> $sbatch_file_name
            echo '#SBATCH -c 30' >> $sbatch_file_name
            echo '#SBATCH --mem 10G' >> $sbatch_file_name
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
            echo "python propreitary_inference.py \
-m ${model} \
-f ${INPUT_FILE}/${prompt}/${domain}.jsonl \
-o ${OUTPUT_FILE}/${model_name}/${prompt}/${domain}.jsonl
-k ${} \
-i ${INDEX} \
-t ${TEMPERATURE} \
" >> $sbatch_file_name

            sbatch $sbatch_file_name
            echo "Successfully submitted ${model} ${domain} ${prompt}"
            rm $sbatch_file_name
        done
    done
done