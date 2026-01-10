#!/usr/bin/env bash
set -e

# deepseek-ai/DeepSeek-R1-Distill-Qwen-14B

level_list=(low medium high top)
language_list=(en)

for level in "${level_list[@]}"; do
  for lang in "${language_list[@]}"; do
    python vllm_DeepSeek-R1-Distill-Qwen-14B.py \
      --split "$level" \
      --subset "$lang" \
      --model deepseek-ai/DeepSeek-R1-Distill-Qwen-14B \
      --limit 50
      sleep 3
  done
done



# python vllm_DeepSeek-R1-Distill-Qwen-14B.py --subset en --split low --model deepseek-ai/DeepSeek-R1-Distill-Qwen-14B