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

##############################################################################
# Read categories & products from JSON files
##############################################################################
with open("categories.json", "r") as f:
    categories = json.load(f)

with open("products.json", "r") as f:
    products = json.load(f)

##############################################################################
# Helper Functions
##############################################################################

def cosine_similarity(vec1, vec2):
    """Compute the cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def get_embedding(text: str) -> np.ndarray:
    """
    Create an embedding using the new top-level endpoint openai.embeddings.create
    (for openai>=1.0).
    """
    start_time = time.time()
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    embedding = np.array(response.data[0].embedding)
    end_time = time.time()
    logger.info(f"get_embedding('{text[:20]}...') took {end_time - start_time:.2f}s")
    return embedding

def is_similar(text1: str, text2: str, threshold: float = 0.8) -> bool:
    """
    Determine if two texts are similar based on their embeddings.
    """
    start_time = time.time()
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)
    similarity = cosine_similarity(embedding1, embedding2)
    end_time = time.time()
    logger.info(
        f"is_similar('{text1[:20]}...', '{text2[:20]}...'): "
        f"similarity={similarity:.2f}, took {end_time - start_time:.2f}s"
    )
    return similarity > threshold

##############################################################################
# Core logic: For each category, find the products that match it
##############################################################################

def find_products_for_categories(products, categories):
    """
    Returns a dict where each key is a category,
    and each value is a list of products that match (are similar to) that category.
    """
    start_time = time.time()
    results_by_category = {}

    for cat in categories:
        matching_products = []
        for product in products:
            if is_similar(product["name"], cat):
                matching_products.append(product)

        results_by_category[cat] = matching_products

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
