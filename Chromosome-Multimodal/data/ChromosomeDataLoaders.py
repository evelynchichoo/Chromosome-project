# coding: utf-8

import os
import abc
import torch
import pickle
from .ChromosomeDataOrganizer import ChromosomeDataOrganizer


class BaseDataLoader(object):
    def __init__(self, opts, configs):
        self.opts = opts
        self.configs = configs

    @abc.abstractmethod
    def init_trainset_params(self):
        pass

    @abc.abstractmethod
    def init_valset_params(self):
        pass

    @abc.abstractmethod
    def init_testset_params(self):
        pass

    def get_training_dataloader(self):
        print("train set statistics:")
        trainset_params = self.init_trainset_params()
        trainset = self.get_data(**trainset_params)
        # cls balanced dataloader for training
        weights = trainset.label_weights_for_balance()
        sampler = torch.utils.data.sampler.WeightedRandomSampler(
            weights, num_samples=self.configs.train_params["samples_num"], replacement=True)
        train_dataloader = torch.utils.data.DataLoader(
            trainset, batch_size=self.configs.train_params["batch_size"], sampler=sampler,
            num_workers=self.opts.num_workers)
        print("-" * 100)
        print("validation set statistics:")
        valset_params = self.init_valset_params()
        valset = self.get_data(**valset_params)
        valset.label_statistic()
        val_dataloader = torch.utils.data.DataLoader(valset, batch_size=1, num_workers=self.opts.num_workers)
        return train_dataloader, val_dataloader

    def get_test_dataloader(self):
        testset_params = self.init_testset_params()
        testset = self.get_data(**testset_params)
        return torch.utils.data.DataLoader(testset, batch_size=1, num_workers=self.opts.num_workers)


class ChromosomeDataLoader(BaseDataLoader):
    def __init__(self, opts, configs):
        super(ChromosomeDataLoader, self).__init__(opts, configs)
        self.get_data = ChromosomeDataOrganizer.get_mm_data

    def init_trainset_params(self):
        if not self.configs.if_syn:
            self.configs.syn_collection = None
        return {"collection": self.opts.train_collection,
                "aug_params": self.configs.aug_params["augmentation"],
                "transform": self.configs.transform,
                "if_test": False,
                "cls_num": self.configs.cls_num,
                "if_eval": False,
                "loosepair": self.configs.loosepair,
                "if_syn": self.configs.if_syn,
                "syn_collection": self.configs.syn_collection}

    def init_valset_params(self):
        return {"collection": self.opts.val_collection,
                "aug_params": self.configs.aug_params["onlyresize"],
                "transform": self.configs.transform,
                "if_test": False,
                "cls_num": self.configs.cls_num,
                "if_eval": False,
                "loosepair": False,
                "if_syn": False,
                "syn_collection": None}

    def init_testset_params(self, if_test=True, if_eval=False):
        return {"collection": self.opts.test_collection,
                "aug_params": self.configs.aug_params["onlyresize"],
                "transform": self.configs.transform,
                "if_test": if_test,
                "cls_num": self.configs.cls_num,
                "if_eval": if_eval,
                "loosepair": False,
                "if_syn": False,
                "syn_collection": None}

    def init_camgenerating_params(self):
        return {"collection": self.opts.collection,
                "aug_params": self.configs.aug_params["onlyresize"],
                "transform": self.configs.transform,
                "cls_num": self.configs.cls_num}

    @staticmethod
    def get_dataset_for_eval(collection):
        return ChromosomeDataOrganizer.get_mm_data(collection=collection, if_eval=True)