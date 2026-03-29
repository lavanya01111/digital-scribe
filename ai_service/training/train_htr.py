# train_htr.py
# Fine-tunes TrOCR on your EMNIST word images.
# Run from inside ai_service/ folder:
#   python training/train_htr.py

from transformers import (
    TrOCRProcessor,
    VisionEncoderDecoderModel,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    default_data_collator,
)
from torch.utils.data import Dataset
from PIL import Image
import json
import torch
import os

print("=" * 50)
print("TrOCR Fine-Tuning Script")
print("=" * 50)

# ─── CHECK GPU ───
# Training on GPU (CUDA) is much faster than CPU.
# If you don't have a GPU, it will still work — just slower.
if torch.cuda.is_available():
    print(f"GPU found: {torch.cuda.get_device_name(0)}")
else:
    print("No GPU found — training on CPU (will be slow, but works)")

print()

# ─── CUSTOM DATASET CLASS ───
class EMNISTWordDataset(Dataset):
    """
    Custom PyTorch Dataset that reads from our labels.json file.
    
    Each item returns:
      - pixel_values : the image as a tensor the model can read
      - labels       : the tokenized ground truth text
    """

    def __init__(self, labels_file, processor, max_target_length=32):
        """
        labels_file      : path to labels.json
        processor        : TrOCRProcessor (handles image + text tokenization)
        max_target_length: max number of tokens for the text label
                           32 is enough for short words
        """
        print(f"Loading labels from: {labels_file}")
        with open(labels_file, 'r') as f:
            self.samples = json.load(f)

        self.processor = processor
        self.max_target_length = max_target_length
        print(f"Loaded {len(self.samples)} samples")

    def __len__(self):
        # PyTorch needs this to know how many items are in the dataset
        return len(self.samples)

    def __getitem__(self, idx):
        """
        Called by the DataLoader for each training step.
        Returns one image-label pair, preprocessed and ready for the model.
        """
        sample = self.samples[idx]

        # ── Load image ──
        # Our images are grayscale (1 channel) from EMNIST
        # TrOCR expects RGB (3 channels) — so we duplicate the channel 3 times
        image = Image.open(sample['image']).convert('L')   # load as grayscale
        image = Image.merge('RGB', [image, image, image])  # make it RGB

        # ── Process image → tensor ──
        # TrOCRProcessor resizes, normalizes, and converts to tensor
        pixel_values = self.processor(
            images=image,
            return_tensors='pt'   # 'pt' means PyTorch tensor
        ).pixel_values.squeeze()  # remove the batch dimension (we handle batches in DataLoader)

        # ── Tokenize the ground truth text ──
        # The model outputs token IDs, so we need to convert
        # the text label into token IDs for computing the loss
        labels = self.processor.tokenizer(
            sample['text'],
            padding='max_length',           # pad shorter texts to max_target_length
            max_length=self.max_target_length,
            truncation=True,                # cut off anything longer than max_length
            return_tensors='pt'
        ).input_ids.squeeze()

        # ── Replace padding token with -100 ──
        # The trainer ignores positions where labels == -100 when computing loss
        # This means padding doesn't affect training — only real characters do
        padding_token_id = self.processor.tokenizer.pad_token_id
        labels[labels == padding_token_id] = -100

        return {
            'pixel_values': pixel_values,
            'labels': labels
        }


# ─── LOAD PROCESSOR AND MODEL ───
print("Loading TrOCR processor and model from HuggingFace...")
print("(This downloads ~400MB the first time — cached after that)")
print()

MODEL_NAME = "microsoft/trocr-base-handwritten"

processor = TrOCRProcessor.from_pretrained(MODEL_NAME)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)

print("Model loaded!\n")

# ─── CONFIGURE SPECIAL TOKENS ───
# These tell the model where to start and stop generating text
# The decoder is a language model (GPT-2 style) that generates tokens one by one
# It needs to know: "start here" and "stop here"
model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.eos_token_id = processor.tokenizer.sep_token_id

# ── Beam search settings ──
# During inference (prediction), the model uses beam search to find the best text
# num_beams=4 means it tries 4 different sequences and picks the best one
model.generation_config.early_stopping       = True
model.generation_config.no_repeat_ngram_size = 3
model.generation_config.length_penalty       = 2.0
model.generation_config.num_beams            = 4


# ─── LOAD DATASET ───
# Check that labels.json exists before trying to load it
labels_path = 'data/labels.json'
if not os.path.exists(labels_path):
    print(f"ERROR: {labels_path} not found!")
    print("Please run: python training/prepare_emnist.py first")
    exit(1)

# Load all samples
with open(labels_path) as f:
    all_samples = json.load(f)

print(f"Total labeled samples found: {len(all_samples)}")

# --- CPU FAST MODE ---
print("\n[CPU FAST MODE ENABLED]")
print("Reducing dataset to just 200 images so training finishes in ~5-10 minutes.")
all_samples = all_samples[:200]
# ---------------------

print(f"Total samples using for training: {len(all_samples)}")

# ── Split into train and validation sets ──
# We use 90% for training and 10% for validation
# Validation lets us monitor if the model is overfitting
split_idx = int(len(all_samples) * 0.9)

train_samples = all_samples[:split_idx]
val_samples   = all_samples[split_idx:]

print(f"Train samples : {len(train_samples)}")
print(f"Val samples   : {len(val_samples)}")
print()

# Save split samples to temporary files for the Dataset class
with open('data/train_split.json', 'w') as f:
    json.dump(train_samples, f)

with open('data/val_split.json', 'w') as f:
    json.dump(val_samples, f)

# Create Dataset objects
train_dataset = EMNISTWordDataset('data/train_split.json', processor)
val_dataset   = EMNISTWordDataset('data/val_split.json',   processor)


# ─── TRAINING ARGUMENTS ───
# These control HOW the training runs.
# FIX: 'evaluation_strategy' renamed to 'eval_strategy' in transformers >= 4.36

print("Setting up training arguments...")

training_args = Seq2SeqTrainingArguments(
    output_dir="models_saved/trocr_fine_tuned",
    num_train_epochs=1,                 # CPU: Reduced from 5 to 1
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    learning_rate=5e-5,
    logging_steps=5,                    # CPU: Log every 5 steps so we see progress fast
    evaluation_strategy="epoch",        # Using older name to avoid IDE warnings
    save_strategy="epoch",
    save_total_limit=2,
    load_best_model_at_end=True,
    predict_with_generate=False,        # CPU: Text generation during validation is EXTREMELY slow, so disable it
    fp16=torch.cuda.is_available(),
    report_to="none",
    dataloader_num_workers=0,
)


# ─── CREATE TRAINER ───
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=default_data_collator,  # handles batching automatically
)


# ─── START TRAINING ───
print()
print("=" * 50)
print("Starting training...")
print("You will see loss printed every 50 steps.")
print("Lower loss = model is learning. Aim for < 0.5")
print("=" * 50)
print()

trainer.train()

# ─── SAVE FINAL MODEL ───
print()
print("Saving final model...")
save_path = "models_saved/trocr_fine_tuned"
trainer.save_model(save_path)
processor.save_pretrained(save_path)   # save processor too — needed for inference

print()
print("=" * 50)
print(f"Training complete! Model saved to: {save_path}")
print("Next step: run python training/evaluate.py")
print("=" * 50)