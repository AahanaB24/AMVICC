import argparse
import torch
import os
import json
from tqdm import tqdm
import shortuuid
import base64

from PIL import Image
import math
import pandas as pd
from huggingface_hub import InferenceClient

def split_list(lst, n):
    """Split a list into n (roughly) equal-sized chunks"""
    chunk_size = math.ceil(len(lst) / n)
    return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]

def get_chunk(lst, n, k):
    chunks = split_list(lst, n)
    return chunks[k]

def encode_image(image_path):
    """Encode image to base64 for OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def eval_model(args, model_type):
    local_model = "local"
    api_model = "api"
    if model_type == "hf": 

        benchmark_dir = os.path.join(args.directory, 'Questions.csv')
        df = pd.read_csv(benchmark_dir)
        
        answers_file = os.path.expanduser(args.answers_file)
        if os.path.dirname(answers_file):
            os.makedirs(os.path.dirname(answers_file), exist_ok=True)

        ans_file = open(answers_file, "w")

        for index, row in tqdm(df.iterrows(), total=len(df)):
            cur_prompt = row['Question'] + " " + row['Options']

            photo_id = index + 1
            image_path = os.path.join(args.directory, 'MMVP Images', f"{photo_id}.jpg")

            image_bytes = None
            if os.path.exists(image_path): 
                with open(image_path, "rb") as img_file: 
                    image_bytes = img_file.read()

            try:
                print(cur_prompt)
                image_b64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else None
                response = hf_client.imagetext_to_text(
                    model=args.model_name, 
                    image=[image_b64], 
                    question=cur_prompt,
                )
                generated_text = response[0]['generated_text']
                ans_id = shortuuid.uuid()
                ans_file.write(json.dumps({
                    "question_id": photo_id,
                    "prompt": cur_prompt,
                    "answer": row["Correct Answer"],
                    "response": response,
                    "answer_id": ans_id,
                    "model_id": args.model_name,
                }) + "\n")
                ans_file.flush()

            except Exception as e: 
                print(f"Error procession question {photo_id}: {e}")
                continue
        
        ans_file.close()
    
    elif model_type == "api":
        
        benchmark_dir = os.path.join(args.directory, 'Questions.csv')
        df = pd.read_csv(benchmark_dir)
        
        answers_file = os.path.expanduser(args.answers_file)
        if os.path.dirname(answers_file):
            os.makedirs(os.path.dirname(answers_file), exist_ok=True)
        
        with open(answers_file, 'w') as ans_file:
            for index, row in tqdm(df.iterrows(), total=len(df)):
                cur_prompt = row['Question'] + " " + row['Options']
                photo_id = index + 1
                image_path = os.path.join(args.directory, 'MMVP Images', f"{photo_id}.jpg")
                
                try:
                    completion = hf_client.chat.completions.create(
                        model=args.model_name,
                        messages=[
                            {
                                "role": "user", 
                                "content": [
                                    {
                                        "type": "text",
                                        "text": cur_prompt,
                                    },
                                    {
                                        "type": "image",
                                        "image": image_path,
                                    }
                                ]
                            }
                        ]
                    )
                    
                    outputs= completion.choices[0].message
                    
                    ans_id = shortuuid.uuid()
                    ans_file.write(json.dumps({
                        "question_id": photo_id,
                        "prompt": cur_prompt,
                        "answer": row["Correct Answer"],
                        "response": outputs,
                        "answer_id": ans_id,
                        "model_id": args.model_name,
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
    parser.add_argument("--api-key", type=str, default="error", required=True)
    parser.add_argument("--model-name", type=str, default=None, required=True)
    parser.add_argument("--model", type=str, default="gpt-4o")
    parser.add_argument("--model-type", type=str, default="hf", choices=["local", "api", "hf"], required=True)

    args = parser.parse_args()

    hf_client = InferenceClient(
        provider="hf-inference",
        model=args.model_name,
        token=args.api_key,
    )
    eval_model(args, args.model_type)
