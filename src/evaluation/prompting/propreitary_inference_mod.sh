MODELS=(
    'gpt-4o'
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
    'few_shot_1'
    'few_shot_5'
)

INSTANCES=(
  'Instance_1'
  'Instance_2'
  'Instance_3'
  'Instance_4'
  'Instance_5'
  'Instance_6'
  'Instance_7'
  'Instance_8'
  'Instance_9'
  'Instance_10'
)


SUBS_RAMS_EXT='without_random_sub/without_ramifications'
INPUT_FILE='../../../data/data_for_test/'$SUBS_RAMS_EXT
OUTPUT_FILE='../../../results'
#INDEX=0
#TEMPERATURE=0.0

for model in "${MODELS[@]}"; do
    for domain in "${DOMAINS[@]}"; do
        for instance in "${INSTANCES[@]}"; do
          for prompt in "${PROMPTS[@]}"; do
              sbatch_file_name="sbatch_${model}_${domain}_${prompt}_${instance}.sh"
              echo "python propreitary_inference.py \
-m ${model} \
-f ${INPUT_FILE}/${prompt}/${domain}/${instance}.jsonl \
-o ${OUTPUT_FILE}/${model}/${SUBS_RAMS_EXT}/${prompt}/${domain}/${instance}.jsonl
" >> $sbatch_file_name
            echo "Successfully submitted ${model} ${domain} ${prompt} ${instance}"
#            rm $sbatch_file_name
        done
    done
done
done