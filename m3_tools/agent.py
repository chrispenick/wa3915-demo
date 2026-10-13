import os
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")

RECIPES = {
    "pasta": {
        "none": {"name": "Classic Spaghetti Bolognese", "ingredients": ["pasta", "ground beef", "tomato sauce", "onion", "garlic"]},
        "vegetarian": {"name": "Pasta Primavera", "ingredients": ["pasta", "zucchini", "bell pepper", "tomato sauce", "garlic"]},
        "vegan": {"name": "Pasta Arrabbiata", "ingredients": ["pasta", "tomato sauce", "garlic", "chili flakes", "olive oil"]},
    },
    "salad": {
        "none": {"name": "Caesar Salad", "ingredients": ["romaine lettuce", "chicken", "parmesan", "croutons", "caesar dressing"]},
        "vegetarian": {"name": "Greek Salad", "ingredients": ["cucumber", "tomato", "feta", "olives", "red onion"]},
        "vegan": {"name": "Quinoa Power Bowl", "ingredients": ["quinoa", "chickpeas", "spinach", "avocado", "lemon juice"]},
    },
}

PANTRY = {
    "pasta": True,
    "tomato sauce": True,
    "garlic": True,
    "zucchini": False,
    "bell pepper": True,
    "olive oil": True,
    "chili flakes": True,
    "ground beef": False,
    "onion": True,
}


def find_recipe(dish: str, dietary: str = "none") -> dict:
    """Find a recipe for a dish matching dietary preferences.

    Args:
        dish: The dish to look up. Supported: pasta, salad.
        dietary: Dietary restriction. One of: none, vegetarian, vegan. Default: none.

    Returns:
        A dict with 'name' and 'ingredients' list, or an error dict.
    """
    dish_key = dish.lower()
    dietary_key = dietary.lower()
    if dish_key not in RECIPES:
        return {"status": "error", "message": f"No recipes found for '{dish}'. Try: pasta, salad."}
    variants = RECIPES[dish_key]
    if dietary_key not in variants:
        dietary_key = "none"
    return {"status": "ok", **variants[dietary_key]}


def check_pantry_item(ingredient: str, tool_context: ToolContext) -> dict:
    """Check if an ingredient is available in the pantry.

    Reads the user's dietary preference from session state.

    Args:
        ingredient: The ingredient name to check.

    Returns:
        A dict with 'ingredient', 'available' (bool), and 'dietary_preference' used.
    """
    dietary = tool_context.state.get("dietary_preference", "none")
    available = PANTRY.get(ingredient.lower(), False)
    return {
        "ingredient": ingredient,
        "available": available,
        "dietary_preference": dietary,
    }


root_agent = LlmAgent(
    name="recipe_assistant",
    model=MODEL,
    instruction=(
        "You are a recipe assistant. Help users plan meals by finding recipes and "
        "checking what ingredients they have on hand. "
        "Always check pantry availability for the key ingredients in a recipe."
    ),
    tools=[find_recipe, check_pantry_item],
)
