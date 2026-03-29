# prepare_emnist.py
# FIXED VERSION — Run this to generate labels.json and all PNG word images.
# Place this file at: ai_service/training/prepare_emnist.py
# Run from inside ai_service/ folder:
#   cd ai_service
#   python training/prepare_emnist.py

import os
import json
import random
import torchvision
import torchvision.transforms as transforms
from PIL import Image

print("=" * 50)
print("STEP 1: Downloading EMNIST dataset...")
print("(Already downloaded? torchvision will skip the download)")
print("=" * 50)

# ─── DOWNLOAD EMNIST ───
# The dataset downloads into ai_service/emnist_data/
# torchvision skips re-downloading if already present
train_dataset = torchvision.datasets.EMNIST(
    root='emnist_data',
    split='letters',    # A-Z letters only (best for text)
    train=True,
    download=True,      # skips download if already done
    transform=transforms.ToTensor()
)

print(f"Dataset ready. Total images: {len(train_dataset)}")
print(f"Number of classes: {len(train_dataset.classes)}")
print(f"Classes: {train_dataset.classes}")

# ─── BUILD LABEL MAP ───
# IMPORTANT FIX: In EMNIST 'letters', the class labels are 1-26, not 0-25
# Class 1 = 'a', Class 2 = 'b', ..., Class 26 = 'z'
# torchvision's .classes attribute gives us ['a','b','c',...,'z']
# But the integer labels in the dataset are 1-based!
# We use train_dataset.classes to build the correct map.

# Build: {1: 'a', 2: 'b', ..., 26: 'z'}
label_map = {}
for i, class_name in enumerate(train_dataset.classes):
    # EMNIST 'letters' stores labels starting from 1
    label_map[i + 1] = class_name.lower()

print(f"\nLabel map (first 5): { {k: v for k, v in list(label_map.items())[:5]} }")
print(f"Label map (last 5):  { {k: v for k, v in list(label_map.items())[-5:]} }")

# ─── CREATE OUTPUT FOLDERS ───
os.makedirs('data/train/images', exist_ok=True)
print("\nCreated folder: data/train/images/")

# ─── SORT ALL IMAGES BY LETTER ───
print("\n" + "=" * 50)
print("STEP 2: Sorting images by letter...")
print("(This may take 1-2 minutes for ~80,000 images)")
print("=" * 50)

# Dictionary: {'a': [PIL_img1, PIL_img2, ...], 'b': [...], ...}
letter_images = {}

for idx in range(len(train_dataset)):
    # Print progress every 10,000 images
    if idx % 10000 == 0:
        print(f"  Processing image {idx}/{len(train_dataset)}...")

    image_tensor, class_label = train_dataset[idx]

    # Look up what letter this class_label means
    letter = label_map.get(int(class_label), None)
    if letter is None:
        continue  # skip unknown labels

    # Convert tensor → PIL Image
    # IMPORTANT: EMNIST images are stored rotated/flipped
    # We must fix orientation or letters will be sideways!
    image_pil = transforms.ToPILImage()(image_tensor)
    image_pil = image_pil.rotate(90)          # rotate to upright
    image_pil = image_pil.transpose(Image.FLIP_LEFT_RIGHT)  # mirror fix

    # Store in our dictionary grouped by letter
    if letter not in letter_images:
        letter_images[letter] = []
    letter_images[letter].append(image_pil)

print(f"\nDone sorting! Letters found: {sorted(letter_images.keys())}")
for letter in sorted(letter_images.keys())[:5]:
    print(f"  '{letter}' has {len(letter_images[letter])} images")


# ─── FUNCTION: STITCH LETTERS INTO A WORD IMAGE ───
def make_word_image(word, letter_images, letter_size=32, padding=6):
    """
    Takes a word like 'hello' and creates one PNG image by
    stitching together individual letter images side by side.

    Parameters:
        word         : the word string, e.g. 'hello'
        letter_images: dict of {'a': [img, img, ...], 'b': [...]}
        letter_size  : height and width of each letter (pixels)
        padding      : space between letters (pixels)

    Returns:
        PIL Image of the full word, or None if a letter is missing.
    """
    letters_needed = list(word.lower())
    letter_imgs_for_word = []

    for char in letters_needed:
        if char not in letter_images or len(letter_images[char]) == 0:
            print(f"  Warning: no images for letter '{char}' in word '{word}' — skipping word")
            return None

        # Pick a RANDOM image of this letter
        # This is important: each 'version' of a word uses different
        # letter samples, so the model sees variety and generalizes better
        chosen_img = random.choice(letter_images[char])

        # Resize to consistent size
        chosen_img = chosen_img.resize((letter_size, letter_size), Image.LANCZOS)
        letter_imgs_for_word.append(chosen_img)

    # Calculate total canvas size
    num_letters = len(letter_imgs_for_word)
    total_width = (letter_size * num_letters) + (padding * (num_letters - 1))
    total_height = letter_size + 10  # a little extra vertical padding

    # Create white background (255 = white in grayscale)
    word_image = Image.new('L', (total_width, total_height), color=255)

    # Paste each letter onto the canvas
    x_pos = 0
    for img in letter_imgs_for_word:
        y_pos = (total_height - letter_size) // 2  # center vertically
        word_image.paste(img, (x_pos, y_pos))
        x_pos += letter_size + padding  # move right for next letter

    return word_image


