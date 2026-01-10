model_list=(DeepSeek-R1-Distill-Qwen-14B)
language_list=(en)
level_list=(low medium high top)

for i in ${model_list[*]}; do
    for j in ${language_list[*]}; do
        for k in ${level_list[*]}; do
            python run_eval.py --model $i --language $j --level $k
        done
    done
done

# python run_eval.py --model DeepSeek-R1-Distill-Qwen-1.5B --language en --level low 
