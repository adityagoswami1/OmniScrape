import os
import pandas as pd

class DatasetStatistics:
    def __init__(self, base_folder):
        self.base_folder = base_folder
        
    def generate_report(self):
        print("\n--- Dataset Statistics ---")
        total_images = 0
        
        if not os.path.exists(self.base_folder):
            print("Dataset folder does not exist yet.")
            return

        for category in os.listdir(self.base_folder):
            category_path = os.path.join(self.base_folder, category)
            if os.path.isdir(category_path):
                csv_path = os.path.join(category_path, 'metadata.csv')
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    count = len(df)
                    total_images += count
                    print(f"{category.capitalize()}: {count} images")
                else:
                    # Fallback to counting files if no metadata
                    count = len([f for f in os.listdir(category_path) if f.endswith('.jpg')])
                    total_images += count
                    print(f"{category.capitalize()} (No CSV): {count} images")
                    
        print(f"Total Dataset Size: {total_images} images")
        print("--------------------------\n")
