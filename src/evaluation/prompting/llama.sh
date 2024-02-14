DOMAINS=('blocksworld' 'depots' 'driverlog' 'goldminer' 'grippers' 'logistics' 'miconic' 'mystery' 'npuzzle' 'satellite' 'spanner' 'visitall' 'zenotravel')
PROMPTS=('zero_shot' 'few_shot' 'few_shot_cot')

PYTHON_CMD='python llama.py'

for domain in "${DOMAINS[@]}"; do
    for prompt in "${PROMPTS[@]}"; do
        sbatch_file_name="sbatch_llama_${domain}_${prompt}.sh"
        echo '#!/bin/bash' > $sbatch_file_name
        echo '#SBATCH -N 1' >> $sbatch_file_name
        echo '#SBATCH -c 30' >> $sbatch_file_name
        echo '#SBATCH --mem 100G' >> $sbatch_file_name
        echo '#SBATCH -G a100:1' >> $sbatch_file_name
        echo '#SBATCH -C a100_80' >> $sbatch_file_name
        echo '#SBATCH -t 0-04:00:00' >> $sbatch_file_name
        echo '#SBATCH -p htc' >> $sbatch_file_name
        echo '#SBATCH -q public' >> $sbatch_file_name
        echo '#SBATCH --mail-type=NONE' >> $sbatch_file_name
        echo '#SBATCH --export=NONE' >> $sbatch_file_name
        echo 'module purge' >> $sbatch_file_name
        echo 'module load mamba/latest' >> $sbatch_file_name
        echo 'source activate reasoning_about_actions' >> $sbatch_file_name
        echo "$PYTHON_CMD -d $domain -p $prompt" >> $sbatch_file_name
        sbatch $sbatch_file_name
        echo "Successfully submitted ${domain} ${prompt}"
        rm $sbatch_file_name
    done
done