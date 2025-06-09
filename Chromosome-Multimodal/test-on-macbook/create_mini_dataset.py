#!/usr/bin/env python3
"""
Create a mini dataset with just a few samples for testing
"""

import os
import shutil
from pathlib import Path
import random

def create_mini_dataset(full_dataset_path="dataset", mini_dataset_path="mini_dataset", samples_per_class=5):
    """
    Create a mini dataset with only a few samples per class for testing
    """
    full_path = Path(full_dataset_path)
    mini_path = Path(mini_dataset_path)
    
    # Create mini dataset structure
    for split in ["train", "val"]:
        (mini_path / split / "ImageSets").mkdir(parents=True, exist_ok=True)
        (mini_path / split / "annotations").mkdir(parents=True, exist_ok=True)
        
        # Symlink to original ImageData to save space
        if not (mini_path / split / "ImageData").exists():
            (mini_path / split / "ImageData").symlink_to(f"../../{full_dataset_path}/ImageData")
    
    for split in ["train", "val"]:
        print(f"Creating mini {split} dataset...")
        
        # Read original files
        with open(full_path / split / "ImageSets" / "original.txt", "r") as f:
            orig_files = [line.strip() for line in f]
        
        with open(full_path / split / "ImageSets" / "highpass.txt", "r") as f:
            hp_files = [line.strip() for line in f]
        
        with open(full_path / split / "annotations" / "original.txt", "r") as f:
            orig_anns = [line.strip() for line in f]
        
        with open(full_path / split / "annotations" / "highpass.txt", "r") as f:
            hp_anns = [line.strip() for line in f]
        
        # Group by class
        orig_by_class = {}
        for file, ann in zip(orig_files, orig_anns):
            label = int(ann.split()[-1])
            if label not in orig_by_class:
                orig_by_class[label] = []
            orig_by_class[label].append((file, ann))
        
        hp_by_class = {}
        for file, ann in zip(hp_files, hp_anns):
            label = int(ann.split()[-1])
            if label not in hp_by_class:
                hp_by_class[label] = []
            hp_by_class[label].append((file, ann))
        
        # Sample a few from each class
        mini_orig_files, mini_orig_anns = [], []
        mini_hp_files, mini_hp_anns = [], []
        
        for class_id in range(24):
            # Sample original files
            if class_id in orig_by_class:
                class_data = orig_by_class[class_id]
                sample_size = min(samples_per_class, len(class_data))
                sampled = random.sample(class_data, sample_size)
                
                for file, ann in sampled:
                    mini_orig_files.append(file)
                    mini_orig_anns.append(ann)
            
            # Sample highpass files
            if class_id in hp_by_class:
                class_data = hp_by_class[class_id]
                sample_size = min(samples_per_class, len(class_data))
                sampled = random.sample(class_data, sample_size)
                
                for file, ann in sampled:
                    mini_hp_files.append(file)
                    mini_hp_anns.append(ann)
        
        # Write mini dataset files
        with open(mini_path / split / "ImageSets" / "original.txt", "w") as f:
            for file in mini_orig_files:
                f.write(f"{file}\n")
        
        with open(mini_path / split / "ImageSets" / "highpass.txt", "w") as f:
            for file in mini_hp_files:
                f.write(f"{file}\n")
        
        with open(mini_path / split / "annotations" / "original.txt", "w") as f:
            for ann in mini_orig_anns:
                f.write(f"{ann}\n")
        
        with open(mini_path / split / "annotations" / "highpass.txt", "w") as f:
            for ann in mini_hp_anns:
                f.write(f"{ann}\n")
        
        print(f"  {split}: {len(mini_orig_files)} original, {len(mini_hp_files)} highpass")
    
    print(f"\nMini dataset created at: {mini_dataset_path}")
    print(f"Total samples: ~{samples_per_class * 24 * 2} per split")

if __name__ == "__main__":
    # Create a mini dataset with only 3 samples per class for testing
    create_mini_dataset(samples_per_class=3)