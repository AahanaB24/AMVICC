import os
import csv
import json
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64
import argparse
from openai import OpenAI

# =========================
# CONFIGURATION
# =========================

# Path to your input dataset CSV file
CSV_PATH = "AMVICC.csv"

# Where all generated images and metadata will be saved
OUTPUT_FOLDER = "output_google_flash"

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


def generate_image(prompt_user, client):
    """
    Generates an image using OpenRouter's Google Gemini Flash model.
    """
    print(f"Generating image for prompt: {prompt_user[:50]}...")
    
    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.5-flash-image-preview",
            messages=[
                {
                    "role": "user",
                    "content": prompt_user
                }
            ],
            modalities=["image", "text"]
        )
        
        # Get the assistant's response
        assistant_message = completion.choices[0].message
        
        # Debug: Print the full response structure
        print("Full response structure:")
        print(f"Message: {assistant_message}")
        print(f"Message type: {type(assistant_message)}")
        print(f"Message attributes: {dir(assistant_message)}")
        
        # Try different ways to access the image data
        image_found = False
        
        # Method 1: Check for images attribute
        if hasattr(assistant_message, 'images') and assistant_message.images:
            print(f"Found images attribute: {assistant_message.images}")
            image_data = assistant_message.images[0]
            image_found = True
        
        # Method 2: Check for attachments
        elif hasattr(assistant_message, 'attachments') and assistant_message.attachments:
            print(f"Found attachments: {assistant_message.attachments}")
            image_data = assistant_message.attachments[0]
            image_found = True
            
        # Method 3: Check for content with images
        elif hasattr(assistant_message, 'content'):
            content = assistant_message.content
            print(f"Content: {content}")
            print(f"Content type: {type(content)}")
            
            # If content is a list, look for image blocks
            if isinstance(content, list):
                for block in content:
                    print(f"Block: {block}, Type: {type(block)}")
                    if hasattr(block, 'type') and block.type == 'image':
                        image_data = block
                        image_found = True
                        break
                    elif isinstance(block, dict) and block.get('type') == 'image':
                        image_data = block
                        image_found = True
                        break
            
            # If content is a string, check if it contains image data
            elif isinstance(content, str) and ('data:image/' in content or len(content) > 1000):
                image_data = content
                image_found = True
        
        # Method 4: Check the raw completion object
        if not image_found:
            print("Checking raw completion object...")
            print(f"Completion type: {type(completion)}")
            
            # Sometimes the image might be in the raw response
            if hasattr(completion, 'data') and completion.data:
                image_data = completion.data
                image_found = True
        
        if image_found:
            print(f"Processing image data: {type(image_data)}")
            
            # Handle different image data formats
            if isinstance(image_data, dict):
                # Look for common image data keys
                for key in ['url', 'data', 'b64_json', 'image_url', 'source']:
                    if key in image_data:
                        img_content = image_data[key]
                        if isinstance(img_content, dict) and 'url' in img_content:
                            img_content = img_content['url']
                        
                        if isinstance(img_content, str):
                            if img_content.startswith('data:image/'):
                                base64_data = img_content.split(',')[1]
                                image_bytes = base64.b64decode(base64_data)
                                image = Image.open(BytesIO(image_bytes))
                                return image
                            else:
                                # Try direct base64 decode
                                try:
                                    image_bytes = base64.b64decode(img_content)
                                    image = Image.open(BytesIO(image_bytes))
                                    return image
                                except:
                                    continue
                        
            elif isinstance(image_data, str):
                if image_data.startswith('data:image/'):
                    base64_data = image_data.split(',')[1]
                    image_bytes = base64.b64decode(base64_data)
                    image = Image.open(BytesIO(image_bytes))
                    return image
                else:
                    # Try direct base64 decode
                    try:
                        image_bytes = base64.b64decode(image_data)
                        image = Image.open(BytesIO(image_bytes))
                        return image
                    except:
                        pass
            
            # Handle object with attributes
            elif hasattr(image_data, 'url'):
                print("Found object with URL attribute")
                url = image_data.url
                if url.startswith('data:image/'):
                    base64_data = url.split(',')[1]
                    image_bytes = base64.b64decode(base64_data)
                    image = Image.open(BytesIO(image_bytes))
                    return image
                    
            elif hasattr(image_data, 'data'):
                print("Found object with data attribute")
                data = image_data.data
                if isinstance(data, str):
                    try:
                        image_bytes = base64.b64decode(data)
                        image = Image.open(BytesIO(image_bytes))
                        return image
                    except:
                        pass
        
        print("❌ Could not find or parse image data from response")
        return None
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return None

