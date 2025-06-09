import os
import shutil
import random
from pathlib import Path
import argparse
from collections import defaultdict
import re


def get_base_filename(filename):
    """
    Trích xuất base filename từ augmented filename
    
    VD: 
    - abcxyz_1.jpg -> abcxyz_1
    - abcxyz_1_rotate90.jpg -> abcxyz_1
    - abcxyz_1_flip_horizontal.jpg -> abcxyz_1
    """
    # Remove extension first
    name_without_ext = filename.rsplit('.', 1)[0]
    
    # Define common augmentation suffixes
    aug_patterns = [
        r'_rotate\d+',
        r'_hflip',
        r'_vflip', 
        r'_rdrotate+',
        r'_rr31-90vflip+'
    ]
    
    # Remove augmentation suffixes
    base_name = name_without_ext
    for pattern in aug_patterns:
        base_name = re.sub(pattern + r'$', '', base_name)
    
    # Also handle multiple suffixes (e.g., _rotate90_flip)
    # Keep removing until no more matches
    prev_base = ""
    while base_name != prev_base:
        prev_base = base_name
        for pattern in aug_patterns:
            base_name = re.sub(pattern + r'$', '', base_name)
    
    return base_name


def group_files_by_base(files):
    """
    Nhóm các files theo base filename
    
    Returns:
        dict: {base_name: [list_of_files]}
    """
    groups = defaultdict(list)
    
    for file_path in files:
        base_name = get_base_filename(file_path.name)
        groups[base_name].append(file_path)
    
    return dict(groups)


def split_dataset_with_augmentation(dataset_path, output_path, train_ratio=0.8, val_ratio=0.2, seed=42):
    """
    Chia dataset có augmentation thành train và validation sets
    Đảm bảo ảnh gốc và các phiên bản augmented đi cùng nhau
    
    Args:
        dataset_path (str): Đường dẫn đến thư mục dataset (đã có augmented images)
        output_path (str): Đường dẫn đến thư mục output
        train_ratio (float): Tỷ lệ data dành cho training
        val_ratio (float): Tỷ lệ data dành cho validation
        seed (int): Seed cho random
    """
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Convert to Path objects
    dataset_path = Path(dataset_path)
    output_path = Path(output_path)
    
    # Create output directories
    train_dir = output_path / "train"
    val_dir = output_path / "val"
    
    # Remove existing directories if they exist
    if train_dir.exists():
        shutil.rmtree(train_dir)
    if val_dir.exists():
        shutil.rmtree(val_dir)
    
    # Create new directories
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Created directories:")
    print(f"  Train: {train_dir}")
    print(f"  Val: {val_dir}")
    
    # Get all subdirectories (classes) in the dataset
    class_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]
    
    if not class_dirs:
        print("No class directories found in the dataset!")
        return
    
    print(f"\nFound {len(class_dirs)} classes:")
    for class_dir in class_dirs:
        print(f"  - {class_dir.name}")
    
    total_groups = 0
    total_files = 0
    train_groups = 0
    train_files = 0
    val_groups = 0
    val_files = 0
    
    # Process each class
    for class_dir in class_dirs:
        class_name = class_dir.name
        print(f"\nProcessing class: {class_name}")
        
        # Create class directories in train and val
        train_class_dir = train_dir / class_name
        val_class_dir = val_dir / class_name
        train_class_dir.mkdir(exist_ok=True)
        val_class_dir.mkdir(exist_ok=True)
        
        # Get all files in this class
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        files = [f for f in class_dir.iterdir() 
                if f.is_file() and f.suffix.lower() in image_extensions]
        
        if not files:
            print(f"  No image files found in {class_name}")
            continue
        
        # Group files by base filename
        file_groups = group_files_by_base(files)
        
        print(f"  Total files: {len(files)}")
        print(f"  Unique base images: {len(file_groups)}")
        
        # Show some examples of grouping
        print(f"  Example groupings:")
        for i, (base_name, group_files) in enumerate(list(file_groups.items())[:3]):
            file_names = [f.name for f in group_files]
            print(f"    {base_name}: {file_names}")
        
        # Get list of base names and shuffle them
        base_names = list(file_groups.keys())
        random.shuffle(base_names)
        
        # Calculate split
        total_base_count = len(base_names)
        train_base_count = int(total_base_count * train_ratio)
        
        # Split base names
        train_base_names = base_names[:train_base_count]
        val_base_names = base_names[train_base_count:]
        
        print(f"  Train base images: {len(train_base_names)}")
        print(f"  Val base images: {len(val_base_names)}")
        
        # Copy train files
        train_file_count = 0
        for base_name in train_base_names:
            for file_path in file_groups[base_name]:
                dest_path = train_class_dir / file_path.name
                shutil.copy2(file_path, dest_path)
                train_file_count += 1
        
        # Copy val files
        val_file_count = 0
        for base_name in val_base_names:
            for file_path in file_groups[base_name]:
                dest_path = val_class_dir / file_path.name
                shutil.copy2(file_path, dest_path)
                val_file_count += 1
        
        print(f"  Train files copied: {train_file_count}")
        print(f"  Val files copied: {val_file_count}")
        
        # Update totals
        total_groups += total_base_count
        total_files += len(files)
        train_groups += len(train_base_names)
        train_files += train_file_count
        val_groups += len(val_base_names)
        val_files += val_file_count
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"DATASET SPLIT SUMMARY (WITH AUGMENTATION GROUPING)")
    print(f"{'='*60}")
    print(f"Total unique base images: {total_groups}")
    print(f"Total files processed: {total_files}")
    print(f"")
    print(f"Train:")
    print(f"  Base images: {train_groups} ({train_groups/total_groups*100:.1f}%)")
    print(f"  Total files: {train_files} ({train_files/total_files*100:.1f}%)")
    print(f"")
    print(f"Val:")
    print(f"  Base images: {val_groups} ({val_groups/total_groups*100:.1f}%)")
    print(f"  Total files: {val_files} ({val_files/total_files*100:.1f}%)")
    print(f"")
    print(f"Output directories:")
    print(f"  Train: {train_dir.absolute()}")
    print(f"  Val: {val_dir.absolute()}")


