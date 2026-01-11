#!/usr/bin/env bash
set -e

# exec > >(tee b200.log) 2>&1

# deepseek-ai/DeepSeek-R1-Distill-Qwen-32B #########################################################

# level_list=(high top)
# language_list=(en)

# for level in "${level_list[@]}"; do
#   for lang in "${language_list[@]}"; do
#     python vllm_DeepSeek-R1-Distill-Qwen-32B.py \
#       --split "$level" \
#       --subset "$lang" \
#       --model deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
#       --temperature 0.6 \
#       --max_tokens 65536
#       sleep 3
#   done
# done


# inarikami/DeepSeek-R1-Distill-Qwen-32B-AWQ #########################################################

level_list=(low medium high top)
language_list=(en)

for level in "${level_list[@]}"; do
  for lang in "${language_list[@]}"; do
    python vllm_DeepSeek-R1-Distill-Qwen-32B-AWQ.py \
      --split "$level" \
      --subset "$lang" \
      --model inarikami/DeepSeek-R1-Distill-Qwen-32B-AWQ \
      --temperature 0.6 \
      --max_tokens 65536
      sleep 3
  done
done