def make_directory(path):
    """
    Creates a directory if it doesn't already exist.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def save_image(image, path):
    """
    Saves the given Python Imaging Library image to the specified path.
    """
    image.save(path, format='PNG')

def generate_images(dataset, client):
    """
    Iterates through the dataset, generates images using the prompt,
    saves them to disk, and writes metadata to JSON files.
    
    Returns a list of metadata for use in HTML index generation.
    """
    make_directory(OUTPUT_FOLDER)
    index_data = []

    for i, item in enumerate(dataset):
        print(f"\nProcessing item {i+1}/{len(dataset)}: {item['id']}")
        
        item_folder = os.path.join(OUTPUT_FOLDER, item["id"])
        make_directory(item_folder)

        image_files = []
        
        # Generate implicit prompt image
        try:
            img_im = generate_image(item["prompt_im"], client)
            filename_im = f"{item['id']}_implicit.png"
            filepath_im = os.path.join(item_folder, filename_im)
            save_image(img_im, filepath_im)
            image_files.append(filename_im)
            print(f"✅ Saved implicit image: {filename_im}")
        except Exception as e:
            print(f"❌ Error generating implicit image: {e}")

        # Generate explicit prompt image
        try:
            img_ex = generate_image(item["prompt_ex"], client)
            filename_ex = f"{item['id']}_explicit.png"
            filepath_ex = os.path.join(item_folder, filename_ex)
            save_image(img_ex, filepath_ex)
            image_files.append(filename_ex)
            print(f"✅ Saved explicit image: {filename_ex}")
        except Exception as e:
            print(f"❌ Error generating explicit image: {e}")

        # Save metadata for this item
        meta = {
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "prompt_im": item["prompt_im"], 
            "prompt_ex": item["prompt_ex"],
            "expected": item["expected"],
            "images": image_files,
            "timestamp": datetime.now().isoformat()
        }

        with open(os.path.join(item_folder, "meta.json"), "w", encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = os.path.join(OUTPUT_FOLDER, f"index_{timestamp}.html")

    with open(html_path, "w", encoding='utf-8') as f:
        # Write basic HTML header with CSS styling
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>MMVP Grading</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .item { border: 1px solid #ddd; margin: 20px 0; padding: 20px; }
        .item h2 { color: #333; margin-top: 0; }
        .images { display: flex; flex-wrap: wrap; gap: 10px; }
        .images img { max-width: 300px; border: 1px solid #ccc; }
        .metadata { background: #f5f5f5; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
""")
        f.write("<h1>MMVP Evaluation Results</h1>\n")
        f.write(f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
        f.write(f"<p>Total items: {len(index_data)}</p><hr>\n")

        # Add a section for each dataset item
        for item in index_data:
            f.write(f"<div class='item'>\n")
            f.write(f"<h2>{item['id']} [{item['category']}]</h2>\n")
            f.write(f"<div class='metadata'>\n")
            f.write(f"<p><strong>Question:</strong> {item['question']}</p>\n")
            f.write(f"<p><strong>Implicit Prompt:</strong> {item['prompt_im']}</p>\n")
            f.write(f"<p><strong>Explicit Prompt:</strong> {item['prompt_ex']}</p>\n")
            f.write(f"<p><strong>Expected:</strong> {item['expected']}</p>\n")
            f.write(f"</div>\n")

            # Embed each image for this prompt
            f.write(f"<div class='images'>\n")
            for img_name in item["images"]:
                img_path = f"{item['id']}/{img_name}"
                img_label = "Implicit" if "implicit" in img_name else "Explicit"
                f.write(f"<div>\n")
                f.write(f"<p><strong>{img_label}:</strong></p>\n")
                f.write(f"<img src='{img_path}' alt='{img_name}'>\n")
                f.write(f"</div>\n")
            f.write(f"</div>\n")
            f.write(f"</div>\n")

        f.write("</body></html>\n")

    print(f"✅ HTML report created: {html_path}")
    return html_path

# =========================
# MAIN SCRIPT
# =========================

def main():
    # Declare globals at the start of the function
    global CSV_PATH, OUTPUT_FOLDER
    
    parser = argparse.ArgumentParser(description="Generate images from CSV dataset using OpenRouter API")
    parser.add_argument("--api-key", type=str, required=True, 
                       help="OpenRouter API key")
    parser.add_argument("--csv-path", type=str, default="dataset_tester.csv",
                       help="Path to CSV file")
    parser.add_argument("--output-folder", type=str, default="output_google_flash",
                       help="Output folder for generated images")
    
    args = parser.parse_args()
    
    # Update global variables if provided
    CSV_PATH = args.csv_path
    OUTPUT_FOLDER = args.output_folder

    # Step 1: Load CSV dataset
    print("📂 Loading dataset from:", CSV_PATH)
    try:
        dataset = load_dataset_from_csv(CSV_PATH)
        print(f"📋 Loaded {len(dataset)} rows.")
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found at {CSV_PATH}")
        return
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return

    # Step 2: Initialize OpenRouter client
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=args.api_key,
        )
        print("✅ OpenRouter client initialized")
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return

    # Step 3: Generate images and save metadata
    print("\n🎨 Starting image generation...")
    try:
        index_data = generate_images(dataset, client)
        print(f"✅ Generated images for {len(index_data)} items")
    except Exception as e:
        print(f"❌ Error during image generation: {e}")
        return

    # Step 4: Build HTML interface for human evaluation
    try:
        html_path = generate_html(index_data)
        print(f"✅ Done! Check '{html_path}' for results")
    except Exception as e:
        print(f"❌ Error generating HTML: {e}")

if __name__ == "__main__":
    main()
