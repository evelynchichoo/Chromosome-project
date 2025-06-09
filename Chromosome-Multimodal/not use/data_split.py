import os
import random

def split_dataset(data_dir, train_txt_path, val_txt_path, val_ratio=0.2, seed = 42):
    random.seed(seed)

    image_label_list = []

    # Quet qua 24 folder con
    for label in os.listdir(data_dir):
        label_folder = os.path.join(data_dir, label)
        if not os.path.isdir(label_folder):
            continue
    for img_name in os.listdir(label_folder):
        img_path = os.path.join(label_folder, img_name)
        # luu 'full_path_label'
        image_label_list.append(f"{img_path} {int(label)-1}")

    print(f"Total images found: {len(image_label_list)}")

    random.shuffle(image_label_list)

    # Split train and val
    val_size = int(len(image_label_list) * val_ratio)
    val_list = image_label_list[:val_size]
    train_list = image_label_list[val_size:]

    # Export txt file
    with open(train_txt_path, 'w') as f:
            for item in train_list:
                f.write(f"{item}\n")
    
    with open(val_txt_path, 'w') as f:
            for item in val_list:
                f.write(f"{item}\n")
    
    print(f"Saved {len(train_list)} training samples and {len(val_list)} validation samples.")

if __name__ == "__main__":
    data_dir = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/original"
    split_dataset(
         data_dir,
         train_txt_path="train_list.txt",
         val_txt_path="val_list.txt",
         val_ratio=0.2
    )