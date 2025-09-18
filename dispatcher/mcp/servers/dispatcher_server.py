from fastmcp import FastMCP
from ...package_dispatcher import Stack as PackageStack, sort as package_sort

mcp = FastMCP("Dispatcher MCP Server")

@mcp.tool
def sort(width: float, height: float, length: float, mass: float) -> PackageStack:
    """
    Sorts a package based on its dimensions and mass.

    Delegates the sorting logic to the package dispatcher implementation.

    Args:
        width (float): The width of the package.
        height (float): The height of the package.
        length (float): The length of the package.
        mass (float): The mass of the package.

    Returns:
        PackageStack: The sorted package stack.
    """
    # delegate to the package dispatcher implementation
    return package_sort(width, height, length, mass)


if __name__ == "__main__":
    mcp.run()
