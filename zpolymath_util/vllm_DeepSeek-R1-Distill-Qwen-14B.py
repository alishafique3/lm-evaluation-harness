import argparse
import json
from pathlib import Path
from datasets import load_dataset
from vllm import LLM
from vllm.sampling_params import SamplingParams


def parse_response(raw_response):
    """Split response into thinking and answer parts based on </think> tag."""
    # List of special tokens to remove
    special_tokens = [
        "<think>", "</think>",
        "<|im_start|>", "<|im_end|>",
        "<|start_header_id|>", "<|end_header_id|>",
        "<|eot_id|>", "<|begin_of_text|>", "<|end_of_text|>",
        "<s>", "</s>",
        "<bos>", "<eos>",
        "<pad>", "<unk>",
    ]
    
    if "</think>" in raw_response:
        parts = raw_response.split("</think>", 1)
        thinking = parts[0].strip()
        answer = parts[1].strip()
    else:
        thinking = ""
        answer = raw_response.strip()
    
    # Remove special tokens
    for token in special_tokens:
        thinking = thinking.replace(token, "")
        answer = answer.replace(token, "")
    
    return thinking.strip(), answer.strip()


def main():
    parser = argparse.ArgumentParser(description="Run PolyMath dataset through vLLM")
    parser.add_argument("--subset", type=str, required=True, help="Language abbreviation (e.g., en, ar)")
    parser.add_argument("--split", type=str, required=True, choices=["top", "high", "medium", "low"], 
                        help="Dataset split")
    parser.add_argument("--model", type=str, required=True, 
                        help="Model name (e.g., deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of examples to process")
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset: Qwen/PolyMath, subset={args.subset}, split={args.split}")
    dataset = load_dataset("Qwen/PolyMath", args.subset, split=args.split)
    
    if args.limit:
        dataset = dataset.select(range(min(args.limit, len(dataset))))
        print(f"Processing first {len(dataset)} examples")
    
    # Initialize vLLM
    print(f"Loading model: {args.model}")
    llm = LLM(model=args.model)
    sampling_params = SamplingParams(max_tokens=131072, temperature=0.6)
    
    # Prepare conversations
    conversations = []
    for example in dataset:
        conversation = [
            {
                "role": "user",
                "content": f"{example['question']}\nPlease reason step by step, and put your final answer within \\boxed{{}}",
            }
        ]
        conversations.append(conversation)
    
    # Generate responses
    print("Generating responses...")
    outputs = llm.chat(conversations, sampling_params=sampling_params)
    
    # Prepare output directory
    model_name = args.model.split("/")[-1]
    output_dir = Path("output") / model_name / args.split
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{args.subset}.jsonl"
    
    # Save results
    print(f"Saving results to {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, (example, output) in enumerate(zip(dataset, outputs)):
            raw_response = output.outputs[0].text
            thinking_pred, answer_pred = parse_response(raw_response)
            
            result = {
                "idx": idx,
                "question": example["question"],
                "answer": example["answer"],
                "raw_response": raw_response,
                "thinking_pred": thinking_pred,
                "answer_pred": answer_pred
            }
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    
    print(f"Done! Processed {len(outputs)} examples")


if __name__ == "__main__":
    main()


# python vllm_run.py --subset en --split low --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --limit 10