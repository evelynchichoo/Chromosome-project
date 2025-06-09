import os
import re

def rename_suffix_in_folder(folder_path, old_suffix="_vflip_hp", new_suffix="_rr31-90vflip_hp"):
    """
    Đổi suffix của các file trong folder
    
    Args:
        folder_path (str): Đường dẫn đến folder cần xử lý
        old_suffix (str): Suffix cũ cần thay thế
        new_suffix (str): Suffix mới
    """
    
    # Kiểm tra folder có tồn tại không
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} không tồn tại!")
        return
    
    print(f"Đang xử lý folder: {folder_path}")
    print(f"Đổi suffix từ '{old_suffix}' thành '{new_suffix}'")
    print("-" * 50)
    
    renamed_count = 0
    
    # Duyệt qua tất cả file trong folder
    for filename in os.listdir(folder_path):
        # Kiểm tra file có chứa old_suffix không
        if old_suffix in filename:
            # Tạo tên file mới
            new_filename = filename.replace(old_suffix, new_suffix)
            
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
                renamed_count += 1
                
            except OSError as e:
                print(f"  ✗ Lỗi khi đổi tên {filename}: {e}")
    
    print("-" * 50)
    print(f"Hoàn thành! Đã đổi tên {renamed_count} file.")

def preview_suffix_changes(folder_path, old_suffix="_vflip_hp", new_suffix="_rr31-90vflip_hp"):
    """
    Xem trước những thay đổi sẽ được thực hiện
    """
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} không tồn tại!")
        return
    
    print("=== XEM TRƯỚC CÁC THAY ĐỔI ===")
    print(f"Folder: {folder_path}")
    print(f"Đổi suffix từ '{old_suffix}' thành '{new_suffix}'")
    print("-" * 50)
    
    files_to_rename = []
    
    for filename in os.listdir(folder_path):
        if old_suffix in filename:
            new_filename = filename.replace(old_suffix, new_suffix)
            print(f"  {filename} -> {new_filename}")
            files_to_rename.append((filename, new_filename))
    
    if not files_to_rename:
        print(f"  Không tìm thấy file nào có suffix '{old_suffix}'")
    else:
        print(f"\nTổng cộng {len(files_to_rename)} file sẽ được đổi tên.")
    
    return len(files_to_rename)

def rename_suffix_in_subfolders(rotate_270_folder, old_suffix="_vflip_hp", new_suffix="_rr31-90vflip_hp"):
    """
    Xử lý tất cả file trong các folder con 1-24 của folder rotate_270
    """
    if not os.path.exists(rotate_270_folder):
        print(f"Folder {rotate_270_folder} không tồn tại!")
        return
    
    print(f"Đang xử lý folder: {rotate_270_folder}")
    print(f"Đổi suffix từ '{old_suffix}' thành '{new_suffix}' trong các folder con 1-24")
    print("=" * 60)
    
    total_renamed = 0
    
    # Duyệt qua các folder con từ 1 đến 24
    for folder_num in range(1, 25):
        subfolder_path = os.path.join(rotate_270_folder, str(folder_num))
        
        if not os.path.exists(subfolder_path):
            print(f"Folder {folder_num} không tồn tại, bỏ qua...")
            continue
        
        print(f"\nĐang xử lý folder {folder_num}:")
        folder_renamed = 0
        
        # Duyệt qua tất cả file trong subfolder
        for filename in os.listdir(subfolder_path):
            if old_suffix in filename:
                new_filename = filename.replace(old_suffix, new_suffix)
                
                old_path = os.path.join(subfolder_path, filename)
                new_path = os.path.join(subfolder_path, new_filename)
                
                try:
                    if os.path.exists(new_path):
                        print(f"  CẢNH BÁO: File {new_filename} đã tồn tại, bỏ qua {filename}")
                        continue
                    
                    os.rename(old_path, new_path)
                    print(f"  ✓ {filename} -> {new_filename}")
                    folder_renamed += 1
                    total_renamed += 1
                    
                except OSError as e:
                    print(f"  ✗ Lỗi khi đổi tên {filename}: {e}")
        
        if folder_renamed == 0:
            print(f"  Không có file nào cần đổi tên trong folder {folder_num}")
        else:
            print(f"  Đã đổi tên {folder_renamed} file")
    
    print("=" * 60)
    print(f"Hoàn thành! Tổng cộng đã đổi tên {total_renamed} file.")

def preview_suffix_changes_subfolders(rotate_270_folder, old_suffix="_vflip_hp", new_suffix="_rr31-90vflip_hp"):
    """
    Xem trước thay đổi trong tất cả folder con 1-24
    """
    if not os.path.exists(rotate_270_folder):
        print(f"Folder {rotate_270_folder} không tồn tại!")
        return 0
    
    print("=== XEM TRƯỚC CÁC THAY ĐỔI ===")
    print(f"Folder: {rotate_270_folder}")
    print(f"Đổi suffix từ '{old_suffix}' thành '{new_suffix}' trong các folder con 1-24")
    print("=" * 60)
    
    total_files = 0
    
    for folder_num in range(1, 25):
        subfolder_path = os.path.join(rotate_270_folder, str(folder_num))
        
        if not os.path.exists(subfolder_path):
            continue
        
        folder_files = []
        for filename in os.listdir(subfolder_path):
            if old_suffix in filename:
                new_filename = filename.replace(old_suffix, new_suffix)
                folder_files.append((filename, new_filename))
        
        if folder_files:
            print(f"\nFolder {folder_num}:")
            for old_name, new_name in folder_files:
                print(f"  {old_name} -> {new_name}")
            total_files += len(folder_files)
        else:
            print(f"\nFolder {folder_num}: Không có file nào cần đổi tên")
    
    print("=" * 60)
    print(f"Tổng cộng {total_files} file sẽ được đổi tên.")
    return total_files

# Sử dụng
if __name__ == "__main__":
    # Đường dẫn đến folder rotate_270
    rotate_270_path = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/rr31to90vflip_hp"    # Linux/Mac
    
    print("Chọn phương thức:")
    print("1. Xem trước thay đổi trong tất cả folder con 1-24")
    print("2. Thực hiện đổi tên trong tất cả folder con 1-24")
    print("3. Nhập đường dẫn thủ công")
    
    choice = input("Chọn (1/2/3): ")
    
    if choice == "1":
        preview_suffix_changes_subfolders(rotate_270_path)
        
    elif choice == "2":
        file_count = preview_suffix_changes_subfolders(rotate_270_path)
        if file_count > 0:
            confirm = input(f"\nBạn có chắc chắn muốn đổi tên {file_count} file trong tất cả folder con? (y/n): ")
            if confirm.lower() == 'y':
                rename_suffix_in_subfolders(rotate_270_path)
            else:
                print("Đã hủy thao tác.")
        else:
            print("Không có file nào cần đổi tên.")
        
    elif choice == "3":
        custom_path = input("Nhập đường dẫn đến folder rotate_270: ")
        file_count = preview_suffix_changes_subfolders(custom_path)
        if file_count > 0:
            confirm = input(f"\nBạn có chắc chắn muốn đổi tên {file_count} file? (y/n): ")
            if confirm.lower() == 'y':
                rename_suffix_in_subfolders(custom_path)
            else:
                print("Đã hủy thao tác.")
    
    else:
        print("Lựa chọn không hợp lệ!")