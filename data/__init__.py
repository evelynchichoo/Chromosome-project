import os
import numpy as np
import torch
import cv2 as cv
from . import augmentation


def load_image(img_path, configs):
    """
    Load and preprocess an image from a given path
    """
    raw_img = cv.imread(img_path)
    img = (raw_img / 255.).astype(np.float32)
    # pre-process
    myAug = augmentation.OurAug(configs.aug_params["augmentation"])
    img = myAug.process(img)
    img = configs.transform(img)
    img = torch.unsqueeze(img, dim=0)
    return raw_img, img


def read_imset(dataset, modality, data_path=r'/Users/vantrang/Desktop/BME Design/BME Design III/dataset'):
    """
    Read image set file and return a list of image IDs
    """
    # Path to the txt file that have the ids
    imset_file = os.path.join(data_path, 'ImageSets', f'{modality}.txt')
    imset = list(map(str.strip, open(imset_file).readlines()))
    return imset


def get_impath(img_id, preprocess=None, data_path= r'/Users/vantrang/Desktop/BME Design/BME Design III/dataset'):
    """
    Get the full path to an image based on its ID
    """
    if preprocess is None: # use default
        if img_id.endswith('_hp'):
            preprocess = 'highpass'  
        else: 
            preprocess = 'original'  

# Extract folder number from the image ID (assuming format like "1_123.jpg")
    folder_num = img_id.split('_')[0]
    
    # Construct the full path to the image
    return os.path.join(data_path, preprocess, folder_num, f'{img_id}.jpg')
