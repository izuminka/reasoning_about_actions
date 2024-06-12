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
RANDOM_SUBSTITUTIONS=(
    true
    false
)
RAMIFICATIONS=(
    true
    false
)
N_SHOT=(
    1
    3
    5
)

for domain in "${DOMAINS[@]}"; do
    for substitutions in "${RANDOM_SUBSTITUTIONS[@]}"; do
        for ramifications in "${RAMIFICATIONS[@]}"; do
            for shot in "${N_SHOT[@]}"; do
                sbatch_file_name="sbatch_fewshot__${domain}__${shot}__${substitutions}__${ramifications}.sh"
                
                echo '#!/bin/bash' > $sbatch_file_name
                echo '#SBATCH -N 1' >> $sbatch_file_name
                echo '#SBATCH -c 2' >> $sbatch_file_name
                echo '#SBATCH -t 0-04:00:00' >> $sbatch_file_name
                echo '#SBATCH -p htc' >> $sbatch_file_name
                echo '#SBATCH -q public' >> $sbatch_file_name
                echo '#SBATCH --output=NONE' >> $sbatch_file_name
                echo '#SBATCH --error=NONE' >> $sbatch_file_name
                echo '#SBATCH --mail-type=NONE' >> $sbatch_file_name
                echo '#SBATCH --export=NONE' >> $sbatch_file_name
                echo 'module purge' >> $sbatch_file_name
                echo 'module load mamba/latest' >> $sbatch_file_name
                echo 'source activate reasoning_about_actions' >> $sbatch_file_name
                echo "python prompting_stencils.py \
--domain ${domain} \
--random ${substitutions} \
--ramification ${ramifications} \
--n_shot ${shot} \
" >> $sbatch_file_name

                sbatch $sbatch_file_name
                echo "Successfully submitted ${domain} ${shot} ${substitutions} ${ramifications}"
                rm $sbatch_file_name
            done
        done
    done
done