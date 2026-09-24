# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
import json
import os
import urllib.parse
import urllib.request
import uuid
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from google.cloud import firestore, storage
from google import genai

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback

load_dotenv()

# IMPORTANT: Hardcoded Project ID, Bucket Name, and Memory Bank ID strings for compatibility
PROJECT_ID = "qwiklabs-gcp-01-b334988466c2"
BUCKET_NAME = "retail-shopping-assistant-assets-b334988466c2"
MEMORY_BANK_ID = "1731005136072867840"


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a helpful Retail Shopping Assistant for an online store. "
        "Pay special attention to customer preferences, dietary needs, health requirements, and ALLERGIES "
        "(such as food allergies, or fabric/material sensitivities like wool, latex, nickel, or leather). "
        "Always remember customer allergies across sessions using long-term Memory Bank. "
        "When discovering products, discussing options, or adding items to the cart, check the customer's remembered "
        "allergies and proactively warn or filter out items containing conflicting materials or ingredients. "
        "Help customers discover and search products, check stock availability, "
        "discuss product options (like colors and categories), add items to their shopping cart, "
        "calculate itemized cart totals with taxes and promo discounts, "
        "convert product prices into foreign currencies with live exchange rates, "
        "generate product style and outfit mockup images, "
        "run Python code calculations safely in an isolated sandbox, "
        "and lookup store coordinates or nearby shopping locations using Geocoding and Places APIs. "
        "You can also answer general questions about time or weather when relevant."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback triggered after each turn to send the session to Memory Bank for extraction."""
    try:
        if getattr(callback_context, "_memory_service", None) is None:
            callback_context._memory_service = get_memory_bank_service()
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None


def get_memory_bank_service() -> VertexAiMemoryBankService:
    """Returns a VertexAiMemoryBankService instance pointed at the deployed Memory Bank."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location="us-east4",
        agent_engine_id=MEMORY_BANK_ID,
    )


def get_code_executor() -> AgentEngineSandboxCodeExecutor:

    """Initialize AgentEngineSandboxCodeExecutor by reading agent_engine_resource_name or sandbox_resource_name from deployment_metadata.json if present."""
    metadata_path = os.path.join(os.path.dirname(__file__), "..", "deployment_metadata.json")
    agent_engine_resource_name = None
    sandbox_resource_name = None

    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                data = json.load(f)
                agent_engine_resource_name = data.get("agent_engine_resource_name") or data.get("resource_name")
                sandbox_resource_name = data.get("sandbox_resource_name")
        except Exception:
            pass

    if sandbox_resource_name:
        return AgentEngineSandboxCodeExecutor(sandbox_resource_name=sandbox_resource_name)
    elif agent_engine_resource_name:
        return AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_resource_name)
    else:
        return AgentEngineSandboxCodeExecutor()


def get_firestore_client():

    return firestore.Client(project=PROJECT_ID)


async def generate_product_image(prompt: str, tool_context: ToolContext) -> str:
    """Generate a visual mockup or outfit pairing image for a product using gemini-3.1-flash-lite-image in the global region.

    Args:
        prompt: Description of the product visual, outfit pairing, or style mockup to generate (e.g. 'A classic denim jacket styled with white sneakers').

    Returns:
        Public Cloud Storage HTTPS URL of the generated image.
    """
    try:
        genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return "Failed to generate product image: No image data returned from model."

        ext = "png" if "png" in mime_type else "jpg"
        object_name = f"generated_product_{uuid.uuid4().hex[:8]}.{ext}"

        # (1) Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=object_name, artifact=artifact_part)

        # (2) Upload directly to public Cloud Storage bucket without local file writes
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
        return f"Successfully generated product image! Public URL: {public_url}"

    except Exception as e:
        return f"Failed to generate product image: {e}"


async def generate_product_video(prompt: str, tool_context: ToolContext) -> str:
    """Generate a short product demonstration or promotional showcase video for an item using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Args:
        prompt: Description of the product video to generate (e.g. 'A 3D product showcase video of Stealth Black Performance Running Shoes spinning on a pedestal').

    Returns:
        Public Cloud Storage HTTPS URL of the generated video.
    """
    try:
        genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        interaction = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        if hasattr(interaction, "output_video") and interaction.output_video:
            raw_data = getattr(interaction.output_video, "data", None) or getattr(interaction.output_video, "bytes", None)
            if isinstance(raw_data, bytes):
                video_bytes = raw_data
            elif isinstance(raw_data, str):
                video_bytes = base64.b64decode(raw_data)

        if not video_bytes:
            return "Failed to generate product video: No video data returned from model."

        object_name = f"generated_video_{uuid.uuid4().hex[:8]}.mp4"

        # (1) Save with tool_context.save_artifact so it shows up in Playground's Artifacts panel
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=object_name, artifact=artifact_part)

        # (2) Upload directly to public Cloud Storage bucket without local file writes
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
        return f"Successfully generated product video! Public URL: {public_url}"

    except Exception as e:
        return f"Failed to generate product video: {e}"


