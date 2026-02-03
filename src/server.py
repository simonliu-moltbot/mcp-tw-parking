"""
Taipei Parking MCP Server using FastMCP.
Supports both STDIO and Streamable HTTP transport modes.
"""
import sys
import os
import argparse
import asyncio

# Add current directory to path so we can import 'logic'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
import logic

# Initialize FastMCP
mcp = FastMCP("mcp-tw-parking")

@mcp.tool()
async def get_all_parking_lots() -> str:
    """
    獲取台北市所有公有停車場的即時剩餘車位資訊。
    """
    data = await logic.fetch_parking_data()
    return str(data)

@mcp.tool()
async def search_parking_by_name(keyword: str) -> str:
    """
    依據關鍵字搜尋特定的停車場車位。
    Args:
        keyword: 停車場名稱關鍵字，例如「信義」。
    """
    data = await logic.search_parking(keyword)
    return str(data)

def main():
    parser = argparse.ArgumentParser(description="Taipei Parking MCP Server")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio", help="Transport mode")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (only for http mode)")
    args = parser.parse_args()

    if args.mode == "stdio":
        mcp.run()
    else:
        print(f"Starting FastMCP in streamable-http mode on port {args.port}...", file=sys.stderr)
        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=args.port,
            path="/mcp"
        )

if __name__ == "__main__":
    main()
