import os
import shutil
from pathlib import Path

def generate_chromosome_dataset(original_path, highpass_path, output_path):
    """
    Generate dataset structure for chromosome images
    Note: Original and highpass are different samples, not the same sample processed differently
    """
    # Create output directories
    output_path = Path(output_path)
    imagesets_dir = output_path / "ImageSets"
    imagedata_dir = output_path / "ImageData"
    annotations_dir = output_path / "annotations"
    
    imagesets_dir.mkdir(parents=True, exist_ok=True)
    (imagedata_dir / "original-image").mkdir(parents=True, exist_ok=True)
    (imagedata_dir / "highpass-image").mkdir(parents=True, exist_ok=True)
    annotations_dir.mkdir(parents=True, exist_ok=True)
    
    original_files = []
    highpass_files = []
    original_labels = []
    highpass_labels = []
    
    # Process original images
    original_path = Path(original_path)
    print("Processing original images...")
    for class_folder in sorted(original_path.iterdir()):
        if class_folder.is_dir():
            class_label = int(class_folder.name) - 1  # Convert to 0-based indexing
            print(f"  Class {class_folder.name}: ", end="")
            
            file_count = 0
            for img_file in class_folder.glob("*.jpg"):
                # Use original filename without modification
                img_id = f"orig_{class_folder.name}_{img_file.stem}"
                
                # Copy image to ImageData/original-image with .png extension
                dst_file = imagedata_dir / "original-image" / f"{img_id}.png"
                shutil.copy2(img_file, dst_file)
                
                original_files.append(img_id)
                original_labels.append(class_label)
                file_count += 1
            
            print(f"{file_count} files")
    
    # Process highpass images
    highpass_path = Path(highpass_path)
    print("Processing highpass images...")
    for class_folder in sorted(highpass_path.iterdir()):
        if class_folder.is_dir():
            class_label = int(class_folder.name) - 1  # Convert to 0-based indexing
            print(f"  Class {class_folder.name}: ", end="")
            
            file_count = 0
            for img_file in class_folder.glob("*.jpg"):
                # Use original filename, remove _hp suffix if present
                stem = img_file.stem
                if stem.endswith("_hp"):
                    stem = stem[:-3]  # Remove _hp suffix
                
                img_id = f"hp_{class_folder.name}_{stem}"
                
                # Copy image to ImageData/highpass-image with .png extension
                dst_file = imagedata_dir / "highpass-image" / f"{img_id}.png"
                shutil.copy2(img_file, dst_file)
                
                highpass_files.append(img_id)
                highpass_labels.append(class_label)
                file_count += 1
            
            print(f"{file_count} files")
    
    # Write ImageSets files
    with open(imagesets_dir / "original.txt", "w") as f:
        for img_id in original_files:
            f.write(f"{img_id}\n")
    
    with open(imagesets_dir / "highpass.txt", "w") as f:
        for img_id in highpass_files:
            f.write(f"{img_id}\n")
    
    # Write annotations files
    with open(annotations_dir / "original.txt", "w") as f:
        for img_id, label in zip(original_files, original_labels):
            f.write(f"{img_id} {label}\n")
    
    with open(annotations_dir / "highpass.txt", "w") as f:
        for img_id, label in zip(highpass_files, highpass_labels):
            f.write(f"{img_id} {label}\n")
    
    print(f"\nGenerated dataset with:")
    print(f"Original images: {len(original_files)}")
    print(f"Highpass images: {len(highpass_files)}")
    print(f"Classes: {max(max(original_labels), max(highpass_labels)) + 1}")

