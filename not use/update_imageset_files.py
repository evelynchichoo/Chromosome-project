# create_imageset_simple.py
import os
import sys

def create_imageset_files(imageset_path):
    """
    Simple script to create original.txt and highpass.txt
    
    Args:
        imageset_path: Path to ImageSets folder containing original/ and highpass/
    """
    
    # Check if path exists
    if not os.path.exists(imageset_path):
        print(f"Error: Path does not exist: {imageset_path}")
        return
    
    # Image extensions
    image_exts = ('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')
    
    # Process original folder
    original_folder = os.path.join(imageset_path, "original")
    original_images = []
    
    if os.path.exists(original_folder):
        for chr_num in range(1, 25):
            chr_folder = os.path.join(original_folder, str(chr_num))
            if os.path.exists(chr_folder):
                for filename in sorted(os.listdir(chr_folder)):
                    if filename.lower().endswith(image_exts):
                        # Save as: original/1/filename.jpg
                        original_images.append(f"original/{chr_num}/{filename}")
                        
    # Process highpass folder  
    highpass_folder = os.path.join(imageset_path, "highpass")
    highpass_images = []
    
    if os.path.exists(highpass_folder):
        for chr_num in range(1, 25):
            chr_folder = os.path.join(highpass_folder, str(chr_num))
            if os.path.exists(chr_folder):
                for filename in sorted(os.listdir(chr_folder)):
                    if filename.lower().endswith(image_exts):
                        # Save as: highpass/1/filename.jpg
                        highpass_images.append(f"highpass/{chr_num}/{filename}")
    
    # Write original.txt
    original_txt = os.path.join(imageset_path, "original.txt")
    with open(original_txt, 'w') as f:
        for img_path in original_images:
            f.write(img_path + '\n')
    
    print(f"Created: {original_txt}")
    print(f"Total original images: {len(original_images)}")
    
    # Write highpass.txt
    highpass_txt = os.path.join(imageset_path, "highpass.txt")
    with open(highpass_txt, 'w') as f:
        for img_path in highpass_images:
            f.write(img_path + '\n')
            
    print(f"Created: {highpass_txt}")
    print(f"Total highpass images: {len(highpass_images)}")


if __name__ == "__main__":
    # Get path from command line or use default
    if len(sys.argv) > 1:
        imageset_path = sys.argv[1]
    else:
        imageset_path = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/ImageSets"
    
    create_imageset_files(imageset_path)