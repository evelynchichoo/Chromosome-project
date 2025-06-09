import random

# Đọc ID từ file original và highpass
with open("/Users/vantrang/Desktop/BME Design/BME Design III/dataset/ImageSets/original.txt", "r") as f:
    original_ids = set(line.strip() for line in f if line.strip())

with open("/Users/vantrang/Desktop/BME Design/BME Design III/dataset/ImageSets/highpass.txt", "r") as f:
    highpass_ids = set(line.strip() for line in f if line.strip())

# Chỉ lấy những ID có cả original và highpass
valid_ids = list(original_ids & highpass_ids)

# Shuffle và chia
random.seed(42)
random.shuffle(valid_ids)

split_idx = int(0.8 * len(valid_ids))
train_ids = valid_ids[:split_idx]
val_ids = valid_ids[split_idx:]

# Ghi ra file
with open("train.txt", "w") as f:
    for id in train_ids:
        f.write(id + "\n")

with open("val.txt", "w") as f:
    for id in val_ids:
        f.write(id + "\n")

print(f"Created train.txt ({len(train_ids)} ID) and val.txt ({len(val_ids)} ID)")