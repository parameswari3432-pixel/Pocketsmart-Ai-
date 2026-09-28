import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize client if API key is present
client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize Google GenAI SDK: {e}")


def _parse_json_or_fallback(text: str, fallback_data: Dict[str, Any]) -> Dict[str, Any]:
    """Cleans up markdown json code blocks and parses JSON, or falls back safely."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except Exception as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return fallback_data


def generate_interior_plan(
    budget: float,
    room_type: str,
    style: str,
    square_feet: float,
    priorities: str = "balanced",
    currency: str = "$"
) -> Dict[str, Any]:
    """Generates an AI-powered interior design budget breakdown and styling advice."""
    prompt = f"""
You are an expert interior designer and budget consultant.
Create a comprehensive, realistic interior decoration and remodeling budget plan.

Details:
- Room Type: {room_type}
- Target Budget: {currency}{budget:,.2f}
- Interior Style Preference: {style}
- Approximate Area: {square_feet} sq ft
- Budget Priority: {priorities}
- Currency: {currency}

Provide your response strictly in the following JSON format without any extra markdown explanation outside the JSON:
{{
    "title": "...",
    "summary": "...",
    "style_analysis": "...",
    "allocations": [
        {{"category": "Furniture & Core Pieces", "percentage": 35, "amount": 0, "description": "..."}},
        {{"category": "Lighting & Electricals", "percentage": 15, "amount": 0, "description": "..."}},
        {{"category": "Wall Treatments & Paint", "percentage": 15, "amount": 0, "description": "..."}},
        {{"category": "Flooring & Rugs", "percentage": 15, "amount": 0, "description": "..."}},
        {{"category": "Decor, Art & Textiles", "percentage": 12, "amount": 0, "description": "..."}},
        {{"category": "Contingency & Installation", "percentage": 8, "amount": 0, "description": "..."}}
    ],
    "itemized_shopping_list": [
        {{"item": "...", "category": "...", "estimated_cost": 0, "priority": "High|Medium|Low", "recommendation": "..."}}
    ],
    "money_saving_tips": [
        "...", "..."
    ],
    "diy_opportunities": [
        "...", "..."
    ],
    "color_palette": [
        {{"name": "...", "hex": "#...", "usage": "..."}}
    ]
}}
Ensure the allocations sum exactly to 100%, and calculate amounts according to the total budget {budget}.
"""

    fallback = {
        "title": f"Custom {style} {room_type} Design Plan",
        "summary": f"A balanced {style} layout optimized for {square_feet} sq ft within a {currency}{budget:,.0f} budget.",
        "style_analysis": f"Emphasizes clean lines, curated textures, and functional elegance typical of {style} interiors.",
        "allocations": [
            {"category": "Furniture & Core Pieces", "percentage": 35, "amount": budget * 0.35, "description": "Primary statement pieces, modular storage, and seating."},
            {"category": "Lighting & Ambience", "percentage": 15, "amount": budget * 0.15, "description": "Layered warm lighting, accent lamps, and smart fixtures."},
            {"category": "Wall Accents & Paint", "percentage": 15, "amount": budget * 0.15, "description": "Low-VOC premium paint and subtle textured feature wall."},
            {"category": "Flooring & Rugs", "percentage": 15, "amount": budget * 0.15, "description": "Plush area rug and durable underlay."},
            {"category": "Decor, Art & Curtains", "percentage": 12, "amount": budget * 0.12, "description": "Curated wall art, throw pillows, and linen drapes."},
            {"category": "Contingency / Installation", "percentage": 8, "amount": budget * 0.08, "description": "Hardware, delivery fees, and assembly buffer."}
        ],
        "itemized_shopping_list": [
            {"item": f"Primary {room_type} Focal Furniture", "category": "Furniture", "estimated_cost": budget * 0.25, "priority": "High", "recommendation": "Invest in neutral durable upholstery or solid wood frames."},
            {"item": "Dimmable Pendant / Ceiling Fixture", "category": "Lighting", "estimated_cost": budget * 0.08, "priority": "Medium", "recommendation": "Warm 2700K-3000K diffused lighting."},
            {"item": "High-pile or Woven Texture Rug", "category": "Flooring", "estimated_cost": budget * 0.10, "priority": "High", "recommendation": "Ensure front furniture legs rest on the rug."},
            {"item": "Custom-look Linen Curtain Panels", "category": "Decor", "estimated_cost": budget * 0.06, "priority": "Medium", "recommendation": "Hang high and wide to visually enlarge space."},
            {"item": "Statement Wall Mirror / Art", "category": "Decor", "estimated_cost": budget * 0.06, "priority": "Low", "recommendation": "Adds depth and reflects natural light."}
        ],
        "money_saving_tips": [
            "Source secondary accent tables and plant stands from discount outlets or thrift shops.",
            "Use peel-and-stick architectural trim or paint color-blocking instead of expensive millwork.",
            "Standardize curtain lengths and hem them with iron-on adhesive tape for a bespoke drape."
        ],
        "diy_opportunities": [
            "Paint existing wooden furniture with chalk paint and update brass hardware.",
            "Create oversized canvas textured wall art using joint compound and neutral paint."
        ],
        "color_palette": [
            {"name": "Warm Linen", "hex": "#F4EFEB", "usage": "Primary Walls & Ceilings"},
            {"name": "Muted Sage / Accent", "hex": "#8A9A86", "usage": "Accent Wall / Textiles"},
            {"name": "Charcoal Slate", "hex": "#2B2D42", "usage": "Hardware & Metal Accents"},
            {"name": "Warm Oak", "hex": "#C49A6C", "usage": "Wood Finishes & Flooring"}
        ]
    }

    if not client:
        return fallback

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return _parse_json_or_fallback(response.text, fallback)
    except Exception as e:
        logger.error(f"Gemini Interior Plan error: {e}")
        return fallback


def generate_party_plan(
    budget: float,
    event_type: str,
    guest_count: int,
    theme: str,
    venue_type: str = "Home / Backyard",
    currency: str = "$"
) -> Dict[str, Any]:
    """Generates an AI-powered party budget planner with per-head estimates and timelines."""
    per_guest = budget / max(guest_count, 1)
    prompt = f"""
