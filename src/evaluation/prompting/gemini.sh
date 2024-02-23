DOMAINS=('blocksworld' 'depots' 'driverlog' 'goldminer' 'grippers' 'logistics' 'miconic' 'mystery' 'npuzzle' 'satellite' 'spanner' 'visitall' 'zenotravel')
PROMPTS=('few_shot_4')
START_IDX=0    # Zero-index

PYTHON_CMD='python gemini.py'

for prompt in "${PROMPTS[@]}"; do
    sbatch_file_name="sbatch_gemini_${prompt}.sh"
    echo '#!/bin/bash' > $sbatch_file_name
    echo '#SBATCH -N 1' >> $sbatch_file_name
    echo '#SBATCH -c 2' >> $sbatch_file_name
    echo '#SBATCH -t 0-04:00:00' >> $sbatch_file_name
    echo '#SBATCH -p htc' >> $sbatch_file_name
    echo '#SBATCH -q public' >> $sbatch_file_name
    echo '#SBATCH --mail-type=NONE' >> $sbatch_file_name
    echo '#SBATCH --export=NONE' >> $sbatch_file_name
    echo 'module purge' >> $sbatch_file_name
    echo 'module load mamba/latest' >> $sbatch_file_name
    echo 'source activate reasoning_about_actions' >> $sbatch_file_name
    for domain in "${DOMAINS[@]}"; do
        echo "$PYTHON_CMD -d $domain -p $prompt -i $START_IDX" >> $sbatch_file_name
    done
    sbatch $sbatch_file_name
    echo "Successfully submitted ${prompt}"
    rm $sbatch_file_name
done