def geocode_address(address: str) -> str:

    """Turn an address or location query into geographic latitude and longitude coordinates using Google Maps Geocoding API.

    Args:
        address: Street address or location query (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA').

    Returns:
        Formatted address, location name, and latitude/longitude coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not configured."

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RetailShoppingAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("status") != "OK" or not data.get("results"):
            return f"Could not geocode address '{address}'. API status: {data.get('status')}."

        first_result = data["results"][0]
        formatted_address = first_result.get("formatted_address", address)
        loc = first_result.get("geometry", {}).get("location", {})
        lat = loc.get("lat")
        lng = loc.get("lng")

        return f"Geocoded '{address}': Name/Address: {formatted_address}, Location: (Latitude: {lat}, Longitude: {lng})."
    except Exception as e:
        return f"Failed to geocode address: {e}"


def find_nearby_places(latitude: float, longitude: float, place_type: str = "store", radius_meters: float = 5000.0) -> str:
    """Find nearby places (stores, shopping malls, pickup locations) around coordinates using Google Places API (New).

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Type of place to search for (e.g. 'store', 'shopping_mall', 'clothing_store').
        radius_meters: Search radius in meters (defaults to 5000.0 meters / 5 km).

    Returns:
        A list of nearby places containing name, formatted address, and location coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not configured."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location"
    }

    body = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius_meters
            }
        }
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        places = data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters} meters."

        results = []
        for p in places:
            display_name = p.get("displayName", {}).get("text", "Unknown Place")
            addr = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            lat = loc.get("latitude")
            lng = loc.get("longitude")
            results.append(f"- Name: {display_name}, Address: {addr}, Location: (Latitude: {lat}, Longitude: {lng})")

        return f"Nearby '{place_type}' places found:\n" + "\n".join(results)
    except Exception as e:
        return f"Failed to search nearby places: {e}"


