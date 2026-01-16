#!/usr/bin/env bash
set -e

lm-eval --model vllm \
    --model_args pretrained=deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B,dtype='auto',max_gen_toks=32768,trust_remote_code=True \
    --tasks minerva_math500_ur \
    --apply_chat_template \
    --gen_kwargs do_sample=true,temperature=0.6 \
    --batch_size 'auto' \
    --output_path './results/' \
    --log_samples