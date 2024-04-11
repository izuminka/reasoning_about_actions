#!/bin/bash

#SBATCH -N 1
#SBATCH -c 30
#SBATCH --mem 400G
#SBATCH -G a100:3
#SBATCH -C a100_80
#SBATCH -t 7-00:00:00
#SBATCH -p general
#SBATCH -q public
#SBATCH -o slurm.%j.out
#SBATCH -e slurm.%j.err
#SBATCH --mail-type=ALL
#SBATCH --export=NONE

module purge
module load mamba/latest
source activate reasoning_about_actions

TOKEN=$(cat ../prompting/huggingface.token.key)

# python llama.py \
accelerate launch llama.py \
            -m meta-llama/Llama-2-7b-hf \
            -f ../../../data/tuning_data \
            -o /scratch/dhanda/reasoning_about_actions/finetuned_llama_2 \
            -c 4096 \
            -d /scratch/dhanda/huggingface_cache \
            -t $TOKEN