def convert_currency(amount: float, from_currency: str = "USD", to_currency: str = "EUR") -> str:

    """Convert a product price or cart total to a foreign currency using live real-time exchange rates.

    Args:
        amount: The monetary amount to convert (e.g. 89.99).
        from_currency: 3-letter source currency code (defaults to 'USD').
        to_currency: 3-letter target currency code (e.g. 'EUR', 'GBP', 'CAD', 'JPY').

    Returns:
        Converted amount and live rate information from the public Frankfurter Exchange Rate API.
    """
    from_curr = from_currency.strip().upper()
    to_curr = to_currency.strip().upper()

    if from_curr == to_curr:
        return f"{amount:.2f} {from_curr} is equal to {amount:.2f} {to_curr}."

    # Read optional API key from env var if configured
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "")

    url = f"https://api.frankfurter.dev/v1/latest?amount={amount}&from={from_curr}&to={to_curr}"
    headers = {"User-Agent": "RetailShoppingAssistant/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        rates = data.get("rates", {})
        if to_curr not in rates:
            return f"Unable to convert from {from_curr} to {to_curr}. Please check the currency code."

        converted_amount = rates[to_curr]
        rate_val = converted_amount / amount if amount > 0 else 0
        return f"{amount:.2f} {from_curr} = {converted_amount:.2f} {to_curr} (Live Rate: 1 {from_curr} = {rate_val:.4f} {to_curr} as of {data.get('date')})."
    except Exception as e:
        return f"Failed to fetch live exchange rates: {e}"


SYNONYMS = {
    "shoe": ["shoes", "sneaker", "sneakers", "footwear", "running"],
    "shoes": ["shoe", "sneaker", "sneakers", "footwear", "running"],
    "sneakers": ["shoe", "shoes", "sneaker", "footwear"],
    "tshirt": ["t-shirt", "tee", "shirt", "top", "apparel"],
    "t-shirt": ["tshirt", "tee", "shirt", "top", "apparel"],
    "shirt": ["tshirt", "t-shirt", "tee", "top", "apparel"],
    "tee": ["tshirt", "t-shirt", "shirt", "top"],
    "glasses": ["sunglasses", "aviator", "eyewear"],
    "sunglasses": ["glasses", "aviator", "eyewear"],
    "watch": ["watches", "chronograph"],
    "jeans": ["pants", "denim"],
    "jacket": ["coat", "outerwear", "denim"],
}


def search_products(query: str = "", category: str = "", max_price: float = 0.0) -> str:
    """Search and discover products in the store catalog.

    Args:
        query: Keywords to search in product names or descriptions (e.g. 'shoes', 'tshirt', 'backpack', 'headphones').
        category: Filter by product category (e.g. 'Apparel', 'Footwear', 'Electronics', 'Accessories', 'Home').
        max_price: Optional maximum price limit for filtering.

    Returns:
        A list of matching products with name, price, stock, color, and description.
    """
    db = get_firestore_client()
    docs = list(db.collection("products").stream())
    
    results = []
    q_clean = query.strip().lower()
    raw_tokens = q_clean.split() if q_clean else []
    
    expanded_token_groups = []
    for token in raw_tokens:
        group = [token]
        if token in SYNONYMS:
            group.extend(SYNONYMS[token])
        expanded_token_groups.append(group)

    for doc in docs:
        prod = doc.to_dict()
        
        if category and category.lower() not in prod.get("category", "").lower():
            continue
            
        if max_price > 0 and prod.get("price", 0) > max_price:
            continue
            
        if raw_tokens:
            full_text = f"{prod.get('name', '')} {prod.get('description', '')} {prod.get('color', '')} {prod.get('category', '')}".lower()
            all_tokens_matched = True
            for group in expanded_token_groups:
                if not any(term in full_text for term in group):
                    all_tokens_matched = False
                    break
            if not all_tokens_matched:
                continue
                
        results.append(prod)

    if not results:
        all_prods = [d.to_dict() for d in docs]
        return f"No products matching '{query}' were found. Available catalog items: {all_prods}"
    return str(results)


def check_product_availability(product_id: str) -> str:
    """Check stock availability for a specific product by its ID.

    Args:
        product_id: The unique product ID (e.g. 'prod-001', 'prod-002').

    Returns:
        Stock status and details for the given product.
    """
    db = get_firestore_client()
    doc_ref = db.collection("products").document(product_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Product with ID '{product_id}' was not found."

    data = doc.to_dict()
    stock = data.get("stock", 0)
    status = "In Stock" if stock > 0 else "Out of Stock"
    return f"Product '{data.get('name')}' ({product_id}): {status} (Quantity available: {stock})."


def add_to_cart(product_id: str, quantity: int = 1, selected_options: str = "") -> str:
    """Add a selected product to the customer's shopping cart.

    Args:
        product_id: The ID of the product to add (e.g. 'prod-001').
        quantity: The quantity of the item to add (defaults to 1).
        selected_options: Options such as color or size (e.g. 'Color: Blue, Size: Medium').

    Returns:
        Confirmation message for the added cart item.
    """
    db = get_firestore_client()
    doc_ref = db.collection("products").document(product_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Cannot add to cart: Product ID '{product_id}' does not exist."

    prod_data = doc.to_dict()
    cart_item = {
        "product_id": product_id,
        "name": prod_data.get("name"),
        "price": prod_data.get("price"),
        "quantity": quantity,
        "selected_options": selected_options,
        "added_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    cart_ref = db.collection("cart_items").document()
    cart_ref.set(cart_item)

    return f"Successfully added {quantity}x '{prod_data.get('name')}' to your shopping cart!"


def calculate_cart_total(discount_code: str = "", tax_rate: float = 0.08) -> str:
    """Calculate the subtotal, applied discounts, estimated sales tax, and total price for items in the shopping cart.

    Args:
        discount_code: Optional promotional discount code (e.g. 'SAVE10' for 10% off, 'WELCOME20' for 20% off).
        tax_rate: Estimated sales tax rate as a decimal (defaults to 0.08 for 8%).

    Returns:
        An itemized breakdown of items in cart, subtotal, applied discount, estimated tax, and final total price.
    """
    db = get_firestore_client()
    docs = list(db.collection("cart_items").stream())

    if not docs:
        return "Your shopping cart is currently empty."

    items_detail = []
    subtotal = 0.0

    for doc in docs:
        item = doc.to_dict()
        name = item.get("name", "Unknown Item")
        price = float(item.get("price", 0.0))
        qty = int(item.get("quantity", 1))
        item_total = price * qty
        subtotal += item_total
        items_detail.append(f"{qty}x '{name}' @ ${price:.2f} ea = ${item_total:.2f}")

    discount_percent = 0.0
    code_clean = discount_code.strip().upper()
    if code_clean == "SAVE10":
        discount_percent = 0.10
    elif code_clean == "WELCOME20":
        discount_percent = 0.20
    elif code_clean:
        return f"Invalid discount code '{discount_code}'. Valid codes are 'SAVE10' (10% off) or 'WELCOME20' (20% off)."

    discount_amount = subtotal * discount_percent
    taxable_amount = subtotal - discount_amount
    tax_amount = taxable_amount * tax_rate
    final_total = taxable_amount + tax_amount

    summary = [
        "Shopping Cart Summary:",
        *[f"  - {line}" for line in items_detail],
        f"Subtotal: ${subtotal:.2f}",
    ]
    if discount_amount > 0:
        summary.append(f"Discount ({code_clean}, {int(discount_percent*100)}% off): -${discount_amount:.2f}")
    summary.extend([
        f"Estimated Tax ({int(tax_rate*100)}%): ${tax_amount:.2f}",
        f"Total: ${final_total:.2f}"
    ])

    return "\n".join(summary)


def get_weather(query: str) -> str:
    """Simulates a web search for weather information.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        client_kwargs={"vertexai": True, "project": PROJECT_ID, "location": "us-east4"},
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=get_code_executor(),
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        search_products,
        check_product_availability,
        add_to_cart,
        calculate_cart_total,
        convert_currency,
        generate_product_image,
        generate_product_video,
        geocode_address,
        find_nearby_places,
        get_weather,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)


