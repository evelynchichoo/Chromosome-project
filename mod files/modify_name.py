import os
import re

def rename_files_in_dataset(root_folder):
    """
    Đổi tên các file từ dạng 'name.jpg_suffix.jpg' thành 'name_suffix.jpg'
    
    Args:
        root_folder (str): Đường dẫn đến thư mục gốc chứa các folder 1-24
    """
    
    # Kiểm tra thư mục root có tồn tại không
    if not os.path.exists(root_folder):
        print(f"Thư mục {root_folder} không tồn tại!")
        return
    
    total_renamed = 0
    
    # Duyệt qua các folder từ 1 đến 24
    for folder_num in range(1, 25):
        folder_path = os.path.join(root_folder, str(folder_num))
        
        if not os.path.exists(folder_path):
            print(f"Thư mục {folder_path} không tồn tại, bỏ qua...")
            continue
            
        print(f"Đang xử lý thư mục: {folder_path}")
        folder_renamed = 0
        
        # Duyệt qua tất cả file trong folder
        for filename in os.listdir(folder_path):
            # Kiểm tra pattern: tên.jpg_suffix.jpg
            if re.match(r'.*\.jpg.*\.jpg$', filename, re.IGNORECASE):
                # Tách phần tên và phần extension
                # Pattern: name.jpg_suffix.jpg -> name_suffix.jpg
                new_filename = re.sub(r'\.jpg([^.]*\.jpg)$', r'\1', filename, flags=re.IGNORECASE)
                
                # Đường dẫn đầy đủ
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_filename)
                
                try:
                    # Kiểm tra file mới có tồn tại chưa
                    if os.path.exists(new_path):
                        print(f"  CẢNH BÁO: File {new_filename} đã tồn tại, bỏ qua {filename}")
                        continue
                    
                    # Đổi tên file
                    os.rename(old_path, new_path)
                    print(f"  ✓ {filename} -> {new_filename}")
                    folder_renamed += 1
                    total_renamed += 1
                    
                except OSError as e:
                    print(f"  ✗ Lỗi khi đổi tên {filename}: {e}")
        
        print(f"Đã đổi tên {folder_renamed} file trong folder {folder_num}")
        print("-" * 50)
    
    print(f"\nHoàn thành! Tổng cộng đã đổi tên {total_renamed} file.")

def preview_changes(root_folder):
    """
    Xem trước những thay đổi sẽ được thực hiện mà không thực sự đổi tên
    """
    if not os.path.exists(root_folder):
        print(f"Thư mục {root_folder} không tồn tại!")
        return
    
    print("=== XEM TRƯỚC CÁC THAY ĐỔI ===")
    total_files = 0
    
    for folder_num in range(1, 25):
        folder_path = os.path.join(root_folder, str(folder_num))
        
        if not os.path.exists(folder_path):
            continue
            
        folder_files = 0
        print(f"\nThư mục {folder_num}:")
        
        for filename in os.listdir(folder_path):
            if re.match(r'.*\.jpg.*\.jpg$', filename, re.IGNORECASE):
                new_filename = re.sub(r'\.jpg([^.]*\.jpg)$', r'\1', filename, flags=re.IGNORECASE)
                print(f"  {filename} -> {new_filename}")
                folder_files += 1
                total_files += 1
        
        if folder_files == 0:
            print("  (Không có file nào cần đổi tên)")
    
    print(f"\nTổng cộng {total_files} file sẽ được đổi tên.")

# Sử dụng
if __name__ == "__main__":
    # Thay đổi đường dẫn này thành đường dẫn thực tế của dataset
    dataset_path = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/rr31to90vflip_hp"    # Linux/Mac
    
    print("1. Xem trước thay đổi")
    print("2. Thực hiện đổi tên")
    choice = input("Chọn (1/2): ")
    
    if choice == "1":
        preview_changes(dataset_path)
    elif choice == "2":
        confirm = input("Bạn có chắc chắn muốn đổi tên các file? (y/n): ")
        if confirm.lower() == 'y':
            rename_files_in_dataset(dataset_path)
        else:
            print("Đã hủy thao tác.")
    else:
        print("Lựa chọn không hợp lệ!")