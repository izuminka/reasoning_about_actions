#!/bin/bash

#SBATCH -N 1
#SBATCH -c 30
#SBATCH --mem 500G
#SBATCH -G a100:4
#SBATCH -C a100_80
#SBATCH -t 2-00:00:00
#SBATCH -p general
#SBATCH -q public
#SBATCH -o slurm.%j.out
#SBATCH -e slurm.%j.err
#SBATCH --mail-type=ALL
#SBATCH --export=NONE

module purge
module load mamba/latest
source activate reasoning_about_actions

python llama.py \
            -m meta-llama/Llama-2-7b \
            -f ../../../data/tuning_data \
            -o ../../../results/meta-llama/Llama-2-7b \
            -c 4096 \
            -d /scratch/dhanda/huggingface_cache \
            -t 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