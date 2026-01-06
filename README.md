# AMVICC: A Novel Benchmark for Cross-Modal Failure Mode Profiling for VLMs and IGMs
## Contents:
1. [Abstract](#abstract)
2. [Getting Started](#start)
3. [Benchmark](#benchmarks)
4. [Results](#results)
5. [Acknowledgement](#acknowledgement)

## Abstract <a name="abstract"></a>

We investigated visual reasoning limitations of both multimodal large language models (MLLMs) and image generation models (IGMs) by creating a novel benchmark to systematically compare failure modes across image-to-text and text-to-image tasks, enabling cross-modal evaluation of visual understanding. Despite rapid growth in machine learning, vision language models (VLMs) still fail to understand or generate basic visual concepts like object orientation, quantity, or spatial relationships—highlighting gaps in elementary visual reasoning. By adapting MMVP benchmark questions into explicit and implicit prompts, we create AMVICC, a novel benchmark for profiling failure modes across various modalities. After testing 11 MLLMs and 3 IGMs across nine visual reasoning categories, our results show that failure modes are often shared across models and modalities, but certain failures are model-specific and modality-specific can be potentially attributed to various factors. IGMs consistently struggled to manipulate specific visual components in response to prompts, especially in explicit, suggesting poor control over fine-grained visual attributes. Our findings apply most directly to the evaluation of existing state-of-the-art models on structured visual reasoning tasks. This work lays a foundation for future cross-modal alignment studies, offering a framework to probe whether generation and interpretation failures stem from shared limitations—guiding future improvements in unified vision-language modeling.
## Getting Started <a name="start"></a>

### Installation
```
git clone -b branch-name https://github.com/AahanaB24/amvicc-img.git AMVICC
```

### Run on VLM Model with Modified MMVP
```
cd YOUR_PROJECT_FOLDER
mkdir -p result
python scripts/evaluate_mllm_general.py --model-type "api" --model "gpt-4o" --directory "./MMVP_dataset" --answers-file "results/gpt4o_evaluation.jsonl" --temperature 0.2 --api-key "the-key-here" 
cd results
cat gpt4o_evaluation.jsonl | more
type gpt4o_evaluation.jsonl | more
[to view more, press the space bar]
Saved in gpt4o_evaluation.jsonl
evaluate_mllm_gemini.py
```
The above code is only for gpt4o evaluation, and the code would have to be subsequently modified in order to work for various other models depending on the provider and cost. You also must first download the MMVP dataset prior to running the code. Please refer to the MMVP README: [https://github.com/tsb0601/MMVP](url)
### Run on IGM Model with AMVICC
```
cd YOUR_PROJECT_FOLDER
cd scripts
python image_gen_stability.py --stability-api-key "api_key"| for Stable Diffusion 
python image_gen_google.py --api-key "api_key" | for Google Gemini Flash
python image_gen_dalle3.py --dalle3-api-key "api_key" | for Dalle 3
```
The above code is specific to each model outlined but can be adjusted to work for more models within the code. To rerun ablation tests, change the CSV file paths within the code or as an argument (--csv-path "path") to use a different set of prompts. 


## Benchmarks <a name="benchmark"></a>
<img width="559" height="446" alt="image" src="https://github.com/user-attachments/assets/3634d3ba-f3e8-4d2b-a40a-405213be20e1" />

### AMVICC Bechmark
Our AMVICC Benchmark is available [here](scripts/dataset.csv). It is specially crafted to measure **multimodal LLM's** visual capability via VQA and **image generation model's** visual capabilities through image generation. 
The benchmark is seperated into a CSV file containing the corresponding questions, answer choices, and implicit and explicit containing all 300 testing images and an annotation csv file with questions and correct answers. The format of the data is:
```
├── Dataset CSV
│   ├── id, category, question, answer_choices, answer, prompt_im, prompt_ex, expected
│   ├── 1,sc,Are the butterfly's wings closer to being open or closed?,(a) Open (b) Closed,(a),generate a butterfly in a natural outdoor setting,generate a butterfly flying in a sunny meadow with wings fully spread
│   ├── 2,sc,Are the butterfly's wings closer to being open or closed?,(a) Open (b) Closed,(b),generate a butterfly in a natural outdoor setting,generate a butterfly resting on a flower with wings folded closed
│   ├── ...
│   └── 300,sc,How would you describe the background of the image?,(a) Light shining through the clouds from the upper right corner (b) Most of the background is dark and cloudy,(b),Generate an image of the background of a city with a skyline,Generate an image of the background of a city with a skyline and most of background dark and cloudy
└── 
```
## Results for Initial Tests <a name="results"></a> 
## Example for VLM Produced Results
```
{
      "question_id": 4,
      "category": "sh",
      "question": "Is the flame of the match more round or thin? (a) Round (b) Thin",
      "correct_answer": "(b)",
      "model_response": "Based on the image, the flame of the match is more **(a) Round**. \n\nWhile it has a pointed tip, the overall shape of the visible flame is wider and more rounded than thin. It's elongated, but not simply a thin line.",
      "is_correct": false,
      "gpt_grade": "no"
    },
    {
      "question_id": 5,
      "category": "od",
      "question": "Is the dog facing left or right from the camera's perspective? (a) Left (b) Right",
      "correct_answer": "(a)",
      "model_response": "** (b) Right**\n\nThe dog is facing towards the right side of the image from the camera's perspective. You can tell by the direction its head and nose are pointed.",
      "is_correct": false,
      "gpt_grade": "no"
    },
    {
      "question_id": 6,
      "category": "od",
      "question": "Is the dog facing left or right from the camera's perspective? (a) Left (b) Right",
      "correct_answer": "(b)",
      "model_response": "(b) Right\n\nThe dog is facing towards the right side of the image from the camera's perspective. You can tell by the direction its head and eyes are looking.",
      "is_correct": true,
      "gpt_grade": "yes"
    },
```
## Image Generation Models
```
Dalle3 Results
Dalle 3
  Categories      I Im      I Ex      P Im      P Ex
0         sc  0.981481  0.777778  0.962963  0.555556
6         sh  1.000000  0.900000  1.000000  0.800000
1         od  0.966667  0.666667  0.933333  0.400000
7         tx  1.000000  0.714286  1.000000  0.428571
4         qc  0.916667  0.666667  0.916667  0.500000
3         pr  1.000000  0.750000  1.000000  0.562500
2         pf  0.985714  0.757143  0.971429  0.571429
8         vp  1.000000  0.833333  1.000000  0.666667
0         ca  0.928571  0.892857  0.928571  0.857143

Google Flash Results
Google Flash
  Categories      I Im      I Ex      P Im      P Ex
0         ca  1.000000  0.964286  1.000000  0.928571
1         od  0.966667  0.966667  0.933333  0.933333
2         pf  0.971429  0.857143  0.971429  0.742857
3         pr  0.968750  0.906250  0.937500  0.812500
4         qc  1.000000  0.750000  1.000000  0.666667
5         sc  1.000000  0.944444  1.000000  0.888889
6         sh  1.000000  0.966667  1.000000  0.933333
7         tx  1.000000  0.785714  1.000000  0.571429
8         vp  1.000000  1.000000  1.000000  1.000000
Stable Diffusion Results
Stable Diffusion
  Categories      I Im      I Ex      P Im      P Ex
0         ca  0.964286  0.785714  0.928571  0.642857
1         od  0.866667  0.566667  0.800000  0.200000
2         pf  0.928571  0.671429  0.885714  0.400000
3         pr  0.875000  0.437500  0.875000  0.125000
4         qc  0.916667  0.500000  0.916667  0.250000
5         sc  0.962963  0.555556  0.925926  0.259259
6         sh  0.900000  0.733333  0.866667  0.466667
7         tx  0.857143  0.428571  0.857143  0.142857
8         vp  0.944444  0.777778  0.888889  0.666667
```

## Citation <a name="citation"></a>
Please consider citing our paper if you find this project helpful for your research:

```bibtex
@inproceedings{
basappa2025amvicc,
title={{AMVICC}: A Novel Benchmark for Cross-Modal Failure Mode Profiling for {VLM}s and {IGM}s},
author={Aahana Basappa and Pranay Goel and Anusri Karra and Anish Karra and Asa Gilmore and Kevin Zhu},
booktitle={1st Workshop on VLM4RWD @ NeurIPS 2025},
year={2025},
url={https://openreview.net/forum?id=vDkdG55rDL}
}

```

## Acknowledgement <a name="acknowledgement"></a>
-  This work is built upon the work done in [Eyes Wide Shut? Exploring the Visual Shortcomings of Multimodal LLMs]([url](https://www.semanticscholar.org/paper/Eyes-Wide-Shut-Exploring-the-Visual-Shortcomings-of-Tong-Liu/ca00f4056f9039d3c1a4c3a113f5ee0527149b66))
