import os
import argparse
from dataset_builder.collectors.unsplash import UnsplashCollector
from dataset_builder.collectors.pexels import PexelsCollector
from dataset_builder.collectors.pixabay import PixabayCollector
from dataset_builder.cleaner import AutomaticCleaner
from dataset_builder.metadata import MetadataGenerator
from dataset_builder.statistics import DatasetStatistics

def build_dataset(topic, max_images=10):
    # Determine safe label/folder name from topic
    label = topic.lower().replace(' ', '_')
    base_folder = os.path.join("dataset", "important")
    target_folder = os.path.join(base_folder, label)
    
    print(f"=== Ham Dataset Builder ===")
    print(f"Topic: {topic}")
    print(f"Target: {target_folder}")
    print(f"Max images per source: {max_images}")
    print("===========================\n")

    os.makedirs(target_folder, exist_ok=True)

    # Initialize modules
    cleaner = AutomaticCleaner(target_folder)
    metadata = MetadataGenerator(target_folder)
    
    # Initialize collectors
    collectors = [
        ("unsplash", UnsplashCollector(target_folder, max_images)),
        ("pexels", PexelsCollector(target_folder, max_images)),
        ("pixabay", PixabayCollector(target_folder, max_images))
    ]
    
    # Run pipeline
    for source_type, collector in collectors:
        try:
            for filepath, source_url in collector.search_and_download(topic):
                if cleaner.is_valid_and_clean(filepath):
                    metadata.log_image(filepath, label, source_type, source_url)
        except Exception as e:
            print(f"⚠ Collector '{source_type}' failed: {e}")
            print(f"  Continuing with remaining collectors...\n")

    # Print final statistics
    stats = DatasetStatistics(base_folder)
    stats.generate_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Ham Dataset for AI Gallery Cleaner")
    parser.add_argument("topic", type=str, help="Search topic (e.g. 'travel photography')")
    parser.add_argument("--limit", type=int, default=10, help="Max images to download per source")
    
    args = parser.parse_args()
    build_dataset(args.topic, args.limit)
