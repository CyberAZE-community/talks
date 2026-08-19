from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Simple Server",
    stateless_http=True,
    json_response=True,
)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
