import os
import copy
import torch
import shutil
import importlib
import numpy as np
from metrics import accuracy_score, confusion_matrix, sensitivity_score, specificity_score, f1_score


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def load_config(config_filename):
    config_path = "configs.{}".format(config_filename.split('.')[0])
    module = importlib.import_module(config_path)
    return module.Config()


def splitprint():
    print("#"*100)


def runid_checker(opts, if_syn=False):
    rootpath = opts.train_collection
    if if_syn:
        rootpath = opts.syn_collection
    valset_name = os.path.split(opts.val_collection)[-1]
    config_filename = opts.model_configs
    run_id = opts.run_id
    target_path = os.path.join(rootpath, "models", valset_name, config_filename, "run_" + str(run_id))
    if os.path.exists(target_path):
        if opts.overwrite:
            shutil.rmtree(target_path)
        else:
            print("'{}' exists!".format(target_path))
            return False
    os.makedirs(target_path)
    print("checkpoints are saved in '{}'".format(target_path))
    return True


def predict_dataloader(model, loader, device, net_name="mm-model", if_test=False):
    model.eval()
    predicts = []
    scores = []
    expects = []
    imagename_list = []
    for i, (inputs, labels_onehot, imagenames) in enumerate(loader):
        if if_test:
            label = None
        else:
            label = torch.from_numpy(np.argmax(labels_onehot.cpu().numpy(), axis=1).astype(np.int64))
        with torch.no_grad():
            if net_name == "mm-model":
                outputs = model(inputs[0].to(device), inputs[1].to(device))
            elif net_name == "single-model" or net_name == "sm-model":
                outputs = model(inputs.to(device))
            elif net_name == "three-model":
                outputs = model(inputs[0].to(device), inputs[1].to(device), inputs[2].to(device))
            elif net_name == "four-model":
                outputs = model(inputs[0].to(device), inputs[1].to(device), inputs[2].to(device), inputs[3].to(device))         
            elif net_name == "segment2s-model":
                outputs = model(inputs[0].to(device), inputs[1].to(device))   
        output = np.squeeze(torch.softmax(outputs, dim=1).cpu().numpy())
        predicts.append(np.argmax(output))
        scores.append(np.max(output))
        if not if_test:
            expects.append(label.numpy())
        imagename_list.append(np.squeeze(imagenames))
    if if_test:
        return predicts, scores, imagename_list
    return predicts, scores, expects


def batch_eval(predicts, expects, cls_num=24, verbose=False):
    """
    Evaluation for multi-class chromosome classification
    """
    def multi_to_binary(Y, pos_cls_idx):
        Y_cls = copy.deepcopy(np.array(Y))
        pos_idx = np.where(np.array(Y) == pos_cls_idx)
        neg_idx = np.where(np.array(Y) != pos_cls_idx)
        Y_cls[neg_idx] = 0
        Y_cls[pos_idx] = 1
        return Y_cls

    metrics = {"overall": {}}
    
    # Add metrics for each chromosome class
    for i in range(cls_num):
        metrics[f"chr_{i+1}"] = {}
    
    # Overall metrics
    metrics["overall"]["accuracy"] = accuracy_score(expects, predicts)
    metrics["overall"]["confusion_matrix"] = confusion_matrix(expects, predicts)
    
    # Per-class metrics (one-vs-rest approach)
    class_f1_scores = []
    for cls_idx in range(cls_num):
        cls_name = f"chr_{cls_idx+1}"
        predicts_cls = multi_to_binary(predicts, cls_idx)
        expects_cls = multi_to_binary(expects, cls_idx)
        
        try:
            sen = sensitivity_score(expects_cls, predicts_cls)
            spe = specificity_score(expects_cls, predicts_cls)
            f1 = f1_score(sen, spe)
        except:
            # Handle cases where class doesn't appear in validation set
            sen, spe, f1 = 0.0, 0.0, 0.0
            
        metrics[cls_name]["sensitivity"] = sen
        metrics[cls_name]["specificity"] = spe
        metrics[cls_name]["f1_score"] = f1
        class_f1_scores.append(f1)
    
    # Overall F1 score (macro average)
    metrics["overall"]["f1_score"] = np.mean(class_f1_scores)

    if verbose:
        print("Chromosome Classification Results:")
        print("-" * 60)
        print(f"Overall Accuracy: {metrics['overall']['accuracy']:.4f}")
        print(f"Overall F1 Score: {metrics['overall']['f1_score']:.4f}")
        print("-" * 60)
        
        # Print top 5 and bottom 5 performing classes
        f1_with_class = [(f1, i+1) for i, f1 in enumerate(class_f1_scores)]
        f1_with_class.sort(reverse=True)
        
        print("Top 5 performing chromosome classes:")
        for f1, cls_num in f1_with_class[:5]:
            print(f"Chromosome {cls_num}: F1={f1:.4f}")
        
        print("\nBottom 5 performing chromosome classes:")
        for f1, cls_num in f1_with_class[-5:]:
            print(f"Chromosome {cls_num}: F1={f1:.4f}")
        
        print(f"\nConfusion Matrix:\n{metrics['overall']['confusion_matrix']}")
        
    return metrics