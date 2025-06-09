from torchvision import transforms


class Config(object):
    modality = "mm"
    net_name = "%s-model" % modality

    cls_num = 24  # 24 chromosome classes

    # CAM
    heatmap = False
    loosepair = True  # Since original and highpass are different samples
    if_syn = False

    # training details
    fine_tuning = False
    if fine_tuning:
        lr = 0.0001
    else:
        lr = 0.001
    checkpoint = ""

    train_params = {
        "optimizer": "sgd",
        "sgd": {
            "lr": lr,
            "lr_decay": 0.5,
            "lr_decay_start": 2,  # Reduced for testing
            "tolerance_iter_num": 2,  # Reduced for testing
            "lr_min": 1e-7,
            "momentum": 0.9,
            "weight_decay": 1e-4
        },
        "samples_num": 50,  # Very small for mini dataset
        "batch_size": 2,    # Very small batch size
        "print_freq": 1,    # Print every batch
        "max_epoch": 2,     # Only 2 epochs for testing
        "best_metric": "f1_score"
    }

    # normalization - adjusted for chromosome images
    transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])  # ImageNet normalization

    # traditional data augmentation (for train) or just resize (for val or test)
    aug_params = {
        "augmentation": {
            "output_shape": [224, 224],  # Standard size
            "rotation": False, "rotation_range": [0, 360],  # All disabled for speed
            "contrast": False, "contrast_range": [0.8, 1.2],
            "brightness": False, "brightness_range": [0.8, 1.2],
            "color": False, "color_range": [0.8, 1.2],
            "multiple_rgb": False, "multiple_range": [0.8, 1.2],
            "flip": False, "flip_prob": 0.5,
            "crop": False, "crop_prob": 0.3,
            "crop_w": 0.02, "crop_h": 0.02,
            "keep_aspect_ratio": True,
            "resize_pad": False,
            "zoom": False, "zoom_prob": 0.3,
            "zoom_range": [0.00, 0.03],
            "paired_transfos": False,
            "rotation_expand": False,
            "crop_height": False,
            "extra_width_crop": False,
            "extra_height_crop": False,
            "crop_after_rotation": False
        },
        "onlyresize": {
            "output_shape": [224, 224],
            "rotation": False, "rotation_range": [0, 360],
            "contrast": False, "contrast_range": [0.8, 1.2],
            "brightness": False, "brightness_range": [0.8, 1.2],
            "color": False, "color_range": [0.8, 1.2],
            "multiple_rgb": False, "multiple_range": [0.8, 1.2],
            "flip": False, "flip_prob": 0.5,
            "crop": False, "crop_prob": 0.3,
            "crop_w": 0.02, "crop_h": 0.02,
            "keep_aspect_ratio": True,
            "resize_pad": False,
            "zoom": False, "zoom_prob": 0.3,
            "zoom_range": [0.00, 0.03],
            "paired_transfos": False,
            "rotation_expand": False,
            "crop_height": False,
            "extra_width_crop": False,
            "extra_height_crop": False,
            "crop_after_rotation": False
        }
    }