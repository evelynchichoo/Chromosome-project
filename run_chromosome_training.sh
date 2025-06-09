#!/bin/bash

# Chromosome Classification Training Script

# Set paths to the PROCESSED dataset (not original data)
# These should point to the train/val folders created by generate_chromosome_dataset_fixed.py
DATASET_PATH="/Users/vantrang/Desktop/BME Design/BME Design III/chromosome-mm/chromosome/code/dataset"
TRAIN_PATH="${DATASET_PATH}/train"
VAL_PATH="${DATASET_PATH}/val"

# Training parameters
MODEL_CONFIG="config-chromosome.py"
RUN_ID=1
DEVICE=0  # GPU ID, use "cpu" for CPU training
NUM_WORKERS=4
PRINT_FREQ=10

# Check if paths exist
if [ ! -d "$TRAIN_PATH" ]; then
    echo "ERROR: Train path does not exist: $TRAIN_PATH"
    echo "Please run generate_chromosome_dataset_fixed.py first to create the dataset structure"
    exit 1
fi

if [ ! -d "$VAL_PATH" ]; then
    echo "ERROR: Val path does not exist: $VAL_PATH"
    echo "Please run generate_chromosome_dataset_fixed.py first to create the dataset structure"
    exit 1
fi

# Create configs directory if it doesn't exist
mkdir -p configs

echo "Starting chromosome classification training..."
echo "Train dataset: $TRAIN_PATH"
echo "Val dataset: $VAL_PATH"
echo "Model config: $MODEL_CONFIG"
echo "Run ID: $RUN_ID"
echo "Device: $DEVICE"

# Run training
python chromosome_train.py \
    --train_collection "${TRAIN_PATH}" \
    --val_collection "${VAL_PATH}" \
    --model_configs "${MODEL_CONFIG}" \
    --run_id ${RUN_ID} \
    --device ${DEVICE} \
    --num_workers ${NUM_WORKERS} \
    --print_freq ${PRINT_FREQ} \
    --overwrite

echo "Training completed!"
echo "Checkpoints saved in: ${TRAIN_PATH}/models/"