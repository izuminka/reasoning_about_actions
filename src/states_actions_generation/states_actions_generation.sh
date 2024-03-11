#DOMAINS=('blocksworld' 'depots' 'driverlog' 'goldminer' 'grippers' 'logistics' 'miconic' 'mystery' 'npuzzle' 'satellite' 'spanner' 'visitall' 'zenotravel')
DOMAINS=('zenotravel')
#INSTANCES=('Instance_1' 'Instance_2' 'Instance_3' 'Instance_4' 'Instance_5' 'Instance_6' 'Instance_7' 'Instance_8' 'Instance_9' 'Instance_10')
INSTANCES=('Instance_3')

PYTHON_CMD='python states_actions_generation.py'

for domain in "${DOMAINS[@]}"; do
    for instance in "${INSTANCES[@]}"; do
        sbatch_file_name="sbatch_${domain}_${instance}.sh"
        echo '#!/bin/bash' > $sbatch_file_name
        echo '#SBATCH -N 1' >> $sbatch_file_name
        echo '#SBATCH -c 1' >> $sbatch_file_name
        echo '#SBATCH -t 1-16:00:00' >> $sbatch_file_name
        echo '#SBATCH -p general' >> $sbatch_file_name
        echo '#SBATCH -q prerelease' >> $sbatch_file_name
        echo '#SBATCH --mail-type=NONE' >> $sbatch_file_name
        echo '#SBATCH --export=NONE' >> $sbatch_file_name
        echo 'module purge' >> $sbatch_file_name
        echo 'module load mamba/latest' >> $sbatch_file_name
        echo 'source activate reasoning_about_actions' >> $sbatch_file_name
        echo "$PYTHON_CMD -d $domain -i $instance" >> $sbatch_file_name
        sbatch $sbatch_file_name
        echo "Successfully submitted ${domain} ${instance}"
        rm $sbatch_file_name
    done
done
