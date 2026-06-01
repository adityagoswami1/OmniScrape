import os
import sys
from PIL import Image
import imagehash

def deduplicate_dataset(dataset_dir="dataset"):
    print(f"Starting deduplication in {dataset_dir}...")
    
    seen_hashes = {}
    total_images = 0
    duplicates_removed = 0
    errors = 0
    
    extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    
    if not os.path.exists(dataset_dir):
        print(f"Directory {dataset_dir} does not exist.")
        return

    for root, _, files in os.walk(dataset_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                filepath = os.path.join(root, file)
                total_images += 1
                
                try:
                    with Image.open(filepath) as img:
                        hash_val = str(imagehash.phash(img))
                        
                        if hash_val in seen_hashes:
                            os.remove(filepath)
                            duplicates_removed += 1
                        else:
                            seen_hashes[hash_val] = filepath
                            
                except Exception as e:
                    errors += 1
                    
    print("\n--- Deduplication Complete ---")
    print(f"Target Directory:     {dataset_dir}")
    print(f"Total images scanned: {total_images}")
    print(f"Unique images kept:   {len(seen_hashes)}")
    print(f"Duplicates removed:   {duplicates_removed}")
    print(f"Errors encountered:   {errors}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    deduplicate_dataset(target)
