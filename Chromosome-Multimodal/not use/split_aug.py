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


def get_all_base_names_from_channels(channel_paths, class_name):
    """
    Lấy tất cả base names từ tất cả channels của một class
    Đảm bảo consistent giữa các channels
    """
    all_base_names = set()
    
    for channel_name, channel_path in channel_paths.items():
        class_dir = channel_path / class_name
        if not class_dir.exists():
            print(f"  Warning: {class_dir} does not exist, skipping this channel")
            continue
            
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        files = [f for f in class_dir.iterdir() 
                if f.is_file() and f.suffix.lower() in image_extensions]
        
        # Get base names from this channel
        base_names = set(get_base_filename(f.name) for f in files)
        all_base_names.update(base_names)
    
    return list(all_base_names)


def split_multichannel_dataset(channel_paths, output_path, train_ratio=0.8, val_ratio=0.2, seed=42):
    """
    Chia dataset đa kênh (original + highpass) thành train và validation sets
    Đảm bảo cùng base images được chia vào cùng tập train/val cho tất cả channels
    
    Args:
        channel_paths (dict): {'original': path1, 'highpass': path2, ...}
        output_path (str): Đường dẫn đến thư mục output
        train_ratio (float): Tỷ lệ data dành cho training
        val_ratio (float): Tỷ lệ data dành cho validation
        seed (int): Seed cho random
    """
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Convert to Path objects
    channel_paths = {name: Path(path) for name, path in channel_paths.items()}
    output_path = Path(output_path)
    
    print(f"Processing channels:")
    for name, path in channel_paths.items():
        print(f"  {name}: {path}")
    
    # Create output directories for each channel
    train_dirs = {}
    val_dirs = {}
    
    for channel_name in channel_paths.keys():
        train_dir = output_path / channel_name / "train"
        val_dir = output_path / channel_name / "val"
        
        # Remove existing directories if they exist
        if train_dir.exists():
            shutil.rmtree(train_dir)
        if val_dir.exists():
            shutil.rmtree(val_dir)
        
        # Create new directories
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)
        
        train_dirs[channel_name] = train_dir
        val_dirs[channel_name] = val_dir
        
        print(f"Created directories for {channel_name}:")
        print(f"  Train: {train_dir}")
        print(f"  Val: {val_dir}")
    
    # Get all classes from the first channel (assuming all channels have same structure)
    first_channel_path = list(channel_paths.values())[0]
    class_dirs = [d for d in first_channel_path.iterdir() if d.is_dir()]
    
    if not class_dirs:
        print("No class directories found in the dataset!")
        return
    
    print(f"\nFound {len(class_dirs)} classes:")
    for class_dir in class_dirs:
        print(f"  - {class_dir.name}")
    
    total_stats = {
        'groups': 0,
        'files': 0,
        'train_groups': 0,
        'train_files': 0,
        'val_groups': 0,
        'val_files': 0
    }
    
    # Process each class
    for class_dir in class_dirs:
        class_name = class_dir.name
        print(f"\nProcessing class: {class_name}")
        
        # Create class directories in train and val for all channels
        for channel_name in channel_paths.keys():
            train_class_dir = train_dirs[channel_name] / class_name
            val_class_dir = val_dirs[channel_name] / class_name
            train_class_dir.mkdir(exist_ok=True)
            val_class_dir.mkdir(exist_ok=True)
        
        # Get all base names from all channels for this class
        all_base_names = get_all_base_names_from_channels(channel_paths, class_name)
        
        if not all_base_names:
            print(f"  No images found for class {class_name}")
            continue
        
        print(f"  Total unique base images: {len(all_base_names)}")
        
        # Shuffle base names
        random.shuffle(all_base_names)
        
        # Calculate split
        total_base_count = len(all_base_names)
        train_base_count = int(total_base_count * train_ratio)
        
        # Split base names
        train_base_names = set(all_base_names[:train_base_count])
        val_base_names = set(all_base_names[train_base_count:])
        
        print(f"  Train base images: {len(train_base_names)}")
        print(f"  Val base images: {len(val_base_names)}")
        
        # Process each channel
        channel_stats = {}
        for channel_name, channel_path in channel_paths.items():
            print(f"    Processing {channel_name} channel...")
            
            class_dir_path = channel_path / class_name
            if not class_dir_path.exists():
                print(f"      Warning: {class_dir_path} does not exist")
                continue
            
            # Get all files in this channel/class
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
            files = [f for f in class_dir_path.iterdir() 
                    if f.is_file() and f.suffix.lower() in image_extensions]
            
            # Group files by base name
            file_groups = group_files_by_base(files)
            
            # Copy files based on train/val split
            train_file_count = 0
            val_file_count = 0
            
            for base_name, group_files in file_groups.items():
                if base_name in train_base_names:
                    # Copy to train
                    for file_path in group_files:
                        dest_path = train_dirs[channel_name] / class_name / file_path.name
                        shutil.copy2(file_path, dest_path)
                        train_file_count += 1
                elif base_name in val_base_names:
                    # Copy to val
                    for file_path in group_files:
                        dest_path = val_dirs[channel_name] / class_name / file_path.name
                        shutil.copy2(file_path, dest_path)
                        val_file_count += 1
            
            channel_stats[channel_name] = {
                'total_files': len(files),
                'train_files': train_file_count,
                'val_files': val_file_count
            }
            
            print(f"      Files: {len(files)} total, {train_file_count} train, {val_file_count} val")
        
        # Update total stats (using first channel as reference)
        first_channel = list(channel_paths.keys())[0]
        if first_channel in channel_stats:
            stats = channel_stats[first_channel]
            total_stats['groups'] += total_base_count
            total_stats['files'] += stats['total_files']
            total_stats['train_groups'] += len(train_base_names)
            total_stats['train_files'] += stats['train_files']
            total_stats['val_groups'] += len(val_base_names)
            total_stats['val_files'] += stats['val_files']
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"MULTI-CHANNEL DATASET SPLIT SUMMARY")
    print(f"{'='*70}")
    print(f"Channels processed: {list(channel_paths.keys())}")
    print(f"Total unique base images: {total_stats['groups']}")
    print(f"")
    print(f"Train:")
    print(f"  Base images: {total_stats['train_groups']} ({total_stats['train_groups']/total_stats['groups']*100:.1f}%)")
    print(f"  Files per channel: ~{total_stats['train_files']}")
    print(f"")
    print(f"Val:")
    print(f"  Base images: {total_stats['val_groups']} ({total_stats['val_groups']/total_stats['groups']*100:.1f}%)")
    print(f"  Files per channel: ~{total_stats['val_files']}")
    print(f"")
    print(f"Output structure:")
    for channel_name in channel_paths.keys():
        print(f"  {channel_name}/")
        print(f"    train/ -> {train_dirs[channel_name].absolute()}")
        print(f"    val/   -> {val_dirs[channel_name].absolute()}")


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
    parser = argparse.ArgumentParser(description="Split multi-channel augmented dataset")
    parser.add_argument("--original_path", type=str, required=True,
                       help="/Users/vantrang/Desktop/BME Design/BME Design III/dataset/original")
    parser.add_argument("--highpass_path", type=str, required=True,
                       help="/Users/vantrang/Desktop/BME Design/BME Design III/dataset/highpass")
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
    
    # Check if paths exist
    if not os.path.exists(args.original_path):
        print(f"Error: Original path '{args.original_path}' does not exist!")
        return
    
    if not os.path.exists(args.highpass_path):
        print(f"Error: Highpass path '{args.highpass_path}' does not exist!")
        return
    
    # Prepare channel paths
    channel_paths = {
        'original': args.original_path,
        'highpass': args.highpass_path
    }
    
    print(f"Original dataset: {args.original_path}")
    print(f"Highpass dataset: {args.highpass_path}")
    print(f"Output path: {args.output_path}")
    print(f"Train ratio: {args.train_ratio} (of base images)")
    print(f"Val ratio: {args.val_ratio} (of base images)")
    print(f"Random seed: {args.seed}")
    print(f"\nNote: Both channels will be split consistently")
    print(f"      Same base images will go to train/val in both channels")
    
    # Confirm before proceeding
    response = input("\nProceed with multi-channel dataset split? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("Operation cancelled.")
        return
    
    # Split dataset
    split_multichannel_dataset(
        channel_paths=channel_paths,
        output_path=args.output_path,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed
    )


if __name__ == "__main__":
    main()