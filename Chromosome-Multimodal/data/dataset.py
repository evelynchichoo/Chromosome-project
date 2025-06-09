# dataset.py - Modified for chromosome dataset
import os
import cv2 as cv
import numpy as np
from . import augmentation
from torch.utils.data import Dataset


class BaseDataset(Dataset):
    def __init__(self, aug_params=None, transform=None, if_test=False, cls_num=24):
        self.aug_params = aug_params
        self.transform = transform
        self.if_test = if_test
        self.cls_num = cls_num

    def label_statistic(self):
        cls_count = np.zeros(self.cls_num).astype(np.int64)
        for label in self.labels_list:
            cls_count[label] += 1
        for i in range(self.cls_num):
            # Display as chromosome number (1-24) instead of 0-23
            print("Chromosome {}: {}".format(i+1, cls_count[i]))
        print("Summary: {}".format(np.sum(cls_count)))
        return cls_count

    def label_weights_for_balance(self, C=100.0):
        cls_count = self.label_statistic()
        labels_weight_list = []
        for label in self.labels_list:
            labels_weight_list.append(C/float(cls_count[label]))
        return labels_weight_list


class MultiDataset(BaseDataset):
    """Multi-modal Dataset for Chromosome Images"""
    def __init__(
        self, pairs_path_list, labels_list=None,
        aug_params=None, transform=None, if_test=False, cls_num=24):
        super(MultiDataset, self).__init__(aug_params, transform, if_test, cls_num)
        self.pairs_path_list = pairs_path_list
        if not self.if_test:
            self.labels_list = labels_list
            
    def CLAHE(self, img):
        """Apply CLAHE to enhance contrast"""
        b, g, r = cv.split(img)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        b_equalized = clahe.apply(b)
        g_equalized = clahe.apply(g)
        r_equalized = clahe.apply(r)
        equalized = cv.merge((b_equalized, g_equalized, r_equalized))
        return equalized
    
    def HE(self, img):
        """Apply Histogram Equalization"""
        b, g, r = cv.split(img)
        b_equalized = cv.equalizeHist(b)
        g_equalized = cv.equalizeHist(g)
        r_equalized = cv.equalizeHist(r)
        equalized = cv.merge((b_equalized, g_equalized, r_equalized))
        return equalized
    
    def __getitem__(self, index):
        img_o_path, img_h_path = self.pairs_path_list[index]
        img_o_filename = os.path.split(img_o_path)[-1]
        img_h_filename = os.path.split(img_h_path)[-1]

        # Load original image
        img_o_bgr = cv.imread(img_o_path)
        if img_o_bgr is None:
            raise ValueError(f"Cannot read image: {img_o_path}")
        
        # Handle different image formats (TIFF might have different bit depth)
        if img_o_bgr.dtype == np.uint16:
            img_o_bgr = (img_o_bgr / 65535.0 * 255).astype(np.uint8)
        
        img_o = (img_o_bgr/255.).astype(np.float32)

        # Load highpass filtered image
        img_h_bgr = cv.imread(img_h_path)
        if img_h_bgr is None:
            raise ValueError(f"Cannot read image: {img_h_path}")
            
        if img_h_bgr.dtype == np.uint16:
            img_h_bgr = (img_h_bgr / 65535.0 * 255).astype(np.uint8)
            
        img_h = (img_h_bgr/255.).astype(np.float32)

        # Apply augmentations if specified
        if self.aug_params:
            aug = augmentation.OurAug(self.aug_params)
            img_o = aug.process(img_o)
            aug = augmentation.OurAug(self.aug_params)
            img_h = aug.process(img_h)
            
        # Apply transforms if specified
        if self.transform:
            img_o = self.transform(img_o)
            img_h = self.transform(img_h)

        if not self.if_test:
            label = self.labels_list[index]
            label_onehot = np.zeros(self.cls_num).astype(np.float32)
            label_onehot[label] = 1.
        else:
            label_onehot = -1

        return (img_o, img_h), label_onehot, (img_o_filename, img_h_filename)

    def __len__(self):
        return len(self.pairs_path_list)