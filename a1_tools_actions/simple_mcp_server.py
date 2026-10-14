"""Minimal MCP server with two mock tools for the A1c MCP toolset demo.

Run standalone:  python a1_tools_actions/simple_mcp_server.py
Used by mcp_demo.py as a stdio subprocess via StdioServerParameters.
"""
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("demo-tools")


@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather conditions for a city.

    Args:
        city: City name (London, New York, Tokyo, or Sydney).
    """
    data = {
        "london": "Partly cloudy, 15°C, humidity 72%",
        "new york": "Sunny, 22°C, humidity 45%",
        "tokyo": "Light rain, 18°C, humidity 85%",
        "sydney": "Clear skies, 24°C, humidity 60%",
    }
    return data.get(
        city.lower(),
        f"Weather unavailable for '{city}'. Supported cities: London, New York, Tokyo, Sydney.",
    )


@mcp.tool()
def check_inventory(product: str) -> str:
    """Check warehouse inventory for a product.

    Args:
        product: Product name (laptop, phone, tablet, or headphones).
    """
    stock = {
        "laptop": "142 units in stock, available at 3 warehouses",
        "phone": "89 units in stock, available at 2 warehouses",
        "tablet": "0 units — out of stock, restock expected 2025-02-10",
        "headphones": "305 units in stock, available at 4 warehouses",
    }
    return stock.get(
        product.lower(),
        f"Product '{product}' not found. Supported products: laptop, phone, tablet, headphones.",
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
