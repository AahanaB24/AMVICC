from huggingface_hub import snapshot_download, hf_hub_download
import os

def download_mmvp_dataset():
    """Download MMVP dataset files"""
    
    local_dir = "./MMVP_dataset"
    
    print("Downloading MMVP dataset...")
    
    # Download everything from the repository
    snapshot_download(
        repo_id="MMVP/MMVP",
        repo_type="dataset",
        local_dir=local_dir,
        # You can specify patterns to only download what you need
        # allow_patterns=["MMVP Images/*", "Questions.csv"]
    )
    
    print(f"Dataset downloaded to: {local_dir}")
    
    # List what was downloaded
    if os.path.exists(os.path.join(local_dir, "MMVP Images")):
        image_count = len([f for f in os.listdir(os.path.join(local_dir, "MMVP Images")) 
                          if f.endswith('.jpg')])
        print(f"Downloaded {image_count} images")
    
    return local_dir

def download_specific_files():
    """Download only the files you need"""
    local_dir = "./MMVP_dataset"
    os.makedirs(local_dir, exist_ok=True)
    
    # Download Questions.csv
    print("Downloading Questions.csv...")
    hf_hub_download(
        repo_id="MMVP/MMVP",
        filename="Questions.csv",
        repo_type="dataset",
        local_dir=local_dir
    )
    
    # For images, you'd need to know the filenames or use snapshot_download
    print("Downloading images...")
    snapshot_download(
        repo_id="MMVP/MMVP",
        repo_type="dataset",
        local_dir=local_dir,
        allow_patterns=["MMVP Images/*.jpg"]  # Only download JPG files from MMVP Images folder
    )
    
    return local_dir

if __name__ == "__main__":
    # Install required package first: pip install huggingface_hub
    
    # Option 1: Download everything
    dataset_path = download_mmvp_dataset()
    
    print(f"MMVP dataset ready at: {dataset_path}")