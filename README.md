# Taiwan Taipei Parking Helper MCP Server (mcp-tw-parking)

一個提供台北市停車場即時資訊的 MCP Server。支援查詢特定行政區的停車場位數、關鍵字搜尋以及詳細收費資訊。

## 🇹🇼 功能
- **區域查詢**: 列出如「信義區」、「大安區」等區域的所有停車場與即時剩餘位數。
- **關鍵字搜尋**: 透過名稱或地址搜尋停車場。
- **詳細資訊**: 獲取停車場的 ID、地址、電話、收費標準、剩餘汽車/機車位數、充電樁數量等。

## 🛠 安裝與設定

### 1. 建立虛擬環境與安裝依賴
```bash
cd projects/mcp-tw-parking
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 設定 Claude Desktop
在 `claude_desktop_config.json` 中加入：
```json
{
  "mcpServers": {
    "tw-parking": {
      "command": "/Users/simonliuyuwei/clawd/projects/mcp-tw-parking/.venv/bin/python3.13",
      "args": [
        "/Users/simonliuyuwei/clawd/projects/mcp-tw-parking/src/server.py"
      ]
    }
  }
}
```

### 3. 設定 Dive
- **Type**: `stdio`
- **Command**: `/Users/simonliuyuwei/clawd/projects/mcp-tw-parking/.venv/bin/python3.13`
- **Args**: `/Users/simonliuyuwei/clawd/projects/mcp-tw-parking/src/server.py`

## 📊 提供的工具

### `list_parking_by_area(area)`
列出行政區停車場狀態。
- `area`: 行政區名稱 (如: '信義區')。

### `search_parking(keyword)`
關鍵字搜尋停車場。
- `keyword`: 名稱或地址。

### `get_parking_details(parking_id)`
獲取詳細資訊。
- `parking_id`: 停車場 ID。

## 📅 資料來源
- [臺北市政府資料開放平台 - 停車場即時資訊](https://data.taipei/)
