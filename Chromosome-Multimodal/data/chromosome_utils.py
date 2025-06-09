import os


def join_path(collection_path, sub_path, file):
    return os.path.join(collection_path, sub_path, file)


def load_labelfile(filepath):
    with open(filepath, "r") as fp:
        lines = fp.readlines()
    labels_list = [int(line.strip().split(" ")[-1]) for line in lines]
    return labels_list


def load_pathfile(collection, moda, filepath):
    with open(filepath, "r") as fp:
        lines = fp.readlines()
    imgs_path_list = [os.path.join(collection, 'ImageData', moda, line.strip() + '.png') for line in lines]
    return imgs_path_list


def get_chrsmid(name):
    """
    Get chromosome sample ID from image filename
    For chromosome data where original and highpass are different samples,
    this is mainly used for consistency with the multimodal framework
    
    Examples:
    - orig_1_97002023.16.tiff33652998_1.png → orig_1_97002023.16.tiff33652998_1
    - hp_1_97002023.16.tiff33652998_1_hp.png → hp_1_97002023.16.tiff33652998_1
    """
    # Remove file extension
    base_name = name.replace('.png', '').replace('.jpg', '')
    
    # For this chromosome dataset, since original and highpass are different samples,
    # we just return the full filename as ID (this is mainly for framework compatibility)
    return base_name


def get_chrsmid_batch(imgs_path_list):
    """get chromosome sample IDs for pairing chromosome images"""
    chrsmids_list = []
    for item in imgs_path_list:
        chrsmids_list.append(get_chrsmid(os.path.split(item)[-1]))
    return chrsmids_list


def get_impath(img_id, preprocess=None, data_path='dataset/'):
    """
    Get image path for chromosome data
    data_path should point to the processed dataset folder (e.g., 'dataset/')
    """
    if preprocess is None:
        # Determine preprocess type from img_id prefix
        preprocess = 'original-image' if img_id.startswith('orig_') else 'highpass-image'
    return os.path.join(data_path, 'ImageData', preprocess, '%s.png' % img_id)


def read_imset(dataset, modality, data_path='dataset/'):
    """
    Read image set for chromosome data
    modality should be 'original' or 'highpass'
    data_path should point to the processed dataset folder (e.g., 'dataset/')
    """
    imset_file = os.path.join(data_path, dataset, 'ImageSets', '%s.txt' % modality)
    imset = list(map(str.strip, open(imset_file).readlines()))
    return imset


# Test function to verify chrsmid extraction
def test_chrsmid_extraction():
    """Test function to verify chrsmid extraction works correctly"""
    test_cases = [
        "orig_1_97002429.9.tiff255037118_1_rdrotate.png",
        "orig_10_98000056.11.tiff4962352266_20_rotate90.png", 
        "hp_1_98000121.10.tiff383124134_1_rotate180_hp.png",
        "hp_10_97002448.2.tiff4952272679_20_rr31-90vflip_hp.png"
    ]
    
    print("Testing chrsmid extraction:")
    for filename in test_cases:
        chrsmid = get_chrsmid(filename)
        print(f"{filename} → {chrsmid}")
    
    print("Chrsmid extraction completed (no pairing needed for this dataset)")


if __name__ == "__main__":
    test_chrsmid_extraction()