def test_base_filename_extraction():
    """Test function để kiểm tra việc trích xuất base filename"""
    test_cases = [
        "abcxyz_1.jpg",
        "abcxyz_1_rotate90.jpg", 
        "abcxyz_1_flip_horizontal.jpg",
        "abcxyz_1_rotate90_flip_horizontal.jpg",
        "image_001_brightness_150.png",
        "photo_rotate180_blur_5.jpg",
        "test_augmented.png",
        "normal_image.jpg"
    ]
    
    print("Testing base filename extraction:")
    print("-" * 40)
    for filename in test_cases:
        base = get_base_filename(filename)
        print(f"{filename:<35} -> {base}")


def main():
    parser = argparse.ArgumentParser(description="Split augmented dataset into train and validation sets")
    parser.add_argument("--dataset_path", type=str, required=True,
                       help="/Users/vantrang/Desktop/BME Design/BME Design III/dataset/original")
    parser.add_argument("--output_path", type=str, required=True,
                       help="/Users/vantrang/Desktop/BME Design/BME Design III/dataset")
    parser.add_argument("--train_ratio", type=float, default=0.8,
                       help="Ratio of base images for training (default: 0.8)")
    parser.add_argument("--val_ratio", type=float, default=0.2,
                       help="Ratio of base images for validation (default: 0.2)")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--test", action="store_true",
                       help="Run test for base filename extraction")
    
    args = parser.parse_args()
    
    # Run test if requested
    if args.test:
        test_base_filename_extraction()
        return
    
    # Validate ratios
    if abs(args.train_ratio + args.val_ratio - 1.0) > 1e-6:
        print("Error: train_ratio + val_ratio must equal 1.0")
        return
    
    # Check if dataset path exists
    if not os.path.exists(args.dataset_path):
        print(f"Error: Dataset path '{args.dataset_path}' does not exist!")
        return
    
    print(f"Dataset path: {args.dataset_path}")
    print(f"Output path: {args.output_path}")
    print(f"Train ratio: {args.train_ratio} (of base images)")
    print(f"Val ratio: {args.val_ratio} (of base images)")
    print(f"Random seed: {args.seed}")
    print(f"\nNote: This will group augmented images with their base images")
    print(f"      to avoid data leakage between train/val sets.")
    
    # Confirm before proceeding
    response = input("\nProceed with dataset split? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("Operation cancelled.")
        return
    
    # Split dataset
    split_dataset_with_augmentation(
        dataset_path=args.dataset_path,
        output_path=args.output_path,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed
    )


if __name__ == "__main__":
    main()