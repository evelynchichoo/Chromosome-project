import os
from pathlib import Path

def test_naming_convention(original_path, highpass_path):
    """Test naming convention to understand the data structure"""
    
    print("=== ANALYZING ORIGINAL DATA ===")
    original_path = Path(original_path)
    for class_folder in sorted(original_path.iterdir())[:3]:  # Check first 3 classes
        if class_folder.is_dir():
            print(f"\nClass {class_folder.name}:")
            files = list(class_folder.glob("*.jpg"))[:5]  # First 5 files
            for f in files:
                print(f"  {f.name}")
    
    print("\n=== ANALYZING HIGHPASS DATA ===")
    highpass_path = Path(highpass_path)
    for class_folder in sorted(highpass_path.iterdir())[:3]:  # Check first 3 classes
        if class_folder.is_dir():
            print(f"\nClass {class_folder.name}:")
            files = list(class_folder.glob("*.jpg"))[:5]  # First 5 files
            for f in files:
                print(f"  {f.name}")

def test_id_extraction():
    """Test các filename examples để xem get_base_chrsmid hoạt động thế nào"""
    
    def get_base_chrsmid(filename):
        # Remove augmentation suffixes
        base = filename.replace("_hflip", "").replace("_vflip", "")
        base = base.replace("_rotate90", "").replace("_rotate180", "").replace("_rotate270", "")
        base = base.replace("_rdrotate", "").replace("_rr31-90vfip", "")
        
        # For generated filenames like "orig_1_97002023.16.tiff33652998_1" or "hp_1_97002023.16.tiff33652998_1"
        # Remove the prefix to get the core identifier
        if base.startswith("orig_"):
            base = base[5:]  # Remove "orig_" prefix
        elif base.startswith("hp_"):
            base = base[3:]   # Remove "hp_" prefix
            
        return base
    
    print("=== TESTING ID EXTRACTION ===")
    
    # Test với naming convention bạn đã cho
    test_cases = [
        # Original files
        "orig_1_97002023.16.tiff33652998_1",
        "orig_1_97002023.16.tiff33652998_1_hflip", 
        "orig_1_97002023.16.tiff33652998_1_rotate90",
        
        # Highpass files  
        "hp_1_97002023.16.tiff33652998_1",
        "hp_1_97002023.16.tiff33652998_1_hflip",
        "hp_1_97002023.16.tiff33652998_1_rotate180",
    ]
    
    for filename in test_cases:
        base_id = get_base_chrsmid(filename)
        print(f"{filename} -> {base_id}")

if __name__ == "__main__":
    # Update với paths thật của bạn
    original_path = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/original"
    highpass_path = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/highpass"
    
    # Check if paths exist
    if os.path.exists(original_path) and os.path.exists(highpass_path):
        test_naming_convention(original_path, highpass_path)
    else:
        print("Paths không tồn tại, chỉ test ID extraction")
    
    test_id_extraction()