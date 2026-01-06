import os
import csv
import json
from datetime import datetime
from PIL import Image
from io import BytesIO
from IPython.display import display
import requests
import argparse
# =========================
# CONFIGURATION
# =========================

# Path to your input dataset CSV file
CSV_PATH = "dataset.csv"

# Where all generated images and metadata will be saved
OUTPUT_FOLDER = "output_midjourney"

# How many images to generate for each prompt
IMAGES_PER_PROMPT = 2

# =========================
# LOAD DATASET FROM CSV
# =========================

def load_dataset_from_csv(path):
    """
    Loads the dataset from a CSV file.
    Assumes each row contains: id, category, question, prompt_im, prompt_ex, expected
    Returns a list of dictionaries, one per row.
    """
    dataset = []
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # Reads each row as a dictionary
        for row in reader:
            dataset.append({
                "id": row["id"],
                "category": row.get("category", "uncategorized"),
                "question": row["question"],
                "prompt_im": row["prompt_im"],
                "prompt_ex": row["prompt_ex"],
                "expected": row["expected"]
            })
    return dataset

# =========================
# GENERATE IMAGES
# =========================

# =========================
# MIDJOURNEY 
# =========================


def query(payload, API_URL, headers): 
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

def generate_midjourney_image(prompt, MJ_API_KEY): 
    """
    Calls a MidJourney wrapper API to generate an image. 
    """
    API_URL = "https://api-inference.huggingface.co/models/models/midjourney-v6"
    headers = {"Authorization": f"Bearer {MJ_API_KEY}", "Content-Type": "application/json"}
    ("Generating Midjourney image for:", prompt)
    image_bytes = query({
        "inputs": prompt
    }, API_URL, headers)


    image = Image.open(BytesIO(image_bytes))

    return image
# =========================
# HTML OUTPUT
# =========================

def make_directory(path):
    """
    Creates a directory if it doesn't already exist.
    """
    if not os.path.exists(path):
        os.makedirs(path)
 # Replace with the actual path

def pull_images(image_directory):
    """
    Pulls the images from the outputted image directory
    """
    valid_extensions = (".jpg", ".jpeg", ".png", "html")
    image_list = []
    for filename in os.listdir(image_directory):
        if filename.lower().endswith(valid_extensions):
            filepath = os.path.join(image_directory, filename)
        try:
            img = Image.open(filepath)
            image_list.append(img)
        except IOError:
            print(f"Could not open or process image: {filename}")
    
    return image_list

def save_image(image, path):
    """
    Saves the given Python Imaging Library image to the specified path.
    """
    image.save(path)

def generate_images(dataset, MJ_API_KEY):
    """
    Iterates through the dataset, generates images using the prompt,
    saves them to disk, and writes metadata to JSON files.
    
    Returns a list of metadata for use in HTML index generation.
    """
    make_directory(OUTPUT_FOLDER)
    index_data = []


    for item in dataset:
        item_folder = os.path.join(OUTPUT_FOLDER, item["id"])
        make_directory(item_folder)

        image_files = []
        img_im= generate_midjourney_image(item["prompt_im"], MJ_API_KEY)
        filename_im = f"{item['id']}_implicit.png"
        filepath_im = os.path.join(item_folder, filename_im)
        save_image(img_im, filepath_im)
        image_files.append(filename_im)
        display(img_im)

        img_ex = generate_midjourney_image(item["prompt_ex"], MJ_API_KEY)
        filename_ex = f"{item['id']}_explicit.png"
        filepath_ex = os.path.join(item_folder, filename_ex)
        save_image(img_ex, filepath_ex)
        image_files.append(filename_ex)
        display(img_ex)
    

        # Save metadata for this item
        meta = {
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "prompt_im": item["prompt_im"], 
            "prompt_ex": item["prompt_ex"],
            "expected": item["expected"],
            "images": image_files
        }

        with open(os.path.join(item_folder, "meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

        index_data.append(meta)

    return index_data

# =========================
# HTML OUTPUT
# =========================

def generate_html(index_data):
    """
    Creates an HTML file that allows a human to visually inspect
    generated images alongside their prompts and questions.
    """
    html_path = os.path.join(OUTPUT_FOLDER, "index.html")

    with open(html_path, "w") as f:
        # Write basic HTML header
        f.write("<html><head><title>MMVP Grading</title></head><body>\n")
        f.write("<h1>MMVP Evaluation</h1>\n")
        f.write(f"<p>Generated: {datetime.now()}</p><hr>\n")

        # Add a section for each dataset item
        for item in index_data:
            f.write(f"<h2>{item['id']} [{item['category']}]</h2>\n")
            f.write(f"<p><strong>Question:</strong> {item['question']}</p>\n")
            f.write(f"<p><strong>Prompt (Implicit): </strong> {item['prompt_im']}</p>\n")
            f.write(f"<p><strong>Prompt (Explicit): </strong> {item['prompt_ex']}</p>\n")
            f.write(f"<p><strong>Expected:</strong> {item['expected']}</p>\n")

            # Embed each image for this prompt
            for img_name in item["images"]:
                img_path = f"{item['id']}/{img_name}"
                f.write(f"<img src='{img_path}' width='256' style='margin:10px;'>\n")

            f.write("<hr>\n")

        f.write("</body></html>\n")

    print("✅ index.html created.")

# =========================
# MAIN SCRIPT
# =========================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mj-api-key", type=str, default=None)
    args = parser.parse_args()

    MJ_API_KEY = args.mj_api_key
    # Step 1: Load CSV dataset
    print("📂 Loading dataset from:", CSV_PATH)
    dataset = load_dataset_from_csv(CSV_PATH)
    print(f"📋 Loaded {len(dataset)} rows.")

    # Step 2: Generate images and save metadata
    index = generate_images(dataset, MJ_API_KEY)

    # Step 3: Build HTML interface for human evaluation
    generate_html(index)

    print("✅ Done! Check 'output/index.html'")