import openai
import json
import aiohttp
import base64
import os
import time
from typing import Dict, Any, Optional
from fastapi import HTTPException
import uuid

class TokenManager:
    def __init__(self, client_id: str, username: str, password: str):
        self.client_id = client_id
        self.username = username
        self.password = password
        self.token_url = "https://platform-sso.stratpro.hse.ru/realms/platform.stratpro.hse.ru/protocol/openid-connect/token"
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0

    async def get_token(self) -> str:
        current_time = time.time()
        
        # Return existing token if it's still valid
        if self._access_token and current_time < self._token_expiry:
            return self._access_token

        # Get new token
        token_data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
        }

        token_headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=token_data, headers=token_headers) as response:
                    response.raise_for_status()
                    token_response = await response.json()
                    
                    self._access_token = token_response["access_token"]
                    # Set token expiry to 10 minutes from now
                    self._token_expiry = current_time + 600  # 600 seconds = 10 minutes
                    
                    return self._access_token
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to obtain authentication token: {str(e)}"
            )

# Initialize TokenManager with environment variables
token_manager = TokenManager(
    client_id=os.getenv("STRATPRO_CLIENT_ID"),
    username=os.getenv("STRATPRO_LOGIN"),
    password=os.getenv("STRATPRO_PASSWORD")
)

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
    

async def upload_image_to_s3(s3_key: str, image_path: str, access_token: str) -> str:
    """
    Upload image to StratPro S3 storage and return the file key.
    
    Args:
        image_path: Path to the image file
        access_token: Authentication token
        
    Returns:
        str: File key to use in the prediction request
        
    Raises:
        HTTPException: If the upload fails
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        async with aiohttp.ClientSession() as session:
            # Get presigned URL
            async with session.put(
                f"https://platform.stratpro.hse.ru/pu-ocr-qwen-pa-qwen/files/users/{s3_key}",
                headers=headers
            ) as response:
                if response.status == 400:
                    async with session.get(
                        f"https://platform.stratpro.hse.ru/pu-ocr-qwen-pa-qwen/files/users/{s3_key}",
                        headers=headers
                    ) as get_response:
                        response = get_response
                
                if response.status not in [200, 201]:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to get presigned URL: {await response.text()}"
                    )
                    
                files_info = await response.json()
                print(files_info)
            
            # Upload file to S3
            with open(image_path, "rb") as f:
                async with session.put(files_info["presigned_put_url"], data=f) as upload_response:
                    if upload_response.status != 200:
                        raise HTTPException(
                            status_code=upload_response.status,
                            detail=f"Failed to upload file to S3: {await upload_response.text()}"
                        )
                    
        return s3_key
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image to S3: {str(e)}"
        )

async def extract_json_from_image_premise(s3_key: str, image_path: str) -> Dict[str, Any]:
    """
    Extract JSON data from an image using Qwen model via StratPro platform.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing the extracted JSON data
        
    Raises:
        HTTPException: If the API call fails or returns invalid data
    """
    try:
        # Get authentication token
        access_token = await token_manager.get_token()
        # Upload image to S3 and get file key
        file_key = await upload_image_to_s3(s3_key, image_path, access_token)

        # Prepare the prompt
        prompt = """
        Extract data from the receipt image and return it in JSON format with the following structure:
        {
            "receipt_number": "string",
            "store_name": "string",
            "store_address": "string",
            "date_time": "string",
            "currency": "string",
            "total_amount": number,
            "total_discount": number,
            "total_tax": number,
            "items": [
                {
                    "name": "string",
                    "quantity": {
                        "amount": number,
                        "unit_of_measurement": "pcs|kg|lb|g"
                    },
                    "price": number,
                    "discount": number
                }
            ]
        }
        Return only well-formed json data and nothing more.
        """

        # Prepare the request payload
        payload = {
            "inputs": [
                {
                    "name": "prompt",
                    "data": prompt,
                    "datatype": "str",
                    "shape": len(prompt)
                },
                {
                    "name": "image",
                    "data": file_key.replace('pu-ocr-qwen-pa-qwen/files/users/', ''),
                    "datatype": "FILE",
                    "content_type": f"image/{file_key.split('.')[-1]}",
                    "shape": 1
                }
            ],
            "output_fields": [
                {
                    "name": "echo",
                    "datatype": "str"
                }
            ]
        }

        print(payload)

        # Send the request with authentication
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        print('Going to send request to stratpro')
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://platform.stratpro.hse.ru/pu-ocr-qwen-pa-qwen/qwen/predict",
                json=payload,
                headers=headers,
                timeout=300
            ) as response:
                if response.status == 200:
                    # Extract the response content
                    response_data = await response.json()
                    json_str = response_data["outputs"][0]["data"]
                    
                    # Clean up the response string (remove markdown code block markers)
                    json_str = json_str.replace("```json", "").replace("```", "").strip()
                    print(json_str)
                    # Parse the JSON response
                    return json.loads(json_str)
                else:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to extract JSON from image: {await response.text()}"
                    )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        ) 
