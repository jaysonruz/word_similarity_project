import os
import time
import json
import logging
import openai
import numpy as np
from dotenv import load_dotenv

##############################################################################
# Configure Logging
##############################################################################
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

##############################################################################
# Load environment variables from .env
##############################################################################
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# create openAI client
client = openai.OpenAI()

##############################################################################
# Read categories & products from JSON files
##############################################################################
with open("categories.json", "r") as f:
    categories = json.load(f)

with open("products.json", "r") as f:
    products = json.load(f)
##############################################################################
# Chat-Based Classification Function
##############################################################################

def classify_product(product_name: str, categories: list[str]) -> str:
    """
    Uses ChatCompletion to classify which ONE of the given categories
    best fits the product_name. If none is appropriate, the model should say 'none'.
    
    Returns the category name as a string, or 'none'.
    """

    # You can tune this prompt as needed:
    system_prompt = (
        """You are a helpful assistant that classifies food product names into one of the category or closest category. (food products can be indian origin) """
        "If the product does not fit any of the categories, respond with 'none'."
    )
    user_prompt = f"""
    Categories: {', '.join(categories)}
    
    Product name: "{product_name}"
    
    Which ONE of these categories best describes this product? 
    If none fit, say 'none'.
    """

    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-4o",  # or another model if desired
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,  # keep it deterministic
    )
    end_time = time.time()

    logger.info(
        f"classify_product('{product_name[:20]}...') took {end_time - start_time:.2f}s"
    )

    classification = response.choices[0].message.content.strip().lower()

    return classification

##############################################################################
# Core logic: For each product, ask the model which category it belongs to
##############################################################################

def find_products_for_categories(products, categories):
    """
    Returns a dict: { category_name: [products that were classified under it] }.
    If the model answers 'none', we exclude that product from all categories.
    """
    start_time = time.time()

    # Initialize a dictionary to hold products per category
    results_by_category = {cat: [] for cat in categories}

    for product in products:
        predicted_category = classify_product(product["name"], categories)

        # Only store the product in results if it's a recognized category
        if predicted_category in results_by_category:
            results_by_category[predicted_category].append(product)
        else:
            logger.info(
                f"Product '{product['name']}' classified as 'none' or unknown category."
            )

    end_time = time.time()
    logger.info(
        f"find_products_for_categories completed in {end_time - start_time:.2f}s"
    )
    return results_by_category

def display_results_by_category(results_by_category):
    """
    Print each category and its matching products.
    """
    for category, products_list in results_by_category.items():
        print(f"Similar products to '{category}':")
        if not products_list:
            print("  - No matching products found.")
        else:
            for p in products_list:
                print(f"  - {p['store']}: {p['name']} - ${p['price']}")
        print()

##############################################################################
# Script Entry Point
##############################################################################

if __name__ == "__main__":
    overall_start = time.time()
    
    results_by_category = find_products_for_categories(products, categories)
    display_results_by_category(results_by_category)
    
    overall_end = time.time()
    logger.info(f"Total script execution time: {overall_end - overall_start:.2f}s")