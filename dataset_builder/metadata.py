import os
import pandas as pd

class MetadataGenerator:
    def __init__(self, target_folder):
        self.target_folder = target_folder
        self.csv_path = os.path.join(target_folder, 'metadata.csv')
        self.columns = ['filename', 'label', 'source_type', 'source_url']
        
        # Initialize CSV if it doesn't exist
        if not os.path.exists(self.csv_path):
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.csv_path, index=False)

    def log_image(self, filepath, label, source_type, source_url):
        filename = os.path.basename(filepath)
        df = pd.DataFrame([{
            'filename': filename,
            'label': label,
            'source_type': source_type,
            'source_url': source_url
        }])
        
        df.to_csv(self.csv_path, mode='a', header=False, index=False)
