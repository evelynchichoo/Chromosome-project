import os
import glob

def create_image_sets(data_path=r'/Users/vantrang/Desktop/BME Design/BME Design III/dataset'):
    """
    Duyệt qua các thư mục original và highpass, lấy danh sách ID ảnh và tạo các file txt
    
    Args:
        data_path: Đường dẫn đến thư mục dataset
    """
    # Tạo thư mục ImageSets nếu chưa tồn tại
    image_sets_dir = os.path.join(data_path, 'ImageSets')
    os.makedirs(image_sets_dir, exist_ok=True)
    
    # Danh sách để lưu trữ IDs
    original_ids = []
    highpass_ids = []
    all_ids = []
    
    # Xử lý original
    original_dir = os.path.join(data_path, 'original')
    for folder in range(1, 25):  # Từ 1 đến 24
        folder_path = os.path.join(original_dir, str(folder))
        if os.path.exists(folder_path):
            # Lấy tất cả file jpg trong thư mục
            for img_path in glob.glob(os.path.join(folder_path, '*.jpg')):
                # Lấy tên file không có phần mở rộng
                img_name = os.path.basename(img_path).split('.')[0]
                # Thêm vào danh sách
                original_ids.append(img_name)
                all_ids.append(img_name)
    
    # Xử lý highpass
    highpass_dir = os.path.join(data_path, 'highpass')
    for folder in range(1, 25):  # Từ 1 đến 24
        folder_path = os.path.join(highpass_dir, str(folder))
        if os.path.exists(folder_path):
            # Lấy tất cả file jpg trong thư mục
            for img_path in glob.glob(os.path.join(folder_path, '*.jpg')):
                # Lấy tên file không có phần mở rộng (tên file đã có _hp)
                img_name = os.path.basename(img_path).split('.')[0]
                # Thêm vào danh sách (không cần thêm _hp vì đã có sẵn)
                highpass_ids.append(img_name)
                all_ids.append(img_name)
    
    # Lưu các danh sách vào file txt
    with open(os.path.join(image_sets_dir, 'original.txt'), 'w') as f:
        f.write('\n'.join(original_ids))
    
    with open(os.path.join(image_sets_dir, 'highpass.txt'), 'w') as f:
        f.write('\n'.join(highpass_ids))
    
    with open(os.path.join(image_sets_dir, 'all.txt'), 'w') as f:
        f.write('\n'.join(all_ids))
    
    print(f"Đã tạo file txt trong thư mục {image_sets_dir}")
    print(f"Số lượng ảnh original: {len(original_ids)}")
    print(f"Số lượng ảnh highpass: {len(highpass_ids)}")
    print(f"Tổng số ảnh: {len(all_ids)}")

if __name__ == "__main__":
    create_image_sets()