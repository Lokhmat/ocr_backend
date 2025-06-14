import os
import random
import json
import base64
import requests
import string
from io import BytesIO
from PIL import Image

# Directories for images and ground truth data
IMG_DIR = "./SROIE2019/train/img"
GT_DIR = "./SROIE2019/train/entities"

# Number of random samples
NUM_SAMPLES = 200

# Placeholder for your API key
API_KEY = os.getenv("API_KEY")

# Maximum width/height for thumbnail to reduce size
MAX_DIMENSION = 1024  # pixels

# JPEG quality for recompression
JPEG_QUALITY = 30     # lower means more compression, smaller Base64


def shrink_and_encode_image(image_path):
    """
    1) Open image with PIL, 
    2) Resize it to max dimension MAX_DIMENSION (preserve aspect ratio),
    3) Recompress as JPEG with quality=JPEG_QUALITY,
    4) Return the Base64-encoded string of the recompressed bytes.
    """
    # Open original image
    img = Image.open(image_path)
    
    # Compute new size preserving aspect ratio
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        if w >= h:
            new_w = MAX_DIMENSION
            new_h = int((MAX_DIMENSION / w) * h)
        else:
            new_h = MAX_DIMENSION
            new_w = int((MAX_DIMENSION / h) * w)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    
    # Recompress to JPEG in memory
    buffer = BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=JPEG_QUALITY)
    buffer.seek(0)
    
    # Encode bytes to Base64
    img_bytes = buffer.read()
    return base64.b64encode(img_bytes).decode("utf-8")


import base64
import json
import requests

def get_prediction(image_path):
    """
    Sends a shrunk Base64-encoded image to a Hugging Face Inference Endpoint
    and returns the extracted JSON receipt data. Assumes the model is trained
    or configured to understand receipt structures and return JSON.

    Returns:
        dict: Extracted JSON data or an empty dict if parsing fails.
    """
    # Inference endpoint URL
    url = "https://faf0a1qu6obk1e3d.us-east-1.aws.endpoints.huggingface.cloud/v1/chat/completions" 

    # Authorization header
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Shrink and encode the image
    img_b64 = shrink_and_encode_image(image_path)

    # Prompt instructing the model to extract fields and return strict JSON
    prompt = (
        "Extract the following fields from the receipt:\n"
        "company, date (in DD/MM/YYYY), address, total amount.\n"
        "Return the result strictly in JSON format without any extra text.\n"
        "{\"company\": \"{COMPANY NAME}\", "
        "\"date\": \"{DATE OF RECEIPT IN FORMAT DD/MM/YYYY}\", "
        "\"address\": \"{ADDRESS OF COMPANY}\", "
        "\"total\": \"{TOTAL_AMOUNT_OF_RECEIPT}\"}"
    )

    # Prepare the request body
    body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"
                        }
                    }
                ]
            }
        ],
        "model": "tgi",
        "max_tokens": 1024,
    }

    # Send POST request
    response = requests.post(url, headers=headers, json=body)

    # Handle response
    if response.status_code == 200:
        data = response.json()
        try:
            # Extract model's response content
            content = data["choices"][0]["message"]["content"]
            # Remove any markdown formatting
            content = content.strip().strip("```json").strip("```")
            # Parse and return JSON
            return json.loads(content)
        except (KeyError, json.JSONDecodeError) as e:
            # Log error and return empty dict if parsing fails
            print(f"Error parsing response: {e}")
            return {}
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return {}


def load_ground_truth(txt_path):
    """
    Loads ground truth JSON from .txt file.
    Assumes .txt file contains a JSON string.
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}


def evaluate_predictions_symbolwise(samples):
    """
    Evaluates model predictions against ground truth on a character-by-character basis.
    Calculates symbol-wise precision, recall, and F1 score.
    """
    total_tp = 0  # True Positives (matching characters)
    total_fp = 0  # False Positives (extra characters in prediction)
    total_fn = 0  # False Negatives (missing characters in prediction)

    for img_file, gt_file in samples:
        full_img_path = os.path.join(IMG_DIR, img_file)
        pred = get_prediction(full_img_path)
        print(f"Predicted first: {pred}")
        
        gt = load_ground_truth(os.path.join(GT_DIR, gt_file))

        # Process each field in ground truth
        for field in gt:
            # Skip non-string fields
            if not (isinstance(gt[field], str) and gt[field].strip()):
                continue

            # Clean strings: remove whitespace, lowercase
            gt_clean = gt[field].translate({ord(c): None for c in string.whitespace}).lower()
            
            # Handle missing fields in prediction
            if field not in pred or not isinstance(pred[field], str):
                total_fn += len(gt_clean)  # All GT characters are missed
                continue

            pred_clean = pred[field].translate({ord(c): None for c in string.whitespace}).lower()

            # Compare up to the length of the shorter string
            min_len = min(len(gt_clean), len(pred_clean))
            tp = sum(gt_clean[i] == pred_clean[i] for i in range(min_len))

            # Count extra/missing characters
            fp = max(0, len(pred_clean) - len(gt_clean))  # Extra in prediction
            fn = max(0, len(gt_clean) - len(pred_clean))  # Missing in prediction

            # Add to totals
            total_tp += tp
            total_fp += fp
            total_fn += fn

    # Avoid division by zero
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return precision, recall, f1


def main():
    # List all image files and corresponding ground truth .txt files
    try:
        all_images = [f for f in os.listdir(IMG_DIR) if f.lower().endswith(".jpg")]
    except FileNotFoundError:
        print(f"Directory not found: {IMG_DIR}")
        return

    samples = []
    for img_file in all_images:
        base_name = os.path.splitext(img_file)[0]
        gt_file = base_name + ".txt"
        if os.path.exists(os.path.join(GT_DIR, gt_file)):
            samples.append((img_file, gt_file))

    # Ensure we have enough samples
    if len(samples) < NUM_SAMPLES:
        print("Not enough images with ground truth for sampling.")
        return

    # Randomly select 100 samples
    selected = random.sample(samples, NUM_SAMPLES)

    # Evaluate
    precision, recall, f1_score = evaluate_predictions_symbolwise(selected)

    # Print results
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1_score:.4f}")


if __name__ == "__main__":
    main()
    