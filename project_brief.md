# My agent: Retail Shopping Assistant

One-liner: A conversational agent that helps online store shoppers discover, compare, and select products with rich visual cards and add items to their shopping cart.

Tool coverage:
- Memory: User shopping preferences (favorite colors, sizes, preferred budget, past cart history across sessions)
- Tools: `search_products(query, category, color, max_price)`, `check_product_availability(product_id)`, `add_to_cart(product_id, quantity, selected_options)`, `get_weather(location)`, `get_current_time(location)`
- Catalog/UI: Product catalog items (renders as product cards with images, prices, color choices, and availability status)
- Image gen: Generating visual outfit pairings or product style mockups based on customer queries
- Sandbox: Cart total calculations, tax estimations, or multi-item package discount calculations

Recommended for every project: memory, storage (Firestore product catalog), tools, image generation, A2UI cards
Agent-specific / stretch: Code sandbox for dynamic cart math, Spring Boot backend proxy + React frontend integration