def create_train_val_split_by_class(dataset_path, train_ratio=0.8):
    """
    Create train/validation split for chromosome dataset
    Since original and highpass are different samples, we split by class
    """
    dataset_path = Path(dataset_path)
    
    # Read original files and labels
    with open(dataset_path / "ImageSets" / "original.txt", "r") as f:
        original_files = [line.strip() for line in f]
    
    with open(dataset_path / "annotations" / "original.txt", "r") as f:
        original_annotations = [line.strip() for line in f]
    
    # Read highpass files and labels
    with open(dataset_path / "ImageSets" / "highpass.txt", "r") as f:
        highpass_files = [line.strip() for line in f]
    
    with open(dataset_path / "annotations" / "highpass.txt", "r") as f:
        highpass_annotations = [line.strip() for line in f]
    
    # Group by class
    original_by_class = {}
    for file, ann in zip(original_files, original_annotations):
        label = int(ann.split()[-1])
        if label not in original_by_class:
            original_by_class[label] = []
        original_by_class[label].append((file, ann))
    
    highpass_by_class = {}
    for file, ann in zip(highpass_files, highpass_annotations):
        label = int(ann.split()[-1])
        if label not in highpass_by_class:
            highpass_by_class[label] = []
        highpass_by_class[label].append((file, ann))
    
    # Create train and val datasets
    train_path = dataset_path / "train"
    val_path = dataset_path / "val"
    
    for split_path in [train_path, val_path]:
        split_path.mkdir(exist_ok=True)
        (split_path / "ImageSets").mkdir(exist_ok=True)
        (split_path / "annotations").mkdir(exist_ok=True)
        
        # Symlink ImageData
        if not (split_path / "ImageData").exists():
            (split_path / "ImageData").symlink_to("../ImageData")
    
    train_orig_files, train_orig_anns = [], []
    train_hp_files, train_hp_anns = [], []
    val_orig_files, val_orig_anns = [], []
    val_hp_files, val_hp_anns = [], []
    
    # Split each class separately
    for class_label in range(24):  # 24 classes
        # Split original files for this class
        if class_label in original_by_class:
            orig_class_data = original_by_class[class_label]
            split_idx = int(len(orig_class_data) * train_ratio)
            
            train_data = orig_class_data[:split_idx]
            val_data = orig_class_data[split_idx:]
            
            for file, ann in train_data:
                train_orig_files.append(file)
                train_orig_anns.append(ann)
            
            for file, ann in val_data:
                val_orig_files.append(file)
                val_orig_anns.append(ann)
        
        # Split highpass files for this class
        if class_label in highpass_by_class:
            hp_class_data = highpass_by_class[class_label]
            split_idx = int(len(hp_class_data) * train_ratio)
            
            train_data = hp_class_data[:split_idx]
            val_data = hp_class_data[split_idx:]
            
            for file, ann in train_data:
                train_hp_files.append(file)
                train_hp_anns.append(ann)
            
            for file, ann in val_data:
                val_hp_files.append(file)
                val_hp_anns.append(ann)
    
    # Write train files
    with open(train_path / "ImageSets" / "original.txt", "w") as f:
        for file in train_orig_files:
            f.write(f"{file}\n")
    
    with open(train_path / "ImageSets" / "highpass.txt", "w") as f:
        for file in train_hp_files:
            f.write(f"{file}\n")
    
    with open(train_path / "annotations" / "original.txt", "w") as f:
        for ann in train_orig_anns:
            f.write(f"{ann}\n")
    
    with open(train_path / "annotations" / "highpass.txt", "w") as f:
        for ann in train_hp_anns:
            f.write(f"{ann}\n")
    
    # Write val files
    with open(val_path / "ImageSets" / "original.txt", "w") as f:
        for file in val_orig_files:
            f.write(f"{file}\n")
    
    with open(val_path / "ImageSets" / "highpass.txt", "w") as f:
        for file in val_hp_files:
            f.write(f"{file}\n")
    
    with open(val_path / "annotations" / "original.txt", "w") as f:
        for ann in val_orig_anns:
            f.write(f"{ann}\n")
    
    with open(val_path / "annotations" / "highpass.txt", "w") as f:
        for ann in val_hp_anns:
            f.write(f"{ann}\n")
    
    print(f"\nTrain: {len(train_orig_files)} original, {len(train_hp_files)} highpass")
    print(f"Val: {len(val_orig_files)} original, {len(val_hp_files)} highpass")

if __name__ == "__main__":
    original_path = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/original"
    highpass_path = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/highpass"
    output_path = "dataset"
    
    print(f"Original path: {original_path}")
    print(f"Highpass path: {highpass_path}")
    print(f"Output path: {output_path}")
    
    # Check if paths exist
    if not os.path.exists(original_path):
        print(f"ERROR: Original path does not exist: {original_path}")
        exit(1)
    if not os.path.exists(highpass_path):
        print(f"ERROR: Highpass path does not exist: {highpass_path}")
        exit(1)
    
    # Generate dataset structure
    generate_chromosome_dataset(original_path, highpass_path, output_path)
    
    # Create train/val split by class
    create_train_val_split_by_class(output_path)