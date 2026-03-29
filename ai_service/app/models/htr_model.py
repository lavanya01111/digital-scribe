# ai_service/app/models/htr_model.py
# Loads and runs the TrOCR handwriting recognition model.
# TrOCR = Transformer-based OCR, trained by Microsoft, free on HuggingFace.
# Model: microsoft/trocr-base-handwritten

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image, ImageOps, ImageFilter
import os

# Load model and processor ONCE at startup (avoids re-loading on each request)
MODEL_PATH = "models_saved/trocr_fine_tuned"

if os.path.exists(MODEL_PATH):
    print("Loading FINE-TUNED TrOCR model — please wait...")
    processor = TrOCRProcessor.from_pretrained(MODEL_PATH)
    model = VisionEncoderDecoderModel.from_pretrained(MODEL_PATH)
else:
    print("Loading BASE TrOCR model — please wait...")
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

print("TrOCR model loaded successfully.")

def preprocess_canvas_image(image: Image.Image) -> Image.Image:
    """
    TrOCR is trained on images tightly cropped around the text with a white background.
    If we pass a huge 800x300 canvas mostly filled with white space, it gets squashed
    and the text becomes unreadable. This function crops the ink and adds padding.
    """
    # 1. Ensure image is RGB (convert from RGBA if it has transparency)
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    else:
        image = image.convert('RGB')
        
    # 2. Convert to grayscale to find ink
    gray = image.convert('L')
    
    # 3. Invert so ink is white (255) and background is black (0) for bounding box
    # Using a threshold to handle slight anti-aliasing artifacts
    inverted = gray.point(lambda p: 255 if p < 200 else 0)
    
    # 4. Get bounding box of the non-zero (ink) regions
    bbox = inverted.getbbox()
    
    if bbox:
        # 5. Crop to the bounding box
        cropped = image.crop(bbox)
        
        # 6. Thicken the strokes! (Crucial for TrOCR which expects "Sharpie" thickness, not 3px HTML canvas)
        # MinFilter on a white-background/black-ink image expands the dark pixels.
        thickened = cropped.filter(ImageFilter.MinFilter(3))
        
        # 7. Add generous white padding around the cropped text (e.g. 40px)
        padding = 40
        padded = ImageOps.expand(thickened, border=padding, fill='white')
        return padded
    else:
        # If canvas is completely blank
        return image

def recognize_handwriting(image: Image.Image) -> str:
    """
    Takes a PIL Image of handwritten text.
    Returns the recognized text as a string.
    """
    # Pre-process the canvas input (crop and pad)
    processed_image = preprocess_canvas_image(image)
    
    # DEBUG: Save exactly what the model sees so we know if the preprocessing is working!
    processed_image.save("debug_canvas.png")

    # Preprocess image into tensor format expected by TrOCR
    pixel_values = processor(images=processed_image, return_tensors="pt").pixel_values

    # Run model inference (generate token IDs)
    generated_ids = model.generate(pixel_values, max_new_tokens=64)

    # Decode token IDs back to a readable text string
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return text.strip()
