from .chromosome_utils import *
from .dataset import MultiDataset

class ChromosomeDataOrganizer:
    
    @staticmethod
    def get_mm_data(
            collection, loosepair=False, aug_params=None, transform=None, if_test=False, cls_num=24, if_eval=False,
            if_syn=False, syn_collection=None):
        def pair_sampler(
                imgs_original_path_list, imgs_highpass_path_list, chrsmids_original_list, chrsmids_highpass_list,
                labels_original_list=None, labels_highpass_list=None,
                loosepair=False, if_test=False, if_syn=False):
            """pair original and highpass chromosome images"""
            if if_test:
                loosepair = False
                labels_original_list = [None] * len(imgs_original_path_list)
                labels_highpass_list = [None] * len(imgs_highpass_path_list)
            
            original_zip = list(zip(imgs_original_path_list, chrsmids_original_list, labels_original_list))
            highpass_zip = list(zip(imgs_highpass_path_list, chrsmids_highpass_list, labels_highpass_list))
            
            pairs_path_list = []
            labels_list = []
            
            for path_orig, chrsmid_orig, label_orig in original_zip:
                for path_hp, chrsmid_hp, label_hp in highpass_zip:
                    if loosepair:
                        # For loosepair, match by label (same chromosome class)
                        # Since original and highpass are different samples, we pair by class
                        if label_orig == label_hp:
                            pairs_path_list.append((path_orig, path_hp))
                            labels_list.append(label_orig)
                    else:
                        # For strict pairing, match by chrsmid (same original sample)
                        # Note: This won't work for your data since original and highpass are different samples
                        if chrsmid_orig == chrsmid_hp:
                            pairs_path_list.append((path_orig, path_hp))
                            labels_list.append(label_orig)
            
            if if_test:
                return pairs_path_list, None
            else:
                return pairs_path_list, labels_list

        # Load original images
        path_file_original = join_path(collection, "ImageSets", "original.txt")
        imgs_original_path_list = load_pathfile(collection, "original-image", path_file_original)
        
        # Load highpass images  
        path_file_highpass = join_path(collection, "ImageSets", "highpass.txt")
        imgs_highpass_path_list = load_pathfile(collection, "highpass-image", path_file_highpass)

        # Handle synthetic data if needed
        if if_syn:
            path_file_original_syn = join_path(syn_collection, "ImageSets", "original.txt")
            imgs_original_path_list.extend(load_pathfile(syn_collection, "original-image", path_file_original_syn))
            path_file_highpass_syn = join_path(syn_collection, "ImageSets", "highpass.txt")
            imgs_highpass_path_list.extend(load_pathfile(syn_collection, "highpass-image", path_file_highpass_syn))

        # Get chromosome sample IDs for pairing
        chrsmids_original_list = get_chrsmid_batch(imgs_original_path_list)
        chrsmids_highpass_list = get_chrsmid_batch(imgs_highpass_path_list)

        # Load labels if not testing
        if (not if_test) or if_eval:
            label_file_original = join_path(collection, "annotations", "original.txt")
            labels_original_list = load_labelfile(label_file_original)
            label_file_highpass = join_path(collection, "annotations", "highpass.txt")
            labels_highpass_list = load_labelfile(label_file_highpass)
            
            if if_syn:
                label_file_original_syn = join_path(syn_collection, "annotations", "original.txt")
                labels_original_list.extend(load_labelfile(label_file_original_syn))
                label_file_highpass_syn = join_path(syn_collection, "annotations", "highpass.txt")
                labels_highpass_list.extend(load_labelfile(label_file_highpass_syn))
        else:
            labels_original_list = None
            labels_highpass_list = None

        # Create pairs
        pairs_path_list, labels_list = pair_sampler(
            imgs_original_path_list, imgs_highpass_path_list, 
            chrsmids_original_list, chrsmids_highpass_list, 
            labels_original_list, labels_highpass_list,
            loosepair, if_test, if_syn)

        if if_eval:
            return pairs_path_list, labels_list

        return MultiDataset(pairs_path_list, labels_list, aug_params, transform, if_test, cls_num)