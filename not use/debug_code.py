#!/usr/bin/env python3
"""
Debug script to check dataset structure and create proper ImageSets files
for your specific file naming convention
"""
import os
import re

def analyze_dataset_structure(data_path):
    """Analyze the actual structure of your dataset"""
    print(f"Analyzing dataset structure at: {data_path}")
    print("=" * 60)
    
    if not os.path.exists(data_path):
        print(f"ERROR: Dataset path does not exist: {data_path}")
        return None, None
    
    original_dir = os.path.join(data_path, 'original')
    highpass_dir = os.path.join(data_path, 'highpass')
    
    def scan_directory(dir_path, modality_name):
        """Scan directory and collect file information"""
        if not os.path.exists(dir_path):
            print(f"✗ {modality_name} directory not found: {dir_path}")
            return []
        
        print(f"✓ Found {modality_name} directory")
        
        files_info = []
        total_files = 0
        
        # Scan all subdirectories
        for subdir in os.listdir(dir_path):
            subdir_path = os.path.join(dir_path, subdir)
            if os.path.isdir(subdir_path):
                print(f"  Scanning subfolder: {subdir}")
                files_in_subdir = 0
                
                for file in os.listdir(subdir_path):
                    if file.endswith(('.jpg', '.jpeg', '.tiff', '.png')):
                        files_info.append({
                            'folder': subdir,
                            'filename': file,
                            'full_path': os.path.join(subdir_path, file)
                        })
                        files_in_subdir += 1
                        total_files += 1
                
                print(f"    {files_in_subdir} image files")
                
                # Show sample files
                sample_files = [f for f in os.listdir(subdir_path) 
                              if f.endswith(('.jpg', '.jpeg', '.tiff', '.png'))][:3]
                for sample in sample_files:
                    print(f"      Sample: {sample}")
        
        print(f"  Total {modality_name} files: {total_files}")
        return files_info
    
    # Scan both directories
    original_files = scan_directory(original_dir, "original")
    highpass_files = scan_directory(highpass_dir, "highpass")
    
    return original_files, highpass_files


def extract_base_id(filename):
    """
    Extract base ID from complex filename
    Examples:
    - 98000031.1.tiff1405192246_39_rotate270.jpg -> 98000031.1
    - 97002310.13.tiff1625312535_40.jpg -> 97002310.13
    """
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Pattern to match the base ID (numbers.numbers at the beginning)
    pattern = r'^(\d+\.\d+)'
    match = re.match(pattern, name_without_ext)
    
    if match:
        return match.group(1)
    
    # Fallback: try to extract just the first part before .tiff
    if '.tiff' in name_without_ext:
        return name_without_ext.split('.tiff')[0]
    
    # Last resort: return the whole name without extension
    return name_without_ext


def create_imagesets_files(data_path, original_files, highpass_files):
    """Create ImageSets files based on actual file structure"""
    print("\nCreating ImageSets files...")
    print("=" * 60)
    
    # Create ImageSets directory
    imagesets_dir = os.path.join(data_path, 'ImageSets')
    os.makedirs(imagesets_dir, exist_ok=True)
    
    # Process original files
    if original_files:
        original_txt_path = os.path.join(imagesets_dir, 'original.txt')
        with open(original_txt_path, 'w') as f:
            for file_info in original_files:
                # Create an identifier that includes both folder and filename
                # This will be used to find the file later
                identifier = f"{file_info['folder']}/{os.path.splitext(file_info['filename'])[0]}"
                f.write(f"{identifier}\n")
        
        print(f"Created {original_txt_path} with {len(original_files)} entries")
        
        # Show some sample entries
        print("Sample original entries:")
        for i, file_info in enumerate(original_files[:5]):
            identifier = f"{file_info['folder']}/{os.path.splitext(file_info['filename'])[0]}"
            print(f"  {identifier}")
    
    # Process highpass files
    if highpass_files:
        highpass_txt_path = os.path.join(imagesets_dir, 'highpass.txt')
        with open(highpass_txt_path, 'w') as f:
            for file_info in highpass_files:
                identifier = f"{file_info['folder']}/{os.path.splitext(file_info['filename'])[0]}"
                f.write(f"{identifier}\n")
        
        print(f"Created {highpass_txt_path} with {len(highpass_files)} entries")
        
        # Show some sample entries
        print("Sample highpass entries:")
        for i, file_info in enumerate(highpass_files[:5]):
            identifier = f"{file_info['folder']}/{os.path.splitext(file_info['filename'])[0]}"
            print(f"  {identifier}")


def create_train_val_split(data_path, original_files, train_ratio=0.8):
    """Create train/val split"""
    if not original_files:
        print("No original files found, skipping train/val split")
        return
    
    print(f"\nCreating train/val split (train: {train_ratio*100}%, val: {(1-train_ratio)*100}%)")
    print("=" * 60)
    
    # Shuffle and split
    import random
    random.seed(42)  # For reproducible splits
    
    shuffled_files = original_files.copy()
    random.shuffle(shuffled_files)
    
    split_idx = int(len(shuffled_files) * train_ratio)
    train_files = shuffled_files[:split_idx]
    val_files = shuffled_files[split_idx:]
    
    imagesets_dir = os.path.join(data_path, 'ImageSets')
    
    # Create train.txt
    train_txt_path = os.path.join(imagesets_dir, 'train.txt')
    with open(train_txt_path, 'w') as f:
        for file_info in train_files:
            identifier = f"{file_info['folder']}/{os.path.splitext(file_info['filename'])[0]}"
            f.write(f"{identifier}\n")
    
    # Create val.txt
    val_txt_path = os.path.join(imagesets_dir, 'val.txt')
    with open(val_txt_path, 'w') as f:
        for file_info in val_files:
            identifier = f"{file_info['folder']}/{os.path.splitext(file_info['filename'])[0]}"
            f.write(f"{identifier}\n")
    
    print(f"Created {train_txt_path} with {len(train_files)} entries")
    print(f"Created {val_txt_path} with {len(val_files)} entries")


if __name__ == "__main__":
    # Update this path to your actual dataset path
    dataset_path = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset"
    
    # Analyze structure
    original_files, highpass_files = analyze_dataset_structure(dataset_path)
    
    if original_files or highpass_files:
        # Create ImageSets files
        create_imagesets_files(dataset_path, original_files, highpass_files)
        
        # Create train/val split
        create_train_val_split(dataset_path, original_files)
        
        print("\n" + "=" * 60)
        print("SUCCESS! ImageSets files created.")
        print("Now update your DataLoaders to use the new file structure.")
    else:
        print("No image files found. Please check your dataset path.")