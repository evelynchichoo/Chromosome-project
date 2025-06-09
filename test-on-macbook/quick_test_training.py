#!/usr/bin/env python3
"""
Test script to verify training setup works without running full training
"""

import os
import sys
import torch
import argparse
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("=== Testing Imports ===")
    try:
        from data.ChromosomeDataOrganizer import ChromosomeDataOrganizer
        print("ChromosomeDataOrganizer imported successfully")
        
        from data.ChromosomeDataLoaders import ChromosomeDataLoader
        print("ChromosomeDataLoader imported successfully")
        
        from models import load_two_stream_model, save_model
        print("Models imported successfully")
        
        from chromosome_train_utils import load_config, batch_eval, predict_dataloader
        print("Training utils imported successfully")
        
        return True
    except Exception as e:
        print(f"Import error: {e}")
        return False

def test_config():
    """Test config loading"""
    print("\n=== Testing Config ===")
    try:
        from chromosome_train_utils import load_config
        config = load_config("config_chromosome.py")  # Updated name
        
        print(f"Config loaded successfully")
        print(f"   - Classes: {config.cls_num}")
        print(f"   - Batch size: {config.train_params['batch_size']}")
        print(f"   - Max epochs: {config.train_params['max_epoch']}")
        print(f"   - Loosepair: {config.loosepair}")
        
        return True, config
    except Exception as e:
        print(f"Config error: {e}")
        return False, None

def test_dataset_loading(train_path, val_path, config):
    """Test dataset loading"""
    print("\n=== Testing Dataset Loading ===")
    try:
        # Create mock opts
        class MockOpts:
            def __init__(self):
                self.train_collection = train_path
                self.val_collection = val_path
                self.num_workers = 0  # Use 0 for testing
        
        opts = MockOpts()
        
        # Test ChromosomeDataLoader
        from data.ChromosomeDataLoaders import ChromosomeDataLoader
        data_loader = ChromosomeDataLoader(opts, config)
        
        print("DataLoader created successfully")
        
        # Test data loading (just get the first batch)
        train_loader, val_loader = data_loader.get_training_dataloader()
        
        print(f"Data loaders created successfully")
        print(f"   - Train batches: {len(train_loader)}")
        print(f"   - Val batches: {len(val_loader)}")
        
        # Test getting one batch
        train_iter = iter(train_loader)
        inputs, labels, filenames = next(train_iter)
        
        print(f"First batch loaded successfully")
        print(f"   - Input shapes: {inputs[0].shape}, {inputs[1].shape}")
        print(f"   - Label shape: {labels.shape}")
        print(f"   - Sample filenames: {filenames[0]}")
        
        return True, train_loader, val_loader
    except Exception as e:
        print(f"Dataset loading error: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def test_model_creation(config, device):
    """Test model creation"""
    print("\n=== Testing Model Creation ===")
    try:
        from models import load_two_stream_model
        
        model = load_two_stream_model(config, device, checkpoint=None)
        print(f"Model created successfully")
        print(f"   - Model type: {type(model)}")
        print(f"   - Device: {device}")
        
        # Test model forward pass with dummy data
        dummy_input1 = torch.randn(1, 3, 224, 224).to(device)
        dummy_input2 = torch.randn(1, 3, 224, 224).to(device)
        
        model.eval()
        with torch.no_grad():
            output = model(dummy_input1, dummy_input2)
        
        print(f"Model forward pass successful")
        print(f"   - Output shape: {output.shape}")
        print(f"   - Expected classes: {config.cls_num}")
        
        return True, model
    except Exception as e:
        print(f"Model creation error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_training_step(model, train_loader, device, config):
    """Test one training step"""
    print("\n=== Testing Training Step ===")
    try:
        import torch.nn as nn
        import numpy as np
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.001)
        
        model.train()
        
        # Get one batch
        inputs, labels_onehot, filenames = next(iter(train_loader))
        labels = torch.from_numpy(np.argmax(labels_onehot.cpu().numpy(), axis=1).astype(np.int64))
        
        # Forward pass
        optimizer.zero_grad()
        outputs = model(inputs[0].to(device), inputs[1].to(device))
        loss = criterion(outputs, labels.to(device))
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        print(f"Training step successful")
        print(f"   - Loss: {loss.item():.4f}")
        print(f"   - Output shape: {outputs.shape}")
        
        return True
    except Exception as e:
        print(f"Training step error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_step(model, val_loader, device, config):
    """Test validation step"""
    print("\n=== Testing Validation Step ===")
    try:
        from chromosome_train_utils import predict_dataloader, batch_eval
        
        model.eval()
        
        # Get predictions for a few batches only
        predicts, scores, expects = [], [], []
        for i, (inputs, labels_onehot, filenames) in enumerate(val_loader):
            if i >= 5:  # Only test first 5 batches
                break
                
            import numpy as np
            label = torch.from_numpy(np.argmax(labels_onehot.cpu().numpy(), axis=1).astype(np.int64))
            
            with torch.no_grad():
                outputs = model(inputs[0].to(device), inputs[1].to(device))
            
            output = np.squeeze(torch.softmax(outputs, dim=1).cpu().numpy())
            predicts.append(np.argmax(output))
            scores.append(np.max(output))
            expects.append(label.numpy())
        
        print(f"Validation predictions successful")
        print(f"   - Tested {len(predicts)} samples")
        print(f"   - Sample predictions: {predicts[:5]}")
        print(f"   - Sample expectations: {expects[:5]}")
        
        # Test metrics calculation
        if len(predicts) > 0:
            results = batch_eval(predicts, expects, config.cls_num, verbose=False)
            print(f"Metrics calculation successful")
            print(f"   - Accuracy: {results['overall']['accuracy']:.4f}")
            print(f"   - F1 Score: {results['overall']['f1_score']:.4f}")
        
        return True
    except Exception as e:
        print(f"Validation step error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Paths
    train_path = "dataset/train"
    val_path = "dataset/val"
    
    print("Chromosome Training Setup Test")
    print("=" * 50)
    
    # Check if dataset exists
    if not os.path.exists(train_path):
        print(f"Train path does not exist: {train_path}")
        print("Please run generate_chromosome_dataset_fixed.py first")
        return False
    
    if not os.path.exists(val_path):
        print(f"Val path does not exist: {val_path}")
        print("Please run generate_chromosome_dataset_fixed.py first")
        return False
    
    print(f"Dataset paths exist")
    print(f"   - Train: {train_path}")
    print(f"   - Val: {val_path}")
    
    # Device setup
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    
    # Run tests
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Config
    config_success, config = test_config()
    if config_success:
        tests_passed += 1
    else:
        print("Cannot continue without config")
        return False
    
    # Test 3: Dataset loading
    dataset_success, train_loader, val_loader = test_dataset_loading(train_path, val_path, config)
    if dataset_success:
        tests_passed += 1
    else:
        print("Cannot continue without dataset")
        return False
    
    # Test 4: Model creation
    model_success, model = test_model_creation(config, device)
    if model_success:
        tests_passed += 1
    else:
        print("Cannot continue without model")
        return False
    
    # Test 5: Training step
    if test_training_step(model, train_loader, device, config):
        tests_passed += 1
    
    # Test 6: Validation step
    if test_validation_step(model, val_loader, device, config):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Test Summary: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("ALL TESTS PASSED! Training setup is ready.")
        print("You can now run full training with confidence.")
        return True
    else:
        print("Some tests failed. Please fix the issues before running full training.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)