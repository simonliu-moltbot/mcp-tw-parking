import requests
import sys

DESC_URL = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json"
AVAIL_URL = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.json"

class ParkingLogic:
    def __init__(self):
        self.cached_desc = None

    def fetch_descriptions(self):
        """Fetch all parking lot descriptions."""
        try:
            print("Fetching parking descriptions...", file=sys.stderr)
            response = requests.get(DESC_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.cached_desc = data.get("data", {}).get("park", [])
            return self.cached_desc
        except Exception as e:
            print(f"Error fetching descriptions: {e}", file=sys.stderr)
            return []

    def fetch_availability(self):
        """Fetch real-time availability."""
        try:
            print("Fetching real-time availability...", file=sys.stderr)
            response = requests.get(AVAIL_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("park", [])
        except Exception as e:
            print(f"Error fetching availability: {e}", file=sys.stderr)
            return []

    def get_parking_by_area(self, area: str):
        """Filter parking lots by area (e.g., 信義區)."""
        if not self.cached_desc:
            self.fetch_descriptions()
        
        results = [p for p in self.cached_desc if area in p.get("area", "")]
        return results

    def search_parking(self, keyword: str):
        """Search parking lots by name or address."""
        if not self.cached_desc:
            self.fetch_descriptions()
        
        results = [p for p in self.cached_desc if keyword in p.get("name", "") or keyword in p.get("address", "")]
        return results

    def get_full_status(self, parking_id: str):
        """Get details and real-time availability for a specific parking lot."""
        if not self.cached_desc:
            self.fetch_descriptions()
        
        desc = next((p for p in self.cached_desc if p.get("id") == parking_id), None)
        if not desc:
            return None
        
        # Get availability
        avail_list = self.fetch_availability()
        avail = next((p for p in avail_list if p.get("id") == parking_id), {})
        
        # Merge
        result = {**desc, **avail}
        return result

    def get_area_availability(self, area: str):
        """Get all parking lots in an area with their real-time availability."""
        area_parks = self.get_parking_by_area(area)
        if not area_parks:
            return []
            
        avail_list = self.fetch_availability()
        avail_map = {p.get("id"): p for p in avail_list}
        
        merged = []
        for p in area_parks:
            pid = p.get("id")
            p_avail = avail_map.get(pid, {})
            merged.append({
                "id": pid,
                "name": p.get("name"),
                "address": p.get("address"),
                "total_car": p.get("totalcar"),
                "available_car": p_avail.get("availablecar", "N/A"),
                "charge_station": p.get("ChargingStation", "0"),
                "pay_info": p.get("payex")
            })
        return merged
