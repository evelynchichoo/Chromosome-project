import os
import shutil

def move_images_from_subfolders(source_folders, destination_root,
                                lower_bound=0, upper_bound=24,
                                image_extensions={'.jpg', '.jpeg', '.png', '.gif', '.bmp'}):
    """
    Di chuyển tất cả các ảnh từ các thư mục con (tên số) của các folder nguồn vào folder đích
    với cấu trúc con tương ứng (chỉ nhận các thư mục có tên số thuộc khoảng lower_bound - upper_bound).
    
    Parameters:
        source_folders (list): Danh sách các folder lớn chứa các thư mục con cần duyệt.
        destination_root (str): Đường dẫn đến folder đích (ví dụ: folder có tên "original").
        lower_bound (int): Giá trị nhỏ nhất của tên folder (mặc định: 0).
        upper_bound (int): Giá trị lớn nhất của tên folder (mặc định: 24).
        image_extensions (set): Các đuôi file của ảnh được chấp nhận.
    """
    # Tạo các thư mục con trong folder đích nếu chưa tồn tại
    for i in range(lower_bound, upper_bound + 1):
        dest_subfolder = os.path.join(destination_root, str(i))
        if not os.path.exists(dest_subfolder):
            os.makedirs(dest_subfolder)
            print(f"Tạo thư mục: {dest_subfolder}")

    # Duyệt qua từng folder lớn nguồn
    for source in source_folders:
        if not os.path.isdir(source):
            print(f"Không tồn tại folder nguồn: {source}")
            continue

        print(f"\nĐang xử lý folder: {source}")
        # Duyệt các thư mục con trực tiếp trong folder nguồn
        for folder_name in os.listdir(source):
            folder_path = os.path.join(source, folder_name)
            # Lọc các thư mục có tên là số và nằm trong khoảng mong muốn
            if os.path.isdir(folder_path) and folder_name.isdigit():
                num = int(folder_name)
                if lower_bound <= num <= upper_bound:
                    dest_folder = os.path.join(destination_root, folder_name)
                    print(f"  -> Xử lý thư mục con: {folder_path}")
                    for file in os.listdir(folder_path):
                        source_file = os.path.join(folder_path, file)
                        if os.path.isfile(source_file):
                            ext = os.path.splitext(file)[1].lower()
                            if ext in image_extensions:
                                dest_file = os.path.join(dest_folder, file)
                                try:
                                    # Nếu file đích đã tồn tại, thêm hậu tố _copy (có thể điều chỉnh theo ý)
                                    if os.path.exists(dest_file):
                                        base, extension = os.path.splitext(file)
                                        dest_file = os.path.join(dest_folder, f"{base}_copy{extension}")
                                    shutil.move(source_file, dest_file)
                                    print(f"    Di chuyển: {source_file} -> {dest_file}")
                                except Exception as e:
                                    print(f"    Lỗi khi di chuyển {source_file}: {e}")

if __name__ == "__main__":
    # Danh sách các folder lớn nguồn (thay đổi đường dẫn theo Mac của bạn)
    source_folders = [
        "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/highpass/val"
    ]
    
    # Đường dẫn đến folder đích (folder 'original')
    destination_folder = "/Users/vantrang/Desktop/BME Design/BME Design III/dataset/val"
    
    move_images_from_subfolders(source_folders, destination_folder)