You are a premier event planner and party budgeting strategist.
Create a detailed, unforgettable party plan and cost optimization breakdown.

Event Details:
- Type of Event: {event_type}
- Total Budget: {currency}{budget:,.2f}
- Guest Count: {guest_count} attendees (~{currency}{per_guest:,.2f} per guest)
- Theme / Vibe: {theme}
- Venue Type: {venue_type}
- Currency: {currency}

Provide your response strictly in the following JSON format without extra markdown outside the JSON:
{{
    "title": "...",
    "tagline": "...",
    "per_guest_budget": {per_guest:.2f},
    "allocations": [
        {{"category": "Food & Catering", "percentage": 40, "amount": 0, "description": "..."}},
        {{"category": "Beverages & Bar", "percentage": 18, "amount": 0, "description": "..."}},
        {{"category": "Decor & Lighting", "percentage": 15, "amount": 0, "description": "..."}},
        {{"category": "Venue & Rentals", "percentage": 12, "amount": 0, "description": "..."}},
        {{"category": "Entertainment & Music", "percentage": 10, "amount": 0, "description": "..."}},
        {{"category": "Favors & Miscellaneous", "percentage": 5, "amount": 0, "description": "..."}}
    ],
    "menu_and_catering_ideas": [
        {{"course": "...", "item": "...", "cost_tier": "$|$$|$$$", "notes": "..."}}
    ],
    "decor_and_ambience_guide": [
        "...", "..."
    ],
    "entertainment_and_games": [
        "...", "..."
    ],
    "event_day_schedule": [
        {{"time": "T-3 Hours", "activity": "..."}},
        {{"time": "0:00", "activity": "Guests Arrive & Welcome Drinks"}},
        {{"time": "+1:00", "activity": "..."}},
        {{"time": "+2:30", "activity": "..."}},
        {{"time": "+4:00", "activity": "Wrap up & Favors"}}
    ],
    "budget_saving_hacks": [
        "...", "..."
    ]
}}
Ensure the allocations sum strictly to 100%, and calculate amounts according to total budget {budget}.
"""

    fallback = {
        "title": f"Ultimate {theme} {event_type}",
        "tagline": f"An immersive {theme.lower()} celebration curated for {guest_count} guests.",
        "per_guest_budget": round(per_guest, 2),
        "allocations": [
            {"category": "Food & Catering", "percentage": 40, "amount": budget * 0.40, "description": "Signature grazing boards, hot buffet platters, and bite-sized desserts."},
            {"category": "Beverages & Signature Bar", "percentage": 18, "amount": budget * 0.18, "description": "2 signature cocktails/mocktails, wine, punch bowls, and ice/garnishes."},
            {"category": "Decor, Florals & Lighting", "percentage": 15, "amount": budget * 0.15, "description": "Fairy string lights, themed photo backdrop, balloons, and table runners."},
            {"category": "Venue, Furniture & Tableware", "percentage": 12, "amount": budget * 0.12, "description": "Eco-friendly premium disposable dinnerware, extra seating, and ice buckets."},
            {"category": "Entertainment & Sound", "percentage": 10, "amount": budget * 0.10, "description": "Curated playlist system, interactive party games, and instant photo station."},
            {"category": "Favors & Emergency Buffer", "percentage": 5, "amount": budget * 0.05, "description": "Custom souvenir takeaway boxes and last-minute supplies."}
        ],
        "menu_and_catering_ideas": [
            {"course": "Appetizer", "item": "Artisan Charcuterie & Bruschetta Board", "cost_tier": "$$", "notes": "High visual impact, self-serve, cost-efficient in bulk."},
            {"course": "Main", "item": "Gourmet Sliders / Street Taco Bar", "cost_tier": "$$", "notes": "Interactive culinary station with customizable toppings."},
            {"course": "Dessert", "item": "Mini Dessert Cups & Cupcake Tower", "cost_tier": "$", "notes": "Portion controlled and eliminates cake cutting fees."}
        ],
        "decor_and_ambience_guide": [
            f"Build a focal selfie wall matching the '{theme}' palette with reusable balloon arches and neon/wooden signage.",
            "Dim main overhead lighting and use warm amber string lights and battery-operated pillar candles.",
            "Create personalized place cards or drink tags to reduce duplicate cup usage."
        ],
        "entertainment_and_games": [
            "Custom Spotify collaborative playlist where guests add songs ahead of time.",
            "Interactive trivia or group icebreaker games tailored to the honoree/theme."
        ],
        "event_day_schedule": [
            {"time": "T-3 Hours", "activity": "Final venue setup, cooling beverages, and audio test."},
            {"time": "0:00", "activity": "Welcome drinks, signature aperitifs, and background jazz/chill beats."},
            {"time": "+1:00", "activity": "Food stations open and toast / main address."},
            {"time": "+2:30", "activity": "Interactive games, photo sessions, and dessert cutting."},
            {"time": "+4:00", "activity": "Wrap-up, farewells, and distributing party favors."}
        ],
        "budget_saving_hacks": [
            "Batch prepare signature cocktails in beverage dispensers instead of offering a fully stocked open bar.",
            "Rent or borrow audio gear and party lighting from friends rather than booking heavy production."
        ]
    }

    if not client:
        return fallback

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return _parse_json_or_fallback(response.text, fallback)
    except Exception as e:
        logger.error(f"Gemini Party Plan error: {e}")
        return fallback


def generate_jewelry_plan(
    budget: float,
    occasion: str,
    style_preference: str,
    metals: str,
    outfit_image_bytes: Optional[bytes] = None,
    outfit_image_mime: Optional[str] = None,
    currency: str = "$"
) -> Dict[str, Any]:
    """Generates an AI jewelry styling and budget plan with optional outfit vision matching."""
    image_prompt_part = ""
    if outfit_image_bytes:
        image_prompt_part = "Analyze the provided outfit image (colors, neckline, embroidery/patterns, silhouette) and tailor every jewelry piece to harmonize flawlessly with this specific outfit."

    prompt = f"""
