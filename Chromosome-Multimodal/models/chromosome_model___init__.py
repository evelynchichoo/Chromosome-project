import numpy as np
import torch
import os
import torch.nn as nn
from . import resnet
from . import multimodal_resnet
from torch.nn.parallel import DataParallel

##################################################################################################################
def init_two_stream_resnet34(fc_ins=1024, num_classes=24, pretrained=True, heatmap=False):  # Changed to 24 classes
    model1 = resnet.resnet34(pretrained=pretrained, heatmap=heatmap, feature_extracting=True)
    model1.avgpool.kernel_size = 7  # Adjusted for 224x224 input
    model2 = resnet.resnet34(pretrained=pretrained, heatmap=heatmap, feature_extracting=True)
    model2.avgpool.kernel_size = 7  # Adjusted for 224x224 input

    fc_inchannel = model1.fc.in_features
    model1.fc = nn.Linear(fc_inchannel, num_classes)
    fc_inchannel = model2.fc.in_features
    model2.fc = nn.Linear(fc_inchannel, num_classes)

    twostream_model = multimodal_resnet.CombineNet_linear_concatenate(
        model1, model2, fc_ins, num_classes=num_classes, heatmap=heatmap)

    return twostream_model

def load_two_stream_model(configs, device, checkpoint=None):
    use_gpu = "cpu" != device.type
      
    if checkpoint:
        print("load checkpoint '{}'".format(checkpoint))
        model = init_two_stream_resnet34(pretrained=False, heatmap=configs.heatmap, num_classes=configs.cls_num)
        if use_gpu:
            model = model.to(device)
            model.load_state_dict(torch.load(checkpoint, map_location="cuda:{}".format(device.index)))        
        else:
            model.load_state_dict(torch.load(checkpoint, map_location="cpu"))
    else:
        model = init_two_stream_resnet34(pretrained=True, heatmap=configs.heatmap, num_classes=configs.cls_num)
        if use_gpu:
            model = model.to(device)
    return model

####################################################################################################################

def save_model(model_state, opts, epoch, best_metric, best_model=False, best_epoch=-1, if_syn=False):
    rootpath = opts.train_collection
    if if_syn:
        rootpath = opts.syn_collection
    valset_name = os.path.split(opts.val_collection)[-1]
    config_filename = opts.model_configs
    run_id = opts.run_id
    path = os.path.join(rootpath, "models", valset_name, config_filename, "run_" + str(run_id))
    os.makedirs(path, exist_ok=True)  # Ensure directory exists
    save_filename = "checkpoint_epoch{epoch}_{metric:.4f}.pth".format(epoch=epoch, metric=best_metric)
    if best_model:
        save_filename = "best_epoch{epoch}_{metric:.4f}.pth".format(epoch=best_epoch, metric=best_metric)
    torch.save(model_state, os.path.join(path, save_filename))

def predict(model, input):
    with torch.no_grad():
        try:
            output, fm = model.forward(input)
        except (TypeError):
            output, fm_orig, fm_hp = model.forward(input[0], input[1])
    scores = np.squeeze(torch.softmax(output, dim=1).cpu().numpy())  # Changed to softmax for multi-class
    return scores
####################################################################################################################