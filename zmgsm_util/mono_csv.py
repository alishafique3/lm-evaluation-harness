#!/usr/bin/env python3
import json
import csv
import os
import sys
from pathlib import Path
import re
from datetime import datetime

# =============================================================================
# LANGUAGE CONFIGURATION - Edit this list to include/exclude languages
# =============================================================================
ENABLED_LANGUAGES = [
    'en',      # English
    'es',      # Spanish
    'fr',      # French
    'de',      # German
    'zh',      # Chinese
    'ja',      # Japanese
    #'th',      # Thai
    #'sw',      # Swahili
    'bn',      # Bengali
    #'te',      # Telugu
    'ru',      # Russian
    # Add or remove languages as needed
]

# Set to None to include ALL languages (no filtering)
# ENABLED_LANGUAGES = None

# =============================================================================

def extract_timestamp_from_filename(filename):
    """Extract timestamp from filename to match jsonl with json files"""
    # Pattern: samples_*_TIMESTAMP.jsonl or results_TIMESTAMP.json
    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+)', filename)
    return match.group(1) if match else None

def find_matching_result_file(jsonl_file, results_dir):
    """Find the corresponding results JSON file for a given JSONL file"""
    timestamp = extract_timestamp_from_filename(jsonl_file.name)
    if not timestamp:
        return None
    
    result_filename = f"results_{timestamp}.json"
    result_path = results_dir / result_filename
    
    return result_path if result_path.exists() else None

def extract_language_from_results(result_file):
    """Extract dataset_name (language) from the results JSON file"""
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Get the first task name from results
        if 'configs' in data:
            for task_name, config in data['configs'].items():
                if 'dataset_name' in config:
                    return config['dataset_name']
        
        return None
    except Exception as e:
        print(f"Error reading result file {result_file}: {e}")
        return None

def should_include_language(language):
    """Check if the language should be included based on ENABLED_LANGUAGES"""
    if ENABLED_LANGUAGES is None:
        return True  # Include all languages
    
    if language is None:
        return False  # Exclude if language couldn't be determined
    
    return language in ENABLED_LANGUAGES

def process_jsonl_files(folder_path, model_name, task, source):
    """Process all JSONL files in the folder and create CSV"""
    results_dir = Path(folder_path)
    
    if not results_dir.exists():
        print(f"Error: Folder '{folder_path}' does not exist")
        sys.exit(1)
    
    # Find all samples JSONL files
    jsonl_files = list(results_dir.glob("samples_*.jsonl"))
    
    if not jsonl_files:
        print(f"No JSONL files found in '{folder_path}'")
        sys.exit(1)
    
    print(f"Found {len(jsonl_files)} JSONL file(s)")
    
    # Language statistics
    language_stats = {}
    skipped_languages = set()
    
    # Prepare CSV data
    csv_data = []
    
    for jsonl_file in jsonl_files:
        print(f"\nProcessing: {jsonl_file.name}")
        
        # Find matching result file
        result_file = find_matching_result_file(jsonl_file, results_dir)
        
        if result_file:
            language = extract_language_from_results(result_file)
            print(f"  Matched with: {result_file.name}")
            print(f"  Language: {language}")
            
            # Check if language should be included
            if not should_include_language(language):
                print(f"  ⚠ Skipping - Language '{language}' not in ENABLED_LANGUAGES")
                skipped_languages.add(language)
                continue
            
        else:
            print(f"  Warning: No matching result file found")
            language = None
            if not should_include_language(language):
                print(f"  ⚠ Skipping - Language could not be determined")
                continue
        
        # Read JSONL file
        file_row_count = 0
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.JSONDecoder().decode(line.strip())
                    
                    # Only process entries with flexible-extract filter
                    if data.get('filter') == 'flexible-extract':
                        # Extract completion from resps
                        completion = data.get('resps', [['']])[0][0] if data.get('resps') else ''
                        
                        csv_row = {
                            'id': data.get('doc_id', ''),
                            'model': model_name,
                            'completion': completion,
                            'task': task,
                            'source': source,
                            'filter': 'flexible-extract',
                            'exact_match': data.get('exact_match', ''),
                            'language': language if language else ''
                        }
                        csv_data.append(csv_row)
                        file_row_count += 1
                        
                        # Update language statistics
                        lang_key = language if language else 'unknown'
                        language_stats[lang_key] = language_stats.get(lang_key, 0) + 1
                
                except json.JSONDecodeError as e:
                    print(f"  Error parsing line in {jsonl_file.name}: {e}")
                    continue
        
        print(f"  ✓ Extracted {file_row_count} rows")
    
    # Print language statistics
    print("\n" + "=" * 60)
    print("LANGUAGE STATISTICS")
    print("=" * 60)
    print(f"Languages included: {', '.join(ENABLED_LANGUAGES) if ENABLED_LANGUAGES else 'ALL'}")
    print(f"\nRows per language:")
    for lang, count in sorted(language_stats.items()):
        print(f"  {lang}: {count}")
    
    if skipped_languages:
        print(f"\n⚠ Skipped languages: {', '.join(sorted(skipped_languages))}")
    
    print(f"\nTotal rows: {len(csv_data)}")
    print("=" * 60)
    
    if not csv_data:
        print("\n❌ No data found matching the criteria")
        sys.exit(1)
    
    # Generate output CSV filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lang_suffix = f"_{'_'.join(ENABLED_LANGUAGES[:3])}" if ENABLED_LANGUAGES and len(ENABLED_LANGUAGES) <= 3 else ""
    output_filename = f"{model_name.replace('/', '_')}_{task}{lang_suffix}_{timestamp}.csv"
    output_path = results_dir / output_filename
    
    # Write CSV
    fieldnames = ['id', 'model', 'completion', 'task', 'source', 'filter', 'exact_match', 'language']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"\n✓ CSV file created: {output_path}")
    print(f"✓ Total rows written: {len(csv_data)}")
    
    return output_path

def main():
    if len(sys.argv) != 5:
        print("Usage: python script.py <folder_path> <model_name> <task> <source>")
        print("\nExample:")
        print("  python script.py workspace/lm-evaluation-harness/results/deepseek-ai__DeepSeek-R1-Distill-Qwen-1.5B deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B mgsm evaluation")
        print("\nLanguage Filtering:")
        print("  Edit ENABLED_LANGUAGES list at the top of the script to select languages")
        print(f"  Currently enabled: {', '.join(ENABLED_LANGUAGES) if ENABLED_LANGUAGES else 'ALL'}")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    model_name = sys.argv[2]
    task = sys.argv[3]
    source = sys.argv[4]
    
    print("=" * 60)
    print("LM Evaluation Results to CSV Converter")
    print("=" * 60)
    print(f"Folder: {folder_path}")
    print(f"Model: {model_name}")
    print(f"Task: {task}")
    print(f"Source: {source}")
    print(f"Language Filter: {'ENABLED' if ENABLED_LANGUAGES else 'DISABLED (ALL)'}")
    if ENABLED_LANGUAGES:
        print(f"Enabled Languages: {', '.join(ENABLED_LANGUAGES)}")
    print("=" * 60)
    
    process_jsonl_files(folder_path, model_name, task, source)

if __name__ == "__main__":
    main()

# python mono_csv.py results/deepseek-ai__DeepSeek-R1-Distill-Qwen-1.5B/monolingual "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" "monolingual" "mgsm_en_cot"