You are a luxury jewelry stylist, gemologist, and smart jewelry investment advisor.
Create a personalized jewelry purchasing & styling guide.

Client Profile:
- Total Budget: {currency}{budget:,.2f}
- Occasion: {occasion}
- Style Aesthetic: {style_preference}
- Preferred Metals / Gems: {metals}
- Currency: {currency}
{image_prompt_part}

Provide your response strictly in the following JSON format without extra markdown outside the JSON:
{{
    "title": "...",
    "styling_verdict": "...",
    "outfit_match_analysis": "...",
    "allocations": [
        {{"category": "Necklace / Statement Piece", "percentage": 45, "amount": 0, "description": "..."}},
        {{"category": "Earrings", "percentage": 25, "amount": 0, "description": "..."}},
        {{"category": "Rings & Bands", "percentage": 18, "amount": 0, "description": "..."}},
        {{"category": "Bracelets / Bangles", "percentage": 12, "amount": 0, "description": "..."}}
    ],
    "recommended_pieces": [
        {{
            "piece_type": "...",
            "material_options": "...",
            "estimated_price": 0,
            "style_pairing_reason": "...",
            "investment_value": "High|Medium|Costume/Fashion"
        }}
    ],
    "metal_and_gemstone_guide": [
        {{"element": "...", "recommendation": "...", "maintenance_tip": "..."}}
    ],
    "smart_buying_advice": [
        "...", "..."
    ],
    "styling_dos_and_donts": {{
        "dos": ["...", "..."],
        "donts": ["...", "..."]
    }}
}}
Ensure allocations sum to 100%, and calculate amounts according to total budget {budget}.
"""

    fallback = {
        "title": f"Bespoke {occasion} Jewelry Styling Portfolio",
        "styling_verdict": f"A curated ensemble marrying {style_preference.lower()} aesthetics with versatile {metals} tones for {occasion}.",
        "outfit_match_analysis": "Selected metals and silhouettes balance your outfit's neckline and visual density without overpowering the garment." if outfit_image_bytes else "Designed for versatile necklines and flattering proportions across event lighting.",
        "allocations": [
            {"category": "Necklace / Central Piece", "percentage": 45, "amount": budget * 0.45, "description": "Focal heirloom or contemporary pendant/choker."},
            {"category": "Earrings / Studs / Drops", "percentage": 25, "amount": budget * 0.25, "description": "Framing earrings complementary to hairstyle and collar."},
            {"category": "Rings & Bands", "percentage": 18, "amount": budget * 0.18, "description": "Stackable accent rings or solitary statement cocktail ring."},
            {"category": "Bracelet / Wristwear", "percentage": 12, "amount": budget * 0.12, "description": "Delicate tennis chain, cuff, or bangle set."}
        ],
        "recommended_pieces": [
            {
                "piece_type": f"Signature {occasion} Focal Necklace",
                "material_options": f"14k/18k Solid Gold, Platinum, or Sterling Silver with Moissanite / Lab-grown Sapphires",
                "estimated_price": budget * 0.45,
                "style_pairing_reason": "Balances the neckline while maintaining refined proportion.",
                "investment_value": "High"
            },
            {
                "piece_type": "Chandelier / Geometric Drop Earrings",
                "material_options": f"Matching {metals} with micro-pave accents",
                "estimated_price": budget * 0.25,
                "style_pairing_reason": "Draws light to the jawline and coordinates seamlessly with hair updos.",
                "investment_value": "Medium"
            },
            {
                "piece_type": "Textured Band or Solitaire Ring",
                "material_options": "Bezel set gemstone with comfort fit shank",
                "estimated_price": budget * 0.18,
                "style_pairing_reason": "Subtle luxury for gestures, toasts, and photography.",
                "investment_value": "Medium"
            }
        ],
        "metal_and_gemstone_guide": [
            {"element": metals, "recommendation": "Look for hallmarked 14k/18k or vermeil with e-coating for durability.", "maintenance_tip": "Clean gently with warm water, mild dish soap, and a microfiber cloth."},
            {"element": "Gemstones / Diamonds", "recommendation": "Consider lab-grown stones or Moissanite to maximize clarity and carat size within budget.", "maintenance_tip": "Avoid spraying perfumes or hairsprays directly onto stones."}
        ],
        "smart_buying_advice": [
            "Opt for lab-grown gemstones or 14k gold rather than 24k to gain 40% cost savings with higher scratch resistance.",
            "Prioritize cut quality over color grade for stones to maximize fire and brilliance under photography flash.",
            "Ask jewellers for certified appraisals and insurance documentation upon purchase."
        ],
        "styling_dos_and_donts": {
            "dos": [
                "Pick ONE hero piece (either statement necklace OR statement earrings) to prevent visual clutter.",
                "Match metal undertones to your skin tone and outfit embellishments (gold for warm, silver/platinum for cool)."
            ],
            "donts": [
                "Don't wear heavy necklaces with high embellished collars or turtle-neck outfits.",
                "Don't compromise on earring weight if you'll be wearing them for 5+ hours."
            ]
        }
    }

    if not client:
        return fallback

    try:
        from google.genai import types
        contents = [prompt]
        if outfit_image_bytes and outfit_image_mime:
            contents.append(
                types.Part.from_bytes(
                    data=outfit_image_bytes,
                    mime_type=outfit_image_mime,
                )
            )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )
        return _parse_json_or_fallback(response.text, fallback)
    except Exception as e:
        logger.error(f"Gemini Jewelry Plan error: {e}")
        return fallback
