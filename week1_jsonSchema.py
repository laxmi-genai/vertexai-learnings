# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    https://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# --- Import necessary libraries ---

# Import the main Google GenAI SDK
from google import genai

# Import specific classes from the genai.types module for configuration
from google.genai.types import (    
    GenerateContentConfig,
    HarmBlockThreshold,
    HarmCategory,
    MediaResolution,
    SafetySetting,   
    Part
)
import os

# Import the 'load_dotenv' function to load environment variables from a .env file
from dotenv import load_dotenv

# --- Load Environment Variables and Configure Client ---

# Execute the function to load variables from a '.env' file in your project's root directory
load_dotenv()



# --- Model and Project Configuration ---

# Define the ID of the specific Gemini model you want to use
MODEL_ID="gemini-2.5-flash"

# Retrieve the Google Cloud Project ID from the loaded environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
# Retrieve the Google Cloud Location (e.g., "us-central1") from the environment variables
LOCATION = os.getenv("LOCATION")



# --- Initialize the Client ---

# 'vertexai=True' specifies that the client should connect to the Vertex AI backend,
# using the provided project and location for authentication and billing.
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# An advanced JSON Schema for identifying products based on category
product_identification_schema = {
    "type": "object",
    "description": "Schema for identifying key features of a product from an image based on its category.",
    # 1. Define all possible properties that could be identified.
    "properties": {
        "product_name": {
            "type": "string",
            "description": "The overall name for the product or set (e.g., 'Cotton T-Shirt', 'Knife Set').",
        },
        "category": {
            "type": "string",
            "description": "The general category of the product.",
            "enum": ["Clothing", "Kitchenware"],
        },
        "brand": {
            "type": "string",
            "description": "The brand name of the clothing item.",
        },
        "color": {
            "type": "string",
            "description": "The dominant color of the clothing item.",
        },
        "material": {
            "type": "string",
            "description": "The primary material of the clothing (e.g., 'Cotton', 'Polyester', 'Wool').",
        },
        "number_of_items": {
            "type": "integer",
            "description": "The total count of items in the kitchenware set.",
        },
        "items": {
            "type": "array",
            "description": "A list of the individual kitchenware items.",
            "items": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "The name of the individual item (e.g., 'Chef's Knife', 'Paring Knife')."
                    },
                    "item_color": {
                        "type": "string",
                        "description": "The color of that specific item."
                    }
                },
                "required": ["item_name", "item_color"]
            }
        }
    },
    # 2. List only the properties that are ALWAYS required for any product.
    "required": ["product_name", "category"],
    # 3. Use 'allOf' to apply conditional requirements based on the category.
    "allOf": [
        {
            # If the product is Clothing...
            "if": {"properties": {"category": {"const": "Clothing"}}},
            # ...then 'brand', 'color', and 'material' are required.
            "then": {"required": ["brand", "color", "material"]},
        },
        {
            # If the product is Kitchenware...
            "if": {"properties": {"category": {"const": "Kitchenware"}}},
            # ...then 'number_of_items' and the 'items' list are required.
            "then": {"required": ["number_of_items", "items"]},
        },
    ],
}


# --- Process Multiple Images Using a Loop ---

# 1. Create a list of all the image file paths you want to analyze.
image_files_to_process = [
    "week1_images/image_1.jpeg",
    "week1_images/image_2.jpeg",
    # You can easily add more file paths here
]

# 2. Loop through each file path in the list.
for image_path in image_files_to_process:
    # Print a header to clearly separate the output for each image.
    print(f"---  Image being processed: {image_path} ---")

    try:
        # Open the current image file in "read binary" ("rb") mode.
        with open(image_path, "rb") as f:
            # Read the file's content into a bytes object.
            image = f.read()

        # Send the request to the Gemini API with the current image's data.
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                Part.from_bytes(data=image, mime_type="image/jpeg"),
                "Fetch key features of the image",
            ],
            config=GenerateContentConfig(
                safety_settings=[
                            SafetySetting(
                                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                            ),
                            SafetySetting(
                                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                            ),
                            SafetySetting(
                                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                            ),
                            SafetySetting(
                                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                            )],
                response_mime_type="application/json",
                response_json_schema=product_identification_schema,
                media_resolution=MediaResolution.MEDIA_RESOLUTION_HIGH,
            )
        )

        # Print the analysis result for the current image.
        # Adding a check to see if the response has text before printing.
        if response.text:
            print(response.text)
        else:
            print("❌ No response was returned.")

    except FileNotFoundError:
        # Handle cases where an image file listed does not exist.
        print(f"❌ Error: File not found at '{image_path}'. Skipping.")
    except Exception as e:
        # Catch any other potential errors during the API call.
        print(f"❌ An unexpected error occurred: {e}")

    # Print a blank line for better readability between outputs.
    print("\n")
