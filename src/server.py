import sys
import os
import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# Import Hack
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from logic import ParkingLogic
except ImportError as e:
    print(f"Error importing logic: {e}", file=sys.stderr)
    class ParkingLogic:
        def __init__(self): pass
        def get_parking_by_area(self, area): return []
        def search_parking(self, keyword): return []
        def get_full_status(self, parking_id): return None
        def get_area_availability(self, area): return []

server = Server("mcp-tw-parking")
logic = ParkingLogic()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_parking_by_area",
            description="列出特定行政區（如：信義區、大安區）的停車場列表與即時剩餘位數。",
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {"type": "string", "description": "行政區名稱，例如 '信義區'"},
                },
                "required": ["area"],
            },
        ),
        types.Tool(
            name="search_parking",
            description="關鍵字搜尋停車場名稱或地址。",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜尋關鍵字"},
                },
                "required": ["keyword"],
            },
        ),
        types.Tool(
            name="get_parking_details",
            description="獲取特定停車場的詳細資訊，包括收費標準、剩餘位數、充電樁等。",
            inputSchema={
                "type": "object",
                "properties": {
                    "parking_id": {"type": "string", "description": "停車場 ID"},
                },
                "required": ["parking_id"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    if not arguments:
        return [types.TextContent(type="text", text="Error: Missing arguments")]

    try:
        if name == "list_parking_by_area":
            area = arguments.get("area", "")
            results = logic.get_area_availability(area)
            if not results:
                return [types.TextContent(type="text", text=f"找不到 {area} 的停車場資訊。")]
            
            # Format output
            lines = [f"### {area} 停車場即時狀態"]
            for p in results:
                lines.append(f"- **{p['name']}**")
                lines.append(f"  - 剩餘位數: {p['available_car']} / {p['total_car']}")
                lines.append(f"  - 地址: {p['address']}")
                lines.append(f"  - 收費: {p['pay_info']}")
            
            return [types.TextContent(type="text", text="\n".join(lines))]

        elif name == "search_parking":
            keyword = arguments.get("keyword", "")
            results = logic.search_parking(keyword)
            if not results:
                return [types.TextContent(type="text", text=f"找不到關鍵字 '{keyword}' 相關的停車場。")]
            
            lines = [f"### 搜尋結果: {keyword}"]
            for p in results:
                lines.append(f"- {p['name']} (ID: {p['id']}) - {p['address']}")
            
            return [types.TextContent(type="text", text="\n".join(lines))]

        elif name == "get_parking_details":
            pid = arguments.get("parking_id", "")
            p = logic.get_full_status(pid)
            if not p:
                return [types.TextContent(type="text", text=f"找不到 ID 為 {pid} 的停車場詳細資訊。")]
            
            lines = [f"## {p.get('name')} 詳情"]
            lines.append(f"- **區域**: {p.get('area')}")
            lines.append(f"- **地址**: {p.get('address')}")
            lines.append(f"- **電話**: {p.get('tel')}")
            lines.append(f"- **收費**: {p.get('payex')}")
            lines.append(f"- **即時剩餘位數**:")
            lines.append(f"  - 汽車: {p.get('availablecar', 'N/A')} / {p.get('totalcar')}")
            lines.append(f"  - 機車: {p.get('availablemotor', 'N/A')} / {p.get('totalmotor')}")
            lines.append(f"- **設施**: 充電樁 x {p.get('ChargingStation', '0')}, 身障車位 x {p.get('Handicap_First', '0')}")
            
            return [types.TextContent(type="text", text="\n".join(lines))]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        print(f"Error in tool {name}: {e}", file=sys.stderr)
        return [types.TextContent(type="text", text=f"發生錯誤: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-tw-parking",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Server crashed during startup: {e}", file=sys.stderr)
        sys.exit(1)
