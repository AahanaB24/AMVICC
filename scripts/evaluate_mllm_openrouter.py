import argparse
import torch
import os
import json
from tqdm import tqdm
import shortuuid
import base64
import requests

from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates, SeparatorStyle
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria

from PIL import Image
import math
import pandas as pd

def split_list(lst, n):
    """Split a list into n (roughly) equal-sized chunks"""
    chunk_size = math.ceil(len(lst) / n)
    return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]

def get_chunk(lst, n, k):
    chunks = split_list(lst, n)
    return chunks[k]

def encode_image(image_path):
    """Encode image to base64 for API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_openrouter_api(prompt, image_path, api_key, model_name, temperature=0.2, max_tokens=1024):
    """Call OpenRouter API with text and image"""
    
    base64_image = encode_image(image_path)
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return "No response generated"
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return f"Error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"Error: {str(e)}"

def eval_model(args, model_type):
    local_model = "local"
    api_model = "api"
    
    if model_type == local_model:
        disable_torch_init()
        model_path = os.path.expanduser(args.model_path)
        model_name = get_model_name_from_path(model_path)

        tokenizer, model, image_processor, context_len = load_pretrained_model(model_path, args.model_base, model_name)
        
        benchmark_dir = os.path.join(args.directory, 'Questions.csv')
        df = pd.read_csv(benchmark_dir)
        
        answers_file = os.path.expanduser(args.answers_file)
        if os.path.dirname(answers_file):
            os.makedirs(os.path.dirname(answers_file), exist_ok=True)

        ans_file = open(answers_file, "w")

        for index, row in tqdm(df.iterrows()):
            cur_prompt = row['Question'] + " " + row['Options']
            qs = cur_prompt

            if model.config.mm_use_im_start_end:
                qs = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n' + qs
            else:
                qs = DEFAULT_IMAGE_TOKEN + '\n' + qs

            conv = conv_templates[args.conv_mode].copy()
            conv.append_message(conv.roles[0], qs)
            conv.append_message(conv.roles[1], None)
            prompt = conv.get_prompt()

            photo_id = row['Index']
            image_path = os.path.join(args.directory, 'MMVP Images', f"{photo_id}.jpg")
            image = Image.open(image_path)

            input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).cuda()
            image_tensor = image_processor.preprocess(image, return_tensors='pt')['pixel_values'][0]

            stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
            keywords = [stop_str]
            stopping_criteria = KeywordsStoppingCriteria(keywords, tokenizer, input_ids)

            with torch.inference_mode():
                output_ids = model.generate(
                    input_ids,
                    images=image_tensor.unsqueeze(0).half().cuda(),
                    do_sample=True,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    num_beams=args.num_beams,
                    max_new_tokens=1024,
                    use_cache=True)

            input_token_len = input_ids.shape[1]
            n_diff_input_output = (input_ids != output_ids[:, :input_token_len]).sum().item()
            if n_diff_input_output > 0:
                print(f'[Warning] {n_diff_input_output} output_ids are not the same as the input_ids')
            
            outputs = tokenizer.batch_decode(output_ids[:, input_token_len:], skip_special_tokens=True)[0]
            outputs = outputs.strip()
            if outputs.endswith(stop_str):
                outputs = outputs[:-len(stop_str)]
            outputs = outputs.strip()

            ans_id = shortuuid.uuid()
            ans_file.write(json.dumps({
                "question_id": photo_id,
                "category": row["Category"],
                "prompt": cur_prompt,
                "answer": row["Correct Answer"],
                "response": outputs,
                "answer_id": ans_id,
                "model_id": model_name,
            }) + "\n")
            ans_file.flush()
        
        ans_file.close()

    elif model_type == api_model:
        
        benchmark_dir = os.path.join(args.directory, 'Questions.csv')
        df = pd.read_csv(benchmark_dir)
        
        answers_file = os.path.expanduser(args.answers_file)
        if os.path.dirname(answers_file):
            os.makedirs(os.path.dirname(answers_file), exist_ok=True)
        
        with open(answers_file, 'w') as ans_file:
            for index, row in tqdm(df.iterrows(), total=len(df)):
                cur_prompt = row['Question'] + " " + row['Options']
                photo_id = row['Index']
                image_path = os.path.join(args.directory, 'MMVP Images', f"{photo_id}.jpg")
                
                try:
                    outputs = call_openrouter_api(
                        prompt=cur_prompt,
                        image_path=image_path,
                        api_key=args.api_key,
                        model_name=args.model,
                        temperature=args.temperature,
                        max_tokens=1024
                    )
                    
                    ans_id = shortuuid.uuid()
                    ans_file.write(json.dumps({
                        "question_id": photo_id,
                        "category": row["Category"],
                        "prompt": cur_prompt,
                        "answer": row["Correct Answer"],
                        "response": outputs,
                        "answer_id": ans_id,
                        "model_id": args.model,
                    }) + "\n")
                    ans_file.flush()
                    
                except Exception as e:
                    print(f"Error processing question {photo_id}: {e}")
                    continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="facebook/opt-350m")
    parser.add_argument("--model-base", type=str, default=None)
    parser.add_argument("--directory", type=str, default="")
    parser.add_argument("--question-file", type=str, default="tables/question.jsonl")
    parser.add_argument("--answers-file", type=str, default="answer.jsonl")
    parser.add_argument("--conv-mode", type=str, default="llava_v1")
    parser.add_argument("--num-chunks", type=int, default=1)
    parser.add_argument("--chunk-idx", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p", type=float, default=None)
    parser.add_argument("--num_beams", type=int, default=1)
    parser.add_argument("--api-key", type=str, required=True)
    parser.add_argument("--model-name", type=str, default=None)
    parser.add_argument("--model", type=str, default=None, required=True)
    parser.add_argument("--model-type", type=str, default="local", choices=["local", "api"])

    args = parser.parse_args()

    eval_model(args, args.model_type)
