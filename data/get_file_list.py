import os

root_dir = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset"
target_folder = os.path.join(root_dir, "original")
with open("file_list.txt", "w") as f:
    for dirpath, dirnames, filenames in os.walk(target_folder):
        for fname in filenames:
            if fname.lower().endswith(".jpg"):
                # Tạo đường dẫn tương đối so với root_dir
                rel_path = os.path.relpath(os.path.join(dirpath, fname), root_dir)
                f.write(rel_path + "\n")
