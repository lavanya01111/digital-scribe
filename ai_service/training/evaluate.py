# training/evaluate.py
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
from jiwer import cer, wer
import json

print("Loading your fine-tuned model...")
MODEL_PATH = "models_saved/trocr_fine_tuned"
processor = TrOCRProcessor.from_pretrained(MODEL_PATH)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_PATH)
print("Model loaded!\n")

# Load the validation split (last 10% of your data)
with open("data/val_split.json") as f:
    samples = json.load(f)

print(f"Testing on {len(samples)} validation samples...")

ground_truth = []
predictions  = []

for i, sample in enumerate(samples):
    if i % 50 == 0:
        print(f"  {i}/{len(samples)}...")

    # Load the image
    image = Image.open(sample["image"]).convert("L")
    image = Image.merge("RGB", [image, image, image])

    # Run the model
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    predicted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    ground_truth.append(sample["text"])
    predictions.append(predicted_text.strip())

    # Show first 10 predictions so you can see what the model thinks
    if i < 10:
        status = "✓" if predicted_text.strip() == sample["text"] else "✗"
        print(f"  [{status}] Expected: '{sample['text']}'  Got: '{predicted_text.strip()}'")

# Calculate scores
print("\n" + "=" * 40)
print(f"CER (Character Error Rate): {cer(ground_truth, predictions):.4f}")
print(f"WER (Word  Error Rate):     {wer(ground_truth, predictions):.4f}")
print("=" * 40)
print("Good = CER < 0.10, WER < 0.20")
print("Great = CER < 0.05, WER < 0.10")