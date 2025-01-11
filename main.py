import os
import openai
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define products to track
products = [
    {"store": "Amazon", "name": "Protein Eggs", "price": 4.99},
    {"store": "Amazon", "name": "Egg", "price": 4.99},
    {"store": "Big Basket", "name": "Chicken Eggs", "price": 5.20},
    {"store": "Flipkart", "name": "Rich Eggs", "price": 5.00},
    {"store": "Amazon", "name": "Organic Dal", "price": 2.99},
    {"store": "Big Basket", "name": "Yellow Dal", "price": 3.20},
    {
        "store": "Big Basket",
        "name": "Tata Sampann Toor Dal/Togari Bele 500g Pouch",
        "price": 105
    },
    {
        "store": "Big Basket",
        "name": "bb Popular Toor/Arhar Dal 5kg Pouch",
        "price": 1085
    },
    {
        "store": "Big Basket",
        "name": "bb Royal Peanuts/Kadlekai - Raw 1kg Pouch",
        "price": 209  
    },
    {
        "store": "Big Basket",
        "name": "bb Royal Organic Toor Dal/Togari Bele 5kg Pouch",
        "price": 938
    },
    {
        "store": "Big Basket",
        "name": "bb Royal Organic Raw Peanuts 2×1kg Multipack",
        "price": 414
    },
    {
        "store": "Big Basket",
        "name": "bb Royal Toor Dal/Togari Bele - Desi 1kg Pouch",
        "price": 194.5
    },
    {
        "store": "Big Basket",
        "name": "Tata Sampann Urad Dal/Ulundhu Bele Whole White 1kg",
        "price": 192.5
    },
    {
        "store": "Big Basket",
        "name": "bb Popular Moong Dal/Hesaru Bele 500g Pouch",
        "price": 99   
    },
    {
        "store": "Big Basket",
        "name": "Tata Sampann Moong Dal/Hesaru Bele 500g Pouch",
        "price": 172  
    },
    {
        "store": "Big Basket",
        "name": "freshol Farm Eggs - Regular, 30 pcs",
        "price": 229
    },
    {
        "store": "Big Basket",
        "name": "Eggoz Farm Fresh White Eggs, 30 pcs",
        "price": 419
    },
    {
        "store": "Big Basket",
        "name": "Farm Made Free Range Eggs, 24 pcs",
        "price": 529
    },
    {
        "store": "Big Basket",
        "name": "Abhi Eggs Nutri+ With Immunity Boosters, 24 pcs",
        "price": 508.75
    },
    {
        "store": "Big Basket",
        "name": "SKM Best Plus Eggs, 12 pcs",
        "price": 156
    },
    {
        "store": "Big Basket",
        "name": "freshol Farm Eggs - Medium, Brown, 10 pcs",
        "price": 135
    },
    {
        "store": "Big Basket",
        "name": "Best Buy Eggs - Wholesome, Rich in Protein, Vitamins & Amino Acids, 30 pcs",
        "price": 530
    },
    {
        "store": "Big Basket",
        "name": "UFP Healthy Brown Eggs - Large, Rich in Protein, Great For Bones, 30 pcs",
        "price": 430
    },
    {
        "store": "Big Basket",
        "name": "Country Cage Free Eggs - Medium, 6 pcs",
        "price": 110
    }
]

def cosine_similarity(vec1, vec2):
    """Compute the cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def is_similar(product1, product2):
    embedding1_response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=product1
    )
    embedding1 = embedding1_response.data[0].embedding

    embedding2_response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=product2
    )
    embedding2 = embedding2_response.data[0].embedding

    similarity = cosine_similarity(embedding1, embedding2)
    return similarity > 0.8


def track_prices(products):
    """
    Group prices for similar products based on is_similar().
    Returns a dictionary where each key is a product name,
    and the value is a list of product entries considered similar.
    """
    grouped_prices = {}

    for i, product1 in enumerate(products):
        for j, product2 in enumerate(products):
            # Avoid comparing the same pair twice or comparing a product with itself
            if i >= j:
                continue

            if is_similar(product1["name"], product2["name"]):
                group_key = product1["name"]

                # Initialize a list in the dictionary for this product name
                if group_key not in grouped_prices:
                    grouped_prices[group_key] = []

                # Add both products to that group
                grouped_prices[group_key].append(product1)
                grouped_prices[group_key].append(product2)

    return grouped_prices

def display_grouped_prices(grouped_prices):
    """Pretty-print the grouped prices for each product group."""
    for product_name, group in grouped_prices.items():
        print(f"Similar products to '{product_name}':")
        # Use a set to avoid printing duplicates
        unique_group = {
            f"{item['store']}: {item['name']}- ${item['price']}"
            for item in group
        }
        for product_info in unique_group:
            print(f"  - {product_info}")
        print()

if __name__ == "__main__":
    # Group and then display the similar products
    grouped_prices = track_prices(products)
    display_grouped_prices(grouped_prices)
