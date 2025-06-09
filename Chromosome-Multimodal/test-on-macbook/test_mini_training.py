#!/usr/bin/env python3
"""
Test with mini dataset to avoid memory issues
"""

import os
import sys
import torch
import numpy as np

def test_mini_training():
    print("Mini Dataset Training Test")
    print("=" * 50)
    
    # Check if mini dataset exists
    if not os.path.exists("mini_dataset/train"):
        print("Mini dataset not found. Creating...")
        os.system("python create_mini_dataset.py")
    
    try:
        # Mock args for mini dataset
        class MockArgs:
            def __init__(self):
                self.train_collection = "mini_dataset/train"
                self.val_collection = "mini_dataset/val"
                self.model_configs = "config_chromosome_mini.py"
                self.run_id = 999
                self.device = "cpu"  # Force CPU for testing
                self.num_workers = 0  # No multiprocessing
                self.print_freq = 1
                self.checkpoint = None
                self.overwrite = True
        
        opts = MockArgs()
        
        # Import modules
        from models import load_two_stream_model
        from data.ChromosomeDataLoaders import ChromosomeDataLoader
        from chromosome_train_utils import load_config, runid_checker
        
        print("Imports successful")
        
        # Load config
        configs = load_config(opts.model_configs)
        print(f"Config loaded - {configs.cls_num} classes")
        
        # Check paths
        runid_checker(opts, configs.if_syn)
        print("Path check passed")
        
        # Setup device
        device = torch.device("cpu")  # Force CPU
        print(f"Using device: {device}")
        
        # Load mini dataset
        print("Loading mini dataset...")
        data_initializer = ChromosomeDataLoader(opts, configs)
        train_loader, val_loader = data_initializer.get_training_dataloader()
        print(f"Mini dataset loaded:")
        print(f"   - Train batches: {len(train_loader)}")
        print(f"   - Val batches: {len(val_loader)}")
        
        # Test getting one batch
        print("Testing batch loading...")
        train_iter = iter(train_loader)
        inputs, labels, filenames = next(train_iter)
        print(f"Batch loaded successfully:")
        print(f"   - Input shapes: {inputs[0].shape}, {inputs[1].shape}")
        print(f"   - Labels shape: {labels.shape}")
        
        # Load model
        print("Loading model...")
        model = load_two_stream_model(configs, device, None)
        print("Model loaded successfully")
        
        # Test forward pass
        print("Testing forward pass...")
        model.eval()
        with torch.no_grad():
            outputs = model(inputs[0], inputs[1])
        print(f"Forward pass successful - output shape: {outputs.shape}")
        
        # Test training step
        print("Testing training step...")
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.001)
        
        model.train()
        labels_int = torch.from_numpy(np.argmax(labels.cpu().numpy(), axis=1).astype(np.int64))
        
        optimizer.zero_grad()
        outputs = model(inputs[0], inputs[1])
        loss = criterion(outputs, labels_int)
        loss.backward()
        optimizer.step()
        
        print(f"Training step successful - loss: {loss.item():.4f}")
        
        print("\nALL TESTS PASSED!")
        print("Mini dataset training works. Your setup is ready!")
        return True
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mini_training()
    
    if success:
        print("\nSetup verified with mini dataset!")
        print("You can now run full training on lab machine.")
    else:
        print("\nIssues found. Please fix before full training.")
    
    sys.exit(0 if success else 1)