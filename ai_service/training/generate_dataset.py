import os
import random
import json
import urllib.request
from PIL import Image, ImageDraw, ImageFont

# Set up directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "canvas_synthetic_images")
LABELS_FILE = os.path.join(DATA_DIR, "labels.json")

os.makedirs(IMAGES_DIR, exist_ok=True)

print("=" * 60)
print("Generating Synthetic Canvas Dataset for Digital Scribe")
print("=" * 60)

# 1. Use built-in Windows handwriting fonts
print("Selecting built-in Windows cursive/handwriting fonts...")
font_options = [
    "C:\\Windows\\Fonts\\comic.ttf",     # Comic Sans MS
    "C:\\Windows\\Fonts\\segoepr.ttf",   # Segoe Print
    "C:\\Windows\\Fonts\\inkfree.ttf",   # Ink Free
    "C:\\Windows\\Fonts\\mvboli.ttf"     # MV Boli
]

font_paths = []
# Filter only ones that actually exist on this system
for f in font_options:
    if os.path.exists(f):
        font_paths.append(f)

if not font_paths:
    print("Failed to find any handwriting fonts. Using default Arial.")
    font_paths = ["arial.ttf"]
else:
    print(f"Found {len(font_paths)} handwriting fonts!")

# 2. Easy / Common SLD word list (about 200 words)
WORDS = [
    "the", "of", "and", "a", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on", "are", "as", "with", "his", "they", "I", 
    "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", 
    "there", "use", "an", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about", "out", "many", "then", "them", "these", "so", 
    "some", "her", "would", "make", "like", "him", "into", "time", "has", "look", "two", "more", "write", "go", "see", "number", "no", "way", "could", "people", 
    "my", "than", "first", "water", "been", "call", "who", "oil", "its", "now", "find", "long", "down", "day", "did", "get", "come", "made", "may", "part",
    "over", "new", "sound", "take", "only", "little", "work", "know", "place", "year", "live", "me", "back", "give", "most", "very", "after", "thing", "our", "just",
    "name", "good", "sentence", "man", "think", "say", "great", "where", "help", "through", "much", "before", "line", "right", "too", "mean", "old", "any", "same", "tell",
    "dyslexia", "student", "teacher", "school", "exam", "test", "write", "reading", "learning", "lone", "tone", "bone", "phone", "apple", "banana", "cat", "dog"
]

TOTAL_IMAGES = 5000
labels = []

print(f"\nGenerating {TOTAL_IMAGES} synthetic canvas images to '{IMAGES_DIR}'...")
for i in range(TOTAL_IMAGES):
    word = random.choice(WORDS)
    # Random capitalization to simulate realistic writing
    if random.random() < 0.2:
        word = word.capitalize()
    elif random.random() < 0.05:
        word = word.upper()
        
    font_path = random.choice(font_paths)
    font_size = random.randint(40, 80)
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Create a white canvas tightly fitting the word with padding
    try:
        left, top, right, bottom = font.getbbox(word)
    except AttributeError:
        # Fallback for very old Pillow versions where load_default() had no getbbox
        left, top = 0, 0
        right, bottom = max(len(word) * 15, 60), 60 # approximate size
        
    width = right - left
    height = bottom - top
    
    # Add standard canvas padding (matches what htr_model.py does)
    padding = random.randint(20, 50)
    img_w = max(width + padding * 2, 60)
    img_h = max(height + padding * 2, 60)
    
    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)
    
    # Draw text in pure black 
    draw.text((padding - left, padding - top), word, font=font, fill="black")
    
    # Apply very slight rotation to mimic realistic handwriting tilt
    if random.random() < 0.6:
        angle = random.uniform(-4, 4)
        # Using white fillcolor so background stays white after rotation
        img = img.rotate(angle, fillcolor="white", expand=True)

    # Save
    filename = f"synth_{i:04d}.png"
    filepath = os.path.join(IMAGES_DIR, filename)
    img.save(filepath)
    
    # Record relative image path
    labels.append({
        "image": f"data/canvas_synthetic_images/{filename}",
        "text": word
    })
    
    if i % 1000 == 0 and i > 0:
        print(f"  Generated {i} images...")

# Save labels to labels.json
with open(LABELS_FILE, "w") as f:
    json.dump(labels, f, indent=4)

print("\nDataset generation complete!")
print(f"Total labeled images: {len(labels)}")
print(f"Labels saved to: {LABELS_FILE}")
print("=" * 60)
print("\nYou can now run: python training/train_htr.py to train on this exact canvas data.")
print("=" * 60)
