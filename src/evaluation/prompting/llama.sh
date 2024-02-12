#!/bin/bash


#SBATCH -N 1
#SBATCH -c 30
#SBATCH --mem 100G
#SBATCH -G a100:1
#SBATCH -C a100_80
#SBATCH -t 0-00:15:00
#SBATCH -p general
#SBATCH -q debug
#SBATCH -o slurm.%j.out
#SBATCH -e slurm.%j.err
#SBATCH --mail-type=ALL
#SBATCH --export=NONE

module purge
module load mamba/latest

source activate reasoning_about_actions

python llama.py