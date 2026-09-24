import sys
from google.cloud import firestore

# IMPORTANT: Hardcoded Project ID string to ensure compatibility with Agent Platform
PROJECT_ID = "qwiklabs-gcp-01-b334988466c2"

def seed_database():
    print(f"Connecting to Firestore database in project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)

    products = [
        {
            "id": "prod-001",
            "name": "Classic Denim Jacket",
            "category": "Apparel",
            "color": "Blue",
            "price": 89.99,
            "stock": 15,
            "description": "Timeless medium-wash denim jacket with copper buttons.",
            "image_url": "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/denim_jacket.jpg"
        },
        {
            "id": "prod-002",
            "name": "Minimalist Leather Backpack",
            "category": "Accessories",
            "color": "Black",
            "price": 129.50,
            "stock": 8,
            "description": "Sleek full-grain leather backpack with 15-inch laptop compartment.",
            "image_url": "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/backpack.jpg"
        },
        {
            "id": "prod-003",
            "name": "Wireless Noise-Canceling Headphones",
            "category": "Electronics",
            "color": "Silver",
            "price": 199.99,
            "stock": 22,
            "description": "Over-ear Bluetooth headphones with active noise cancellation and 30-hour battery life.",
            "image_url": "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/headphones.jpg"
        },
        {
            "id": "prod-004",
            "name": "Organic Cotton Hoodie",
            "category": "Apparel",
            "color": "Sage Green",
            "price": 65.00,
            "stock": 0,
            "description": "Ultra-soft unisex fleece hoodie made from 100% organic cotton.",
            "image_url": "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/hoodie.jpg"
        },
        {
            "id": "prod-005",
            "name": "Ceramic Pour-Over Coffee Maker",
            "category": "Home",
            "color": "White",
            "price": 34.99,
            "stock": 12,
            "description": "Artisanal ceramic dripper for smooth pour-over brewing.",
            "image_url": "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/coffee_maker.jpg"
        },
        {
            "id": "prod-006",
            "name": "Performance Running Shoes",
            "category": "Footwear",
            "color": "White/Red",
            "price": 119.99,
            "stock": 20,
            "description": "Lightweight breathable mesh running shoes with responsive cushioned soles for athletic training.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/shoes.jpg"
        },
        {
            "id": "prod-007",
            "name": "Classic Leather Casual Sneakers",
            "category": "Footwear",
            "color": "White",
            "price": 95.00,
            "stock": 14,
            "description": "Low-top classic white leather casual sneakers and athletic shoes for everyday style.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/sneakers.jpg"
        },
        {
            "id": "prod-008",
            "name": "Graphic Cotton T-Shirt",
            "category": "Apparel",
            "color": "Charcoal Gray",
            "price": 29.99,
            "stock": 30,
            "description": "Premium 100% combed cotton crewneck graphic t-shirt tee shirt with modern print.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/tshirt.jpg"
        },
        {
            "id": "prod-009",
            "name": "Essential Everyday Crewneck T-Shirt",
            "category": "Apparel",
            "color": "Navy Blue",
            "price": 24.50,
            "stock": 25,
            "description": "Soft breathable cotton short-sleeve t-shirt tee for effortless everyday layering.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/navy_tshirt.jpg"
        },
        {
            "id": "prod-010",
            "name": "Polarized Aviator Sunglasses",
            "category": "Accessories",
            "color": "Gold/Brown",
            "price": 75.00,
            "stock": 10,
            "description": "Classic metal frame aviator sunglasses with glare-reducing polarized UV400 lenses.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/sunglasses.jpg"
        },
        {
            "id": "prod-011",
            "name": "Slim-Fit Stretch Denim Jeans",
            "category": "Apparel",
            "color": "Dark Wash Blue",
            "price": 79.99,
            "stock": 18,
            "description": "Comfortable slim-fit stretch denim jeans with classic 5-pocket styling.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/jeans.jpg"
        },
        {
            "id": "prod-012",
            "name": "Stainless Steel Chronograph Watch",
            "category": "Accessories",
            "color": "Silver/Black",
            "price": 149.99,
            "stock": 9,
            "description": "Water-resistant analog chronograph wrist watch with durable stainless steel strap.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/watch.jpg"
        },
        {
            "id": "prod-013",
            "name": "Stealth Black Performance Running Shoes",
            "category": "Footwear",
            "color": "Black",
            "price": 125.00,
            "stock": 16,
            "description": "Sleek all-black lightweight athletic running shoes and sneakers with impact-absorbing soles.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/shoes.jpg"
        },
        {
            "id": "prod-014",
            "name": "Classic Black Cotton Crewneck T-Shirt",
            "category": "Apparel",
            "color": "Black",
            "price": 27.99,
            "stock": 25,
            "description": "Ultra-soft premium black combed cotton short-sleeve crewneck t-shirt tee.",
            "image_url": "https://storage.googleapis.com/retail-shopping-assistant-assets-b334988466c2/tshirt.jpg"
        }
    ]

    print("Seeding 'products' collection...")
    for prod in products:
        doc_ref = db.collection("products").document(prod["id"])
        doc_ref.set(prod)
        print(f"  - Seeded product: {prod['name']} ({prod['id']})")

    print("\nFirestore seeding complete! ✅")

if __name__ == "__main__":
    seed_database()
