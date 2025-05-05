import openai
import json
import requests
import base64
import os
from typing import Dict, Any
from fastapi import HTTPException

# Configure OpenAI client for OpenRouter
client = openai.OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def encode_image(image_path: str) -> str:
    """Encode image file to base64 string."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encode image: {str(e)}")

def extract_json_from_image_cloud(image_path: str) -> Dict[str, Any]:
    """
    Extract JSON data from an image using Qwen model.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing the extracted JSON data
        
    Raises:
        HTTPException: If the API call fails or returns invalid data
    """
    try:
        # Encode image
        encoded_image = encode_image(image_path)
        print("Encoded image")
        
        # Create prompt for JSON extraction
        prompt_text = """
        #Your Task: Receipt Recognition and Data Extraction

        You are tasked with extracting structured information from receipts. Receipts will come from various countries, in different languages, and can have different layouts and formats. Your goal is to parse the receipt text and return the data in JSON format with the required fields. Follow the specific instructions below to ensure accurate extraction.

        #Required Fields:

        1. Receipt Number: Extract the unique receipt number, typically found at the top of the receipt.
        2. Store/Business Name: Extract the name of the store, cafe, restaurant, or service provider.
        3. Store Address: Extract the address of the store, including city and country if available.
        4. Date: Extract the date of the transaction and format it as YYYY-MM-DD HH:MM.
        5. Currency: Extract the currency if explicitly mentioned (e.g., EUR, USD). If the currency is not specified, leave it as null.
        6. Total Amount: Extract the total amount of the transaction. This is typically located at the end of the receipt, often highlighted in bold or a larger font.
        7. Total Discount: Extract the total discount if explicitly mentioned. If not, calculate the total discount by summing up the discounts for individual items.
        8. Tax: Extract the total tax amount if it is listed on the receipt.

        #Item-Level Details:

        For each item on the receipt, extract the following details:

        1. Item Name: Extract the full name of each item. Some items may have names split across multiple lines; in this case, concatenate the lines until you encounter a quantity or unit of measurement (e.g., "2kg"), which marks the end of the item name or indicates that the item details have begun.
        2. Quantity: Extract the quantity of each item, taking into account both the numerical amount and the unit of measurement.
        3. Price: Extract the final price for each item or position on the receipt.
        4. Discount: Optionally extract any discount associated with the item, if available.

        #Handling Quantity and Units:

        When extracting quantity details, consider the following cases to correctly interpret items sold by weight versus items sold by piece:

        1. **Items Sold by Weight:**
        - **Explicit Weight Information:** If the receipt shows a numerical value with a weight unit (such as "kg", "g", or "lb"), extract that number as the weight amount and the corresponding unit as the unit of measurement.
            - *Example:* For a line "Sugar 0.5 kg", extract `"quantity": { "amount": 0.5, "unit_of_measurement": "kg" }`.
        - **Weight Unit Variations:** Recognize variations in units (e.g., "kgs", "kilograms", "grams", "lbs", "pounds"). Normalize these into one of the supported units: `kg`, `g`, or `lb`.
        - **Multi-line Formats:** If weight information is split over multiple lines or appears alongside price details (for example, "Bananas" on one line and "1.2 kg" on the next), merge the lines to correctly assign the weight amount and unit.

        2. **Items Sold by Piece:**
        - **Explicit Piece Information:** If the receipt indicates the number of pieces (often shown as "pcs" or implied by a multiplication format such as "5 * 23.00 = 115.0"), assign the unit of measurement as `"pcs"`.
            - *Example:* For a line "Eggs 12 pcs", extract `"quantity": { "amount": 12, "unit_of_measurement": "pcs" }`.
        - **Multiplication Format Cases:** When a line such as "5 * 23.00 = 115.0" appears, interpret it as 5 pieces, and look for the corresponding item name in an adjacent line. Ensure that `"quantity": { "amount": 5, "unit_of_measurement": "pcs" }` is captured.
        - **Inconsistent or Missing Quantity Information:** If the receipt implies that an item is sold by pieces (for example, through context or typical product type) but does not clearly provide a quantity, default to 1. This means if the quantity is ambiguous or absent, assume that the client bought 1 unit.

        3. **Ambiguous or Inconsistent Cases:**
        - **Missing or Unclear Units:** If a receipt does not clearly specify the unit of measurement but the context implies weight (for example, by showing decimal numbers or using terms like “kg” in nearby text), extract the weight if it is clear; otherwise, mark the unit as `"not available"` and the amount as `"unknown"`.
        - **Context-Dependent Interpretation:** In cases where the same receipt might list both weighted items and items sold by piece, use contextual clues (such as typical product types or formatting cues) to determine whether the number represents a weight or a count. If ambiguous, prioritize explicitly stated units; if none are provided and the context suggests pieces, default the quantity to 1.

        #Special Cases:

        1. Multi-line Item Names: If an item name spans multiple lines, merge the lines to form the complete name. Stop merging when a quantity or unit of measurement is encountered.
        2. Total Amount: The total amount is often larger than other numbers or displayed in bold at the bottom of the receipt. Make sure to capture this accurately.
        3. Total Discount: If no total discount is listed, sum the discounts for each individual item.
        4. Total Tax: Find the total tax amount that is paid or should be paid. It is usually found at the bottom of the receipt.
        5. Quantity Details: The quantity of an item might appear before, after, or on the same line as the item name. Use spatial and contextual cues to merge the relevant information. For example:
        - If one line shows "5 * 23.00 = 115.0" and the next line shows "Milk," interpret this as 5 pieces of Milk at a total price of 115.0.
        - Conversely, if the item name appears first (e.g., "Milk") and a following line shows "5 * 23.00 = 115.0," treat it the same way.

        #JSON Output Format:

        {
        "receipt_number": "string",
        "store_name": "string",
        "store_address": "string",
        "date_time": "string",
        "currency": "optional[string]",
        "total_amount": "number",
        "total_discount": "number",
        "total_tax": "number",
        "items": [
            {
            "name": "string",
            "quantity": {
                "amount": "number",
                "unit_of_measurement": "enumeration[pcs, kg, lb, g]"
            },
            "price": "number",
            "discount": "optional[number]"
            }
        ]
        }

        #Additional Notes:

        1. Handle receipts in various languages and from different countries.
        2. Pay special attention to formatting differences and edge cases, such as multi-line item names, missing currency symbols, and variations in quantity placement.
        3. **Handling Units:**
        - For items sold by weight, extract the numerical weight and normalize the unit to one of the supported values (`kg`, `g`, or `lb`).
        - For items sold by piece, ensure that the unit is set to `"pcs"` and that the number accurately reflects the quantity purchased.
        - When faced with ambiguous formatting or missing quantity information for items that appear to be sold by pieces, default the quantity to 1.
        4. Always ensure the output is well-structured and follows the JSON format provided.
        5. Return the full JSON object with all available information. If any information is unclear or missing, include it as `"unknown"` or `"not available"` in the output.
        6. Do not add any additional text outside the JSON output.
        """
        
        # Make API call to Qwen model
        response = client.chat.completions.create(
            model="qwen/qwen2.5-vl-72b-instruct:free",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]}
            ],
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content.replace("```", "").replace("json", "")
        print(content)
        
        # Try to parse the response as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse model response as JSON"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        ) 
    

def extract_json_from_image_premise(image_path: str) -> Dict[str, Any]:
    """
    Extract JSON data from an image using Qwen model.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing the extracted JSON data
        
    Raises:
        HTTPException: If the API call fails or returns invalid data
    """
    try:
        # Encode image
        encoded_image = encode_image(image_path)
        print("Encoded image")

        # Prepare the request
        files = {"file": encoded_image}
        params = {"prompt": "Extract data from the image in JSON format. Return well formed JSON and only it."}

        # Send the request
        response = requests.post("http://qwen:80/generate", files=files, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the response content
            response_content = response.json()["response"]
            print(response_content)
            return json.loads(response_content)
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to extract JSON from image: {response.text}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        ) 
