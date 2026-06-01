import os
from PIL import Image
import imagehash

class AutomaticCleaner:
    def __init__(self, target_folder, min_dimension=400):
        """
        min_dimension: The shorter side of the image must be at least this many pixels.
        This prevents portrait photos (e.g. 500x750) from being rejected while still
        filtering out tiny icons (96x96) and thumbnails.
        """
        self.target_folder = target_folder
        self.min_dimension = min_dimension
        self.hashes = set()
        
    def is_valid_and_clean(self, filepath):
        """
        Checks if an image is valid, not tiny, and not a duplicate.
        Deletes the file if it fails any check and returns False.
        """
        try:
            with Image.open(filepath) as img:
                # 1. Check for corrupt file (Pillow raises exception if corrupt)
                img.verify()
        except Exception as e:
            print(f"  ✗ Deleting corrupt file: {os.path.basename(filepath)}")
            os.remove(filepath)
            return False

        try:
            # Reopen to check dimensions and hash (verify() closes/modifies state)
            with Image.open(filepath) as img:
                # 2. Check for tiny images / thumbnails
                width, height = img.size
                shorter_side = min(width, height)
                if shorter_side < self.min_dimension:
                    print(f"  ✗ Deleting tiny image: {os.path.basename(filepath)} ({width}x{height})")
                    img.close()
                    os.remove(filepath)
                    return False
                
                # 3. Check for duplicates using perceptual hash
                # We use phash which is good for finding similar images
                hash_val = str(imagehash.phash(img))
                if hash_val in self.hashes:
                    print(f"  ✗ Deleting duplicate: {os.path.basename(filepath)} (hash: {hash_val})")
                    img.close()
                    os.remove(filepath)
                    return False
                
                self.hashes.add(hash_val)
                return True
                
        except Exception as e:
            print(f"  ✗ Error processing: {os.path.basename(filepath)} — {e}")
            os.remove(filepath)
            return False