# ─── WORD LIST ───
# These are the words the model will learn to recognize.
# Add or remove words based on what your students write in exams.
# TIP: Add subject-specific words (science, math, history terms)
WORD_LIST = [
    # Common short words
    "the", "and", "for", "are", "but", "not", "you", "all",
    "can", "her", "was", "one", "our", "out", "day", "get",
    "has", "him", "his", "how", "man", "new", "now", "old",
    "see", "two", "way", "who", "boy", "did", "its", "let",
    "put", "say", "she", "too", "use",

    # Longer common words
    "this", "that", "with", "have", "from", "they", "will",
    "each", "word", "look", "time", "more", "also", "back",
    "call", "come", "come", "down", "find", "give", "good",
    "hand", "here", "high", "just", "know", "last", "left",
    "life", "live", "long", "made", "make", "many", "most",
    "much", "name", "next", "only", "open", "over", "part",
    "play", "read", "same", "seem", "show", "side", "some",
    "such", "take", "tell", "than", "them", "then", "turn",
    "very", "want", "well", "went", "what", "when", "work",
    "year", "your",

    # Dyslexia confusion pairs (commonly reversed/confused)
    # Training on these helps the NLP correction pipeline too
    "was", "saw", "on", "no", "net", "ten", "bad", "dab",
    "dog", "god", "now", "won", "left", "felt", "stop", "tops",
    "star", "rats", "draw", "ward", "step", "pets",

    # Hello world test words (your original sample)
    "hello", "world", "apple", "table", "chair",

    # School/exam words
    "write", "answer", "question", "explain", "describe",
    "because", "example", "which", "where", "there",
    "their", "about", "other", "people", "number",
]

# Remove duplicates while keeping order
seen = set()
WORD_LIST = [w for w in WORD_LIST if not (w in seen or seen.add(w))]
print(f"\nWord list ready: {len(WORD_LIST)} unique words")


# ─── GENERATE WORD IMAGES ───
print("\n" + "=" * 50)
print("STEP 3: Generating word images and labels.json...")
print("=" * 50)

# How many different versions of each word to create
# More versions = better training. 30 is good to start.
VERSIONS_PER_WORD = 30

total_to_generate = len(WORD_LIST) * VERSIONS_PER_WORD
print(f"Will generate: {len(WORD_LIST)} words × {VERSIONS_PER_WORD} versions = {total_to_generate} images")

labels = []       # This list becomes your labels.json
word_count = 0    # Counter for naming image files
skipped = 0       # Count of words we couldn't make

for word in WORD_LIST:
    word_versions_made = 0

    for version in range(VERSIONS_PER_WORD):
        # Create one version of the word image
        word_img = make_word_image(word, letter_images)

        if word_img is None:
            skipped += 1
            break  # Skip all versions of this word if letters are missing

        # Build the file path
        # Example: data/train/images/word_0.png
        filename = f"data/train/images/word_{word_count}.png"

        # Save the PNG file
        word_img.save(filename)

        # Add one entry to labels.json
        labels.append({
            "image": filename,   # ← path to the image
            "text": word         # ← correct spelling (ground truth)
        })

        word_count += 1
        word_versions_made += 1

    # Print progress every 20 words
    if WORD_LIST.index(word) % 20 == 0:
        print(f"  Progress: {WORD_LIST.index(word)+1}/{len(WORD_LIST)} words done... ({word_count} images so far)")

print(f"\nGeneration complete!")
print(f"  Images created : {word_count}")
print(f"  Words skipped  : {skipped} (letters missing from EMNIST)")


# ─── SAVE labels.json ───
print("\n" + "=" * 50)
print("STEP 4: Saving labels.json...")
print("=" * 50)

labels_path = 'data/labels.json'
with open(labels_path, 'w') as f:
    json.dump(labels, f, indent=2)

print(f"Saved: {labels_path}")
print(f"Total entries in labels.json: {len(labels)}")

# ─── SHOW FIRST 3 ENTRIES AS CONFIRMATION ───
print("\nFirst 3 entries in your labels.json:")
print("-" * 40)
for entry in labels[:3]:
    print(f"  image: {entry['image']}")
    print(f"  text:  {entry['text']}")
    print()

print("Last 3 entries:")
print("-" * 40)
for entry in labels[-3:]:
    print(f"  image: {entry['image']}")
    print(f"  text:  {entry['text']}")
    print()

print("=" * 50)
print("ALL DONE! You can now run: python training/train_htr.py")
print("=" * 50)