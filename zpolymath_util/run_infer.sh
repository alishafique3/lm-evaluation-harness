#!/usr/bin/env bash
set -e

level_list=(medium high top)
language_list=(en es fr ja ru zh)

for level in "${level_list[@]}"; do
  for lang in "${language_list[@]}"; do
    python vllm_run.py \
      --split "$level" \
      --subset "$lang" \
      --model deepseek-ai/DeepSeek-R1-Distill-Qwen-14B
      sleep 3
  done
done



# python vllm_run.py --subset en --split low --model deepseek-ai/DeepSeek-R1-Distill-Qwen-14B